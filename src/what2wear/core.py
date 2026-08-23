"""The functional core: two pure seams, no I/O of any kind.

`answer` never changes anything and `apply` never renders anything, so
a shell that wants both composes them. Rotation picks the Shirt;
Resolution decides everything else about the day -- the sweater and the
shoes that follow from its pants.
"""

from datetime import date, timedelta

from what2wear import wardrobe
from what2wear.model import (
    Command,
    DayType,
    DayTypeOverride,
    Outfit,
    ResetRequest,
    Response,
    State,
    closet_for,
    pattern_day_type,
)


def answer(state: State, on: date) -> Response:
    """Resolve what a date calls for, and change nothing.

    Every Position is counted from an Anchor the State holds, so this
    needs no clock: today and a date years out are the same call.
    """
    return (
        _office_response(state, on)
        if state.day_type(on) is DayType.OFFICE
        else _home_response(state, on)
    )


def apply(state: State, command: Command, on: date) -> State:
    """Put what a command asks for into the State, and render nothing.

    State in, State out, so what a command actually changed is a single
    value comparison. Both kinds of command are about one date, which
    defaults to today but is the wearer's to name.
    """
    return (
        state.overriding(command)
        if isinstance(command, DayTypeOverride)
        else _reset(state, command, on)
    )


def _office_response(state: State, on: date) -> Response:
    """Resolve an Office Day by walking its whole Week.

    Which sweater a Shirt gets depends on what the Week has already
    taken, so the Week is walked from Monday and this date's answer
    read off the end.
    """
    resolved: tuple[Response, ...] = ()
    for day in _office_days_of_week(state, on):
        resolved = _resolve_office_day(state, resolved, day)
    return next(response for response in resolved if response.on == on)


def _office_days_of_week(state: State, on: date) -> tuple[date, ...]:
    """List the Office Days of the Week containing `on`.

    Monday-start, and in date order.
    """
    monday = on - timedelta(days=on.weekday())
    week = (monday + timedelta(days=offset) for offset in range(7))
    return tuple(
        day for day in week if state.day_type(day) is DayType.OFFICE
    )


def _resolve_office_day(
    state: State, resolved: tuple[Response, ...], on: date
) -> tuple[Response, ...]:
    """Settle one Office Day against the sweaters the Week has spent.

    Returns the Week resolved so far plus this day. Shoes follow the
    sweater rather than the pants, so a Fallback brings the donor
    row's shoes along with it and shoes inherit the no-repeat
    guarantee instead of being checked for it.
    """
    shirt = _shirt(state, DayType.OFFICE, on)
    taken = frozenset(response.outfit.sweater for response in resolved)
    sweater = _office_sweater(
        wardrobe.DEFAULT_OFFICE.row_for(shirt.pants), taken
    )
    return (
        *resolved,
        Response(
            on=on,
            day_type=DayType.OFFICE,
            outfit=Outfit(
                shirt=shirt.label,
                pants=shirt.pants,
                sweater=sweater,
                shoes=wardrobe.DEFAULT_OFFICE.row_wearing(
                    sweater
                ).shoes,
            ),
            unavoidable_repeat=sweater in taken,
        ),
    )


def _office_sweater(
    row: wardrobe.PantsRow, taken: frozenset[str]
) -> str:
    """Choose a sweater the Week has not already taken.

    The row's own, its Fallback once that is taken, and the row's own
    again when both are. That last case means the Week has more
    Office Days than it has sweaters left to offer, and is the only
    way a sweater repeats.
    """
    if row.sweater not in taken:
        return row.sweater
    if row.fallback is not None and row.fallback not in taken:
        return row.fallback
    return row.sweater


def _home_response(state: State, on: date) -> Response:
    """Home has no no-repeat rule, so the pants say everything."""
    shirt = _shirt(state, DayType.HOME, on)
    row = wardrobe.DEFAULT_HOME.row_for(shirt.pants)
    return Response(
        on=on,
        day_type=DayType.HOME,
        outfit=Outfit(
            shirt=shirt.label,
            pants=shirt.pants,
            sweater=row.sweater,
            shoes=row.shoes,
        ),
    )


def _shirt(state: State, day_type: DayType, on: date) -> wardrobe.Shirt:
    """Take what Rotation offers on a date, before Resolution."""
    closet = closet_for(day_type)
    return closet.shirts[_position(state, closet, day_type, on)]


def _position(
    state: State, closet: wardrobe.Closet, day_type: DayType, on: date
) -> int:
    """Derive where the Rotation stands on a date.

    From its Anchor and the calendar, and nothing else -- a Reset moved
    the Anchor, so there is no offset term to add back in.
    """
    anchor = state.anchor(day_type)
    steps = _days_of_type_between(state, day_type, anchor.on, on)
    return (anchor.position + steps) % len(closet.shirts)


def _days_of_type_between(
    state: State, day_type: DayType, start: date, end: date
) -> int:
    """Count days of `day_type` in [start, end).

    Negative when `end` precedes `start`. Whole weeks are counted
    arithmetically so that a date years out costs the same as
    tomorrow, which is why the weekly pattern is counted first and the
    Overrides corrected for afterwards.
    """
    if end < start:
        return -_days_of_type_between(state, day_type, end, start)
    whole_weeks, remaining_days = divmod((end - start).days, 7)
    office_per_week = len(wardrobe.DEFAULT_OFFICE_WEEKDAYS)
    per_week = (
        office_per_week
        if day_type is DayType.OFFICE
        else 7 - office_per_week
    )
    tail = start + timedelta(days=whole_weeks * 7)
    return (
        whole_weeks * per_week
        + sum(
            pattern_day_type(tail + timedelta(days=offset)) is day_type
            for offset in range(remaining_days)
        )
        + state.overridden_days(day_type, start, end)
    )


def _reset(state: State, request: ResetRequest, on: date) -> State:
    """Move a Shirt Rotation, by moving its Anchor to a date.

    The whole Rotation comes with it, so every other date follows
    rather than snapping back -- which is why a Reset dated ahead of
    today moves today as well. Which Rotation moves is the one the
    date draws from, never the Label; the other is left where it
    stood.
    """
    day_type = state.day_type(on)
    closet = closet_for(day_type)
    position = _reset_position(state, request, closet, day_type, on)
    return state.moved(day_type, wardrobe.Anchor(on, position))


def _reset_position(
    state: State,
    request: ResetRequest,
    closet: wardrobe.Closet,
    day_type: DayType,
    on: date,
) -> int:
    """Say which Position the date is being moved to.

    One Shirt on for a bare Reset; straight to a named one otherwise,
    in the Closet the date draws from. A Shirt that Closet does not
    hold is an error rather than a guess: the same Label can sit in
    the other Closet, or in neither.
    """
    if request.shirt is None:
        return (_position(state, closet, day_type, on) + 1) % len(
            closet.shirts
        )
    return _index_of(closet, day_type, request.shirt)


def _index_of(
    closet: wardrobe.Closet, day_type: DayType, shirt: str
) -> int:
    try:
        return closet.index_of(shirt)
    except StopIteration:
        message = f"no {day_type} shirt named {shirt!r}"
        raise UnknownShirtError(message) from None


class UnknownShirtError(Exception):
    """A Reset named a Shirt the day's Closet does not hold."""
