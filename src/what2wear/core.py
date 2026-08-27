"""The functional core: two pure seams, no I/O of any kind.

`answer` never changes anything and `apply` never renders anything, so
a shell that wants both composes them. Rotation picks the Shirt;
Resolution decides everything else about the day -- the sweater and the
shoes that follow from its pants.

Every rule lives here. `model.py` holds the types and `wardrobe.py` the
starting values, and neither of them decides anything, so this is the
only file to read to learn what the tool does.
"""

from collections.abc import Callable, Mapping
from dataclasses import replace
from datetime import date, timedelta
from operator import attrgetter
from types import MappingProxyType

from what2wear import wardrobe
from what2wear.errors import UnknownShirtError
from what2wear.model import (
    Anchor,
    Closet,
    Command,
    DayType,
    DayTypeOverride,
    Outfit,
    PantsRow,
    ResetRequest,
    Response,
    Shirt,
    State,
)

_CLOSETS: Mapping[DayType, Closet] = MappingProxyType(
    {
        DayType.OFFICE: wardrobe.DEFAULT_OFFICE,
        DayType.HOME: wardrobe.DEFAULT_HOME,
    }
)

_ANCHOR_FIELDS: Mapping[DayType, str] = MappingProxyType(
    {
        DayType.OFFICE: "office_anchor",
        DayType.HOME: "home_anchor",
    }
)


def apply(state: State, command: Command | None, on: date) -> State:
    """Put what a command asks for into the State, and render nothing.

    State in, State out, so what a command actually changed is a single
    value comparison. No command changes nothing, so a shell with
    nothing to record makes the same call as one that has something.
    Both kinds of command are about one date, which defaults to today
    but is the wearer's to name.
    """
    if command is None:
        return state
    return (
        _record_override(state, command)
        if isinstance(command, DayTypeOverride)
        else _reset(state, command, on)
    )


def answer(state: State, on: date) -> Response:
    """Resolve what a date calls for, and change nothing.

    Every Position is counted from an Anchor the State holds, so this
    needs no clock: today and a date years out are the same call.
    """
    return (
        _get_office_response(state, on)
        if _get_day_type(state, on) is DayType.OFFICE
        else _get_home_response(state, on)
    )


def _record_override(state: State, command: DayTypeOverride) -> State:
    """Give back the State with one more date said to be a kind.

    Only a date the weekly pattern does not already make that kind
    is worth a record, so saying what the pattern says leaves no
    record behind -- whether it is taking back an earlier Override or
    agreeing with the pattern to begin with. One record per date, so
    saying the opposite never stacks, and no record ever agrees with
    the pattern it was there to override.
    """
    recorded = {**state.overrides, command.on: command.day_type}
    return replace(
        state,
        overrides=MappingProxyType(
            {
                on: day_type
                for on, day_type in recorded.items()
                if day_type is not _get_pattern_day_type(on)
            }
        ),
    )


def _reset(state: State, request: ResetRequest, on: date) -> State:
    """Move a Shirt Rotation, by moving its Anchor to a date.

    The whole Rotation comes with it, so every other date follows
    rather than snapping back -- which is why a Reset dated ahead of
    today moves today as well. Which Rotation moves is the one the
    date draws from, never the Label; the other is left where it
    stood.
    """
    day_type = _get_day_type(state, on)
    position = _get_reset_position(state, request, day_type, on)
    return _move_anchor(state, day_type, Anchor(on, position))


def _get_day_type(state: State, on: date) -> DayType:
    """Say what kind of day a date actually is.

    A Day Type Override wins over the weekly pattern -- though a
    record that agrees with the pattern, which only an older version
    wrote, says the same thing the pattern already said.
    """
    return state.overrides.get(on, _get_pattern_day_type(on))


def _get_pattern_day_type(on: date) -> DayType:
    """Say what the given weekly pattern alone makes a date.

    Before any Override. Office Days follow the given weekdays; every
    other date, weekends included, is a Home Day.
    """
    return (
        DayType.OFFICE
        if on.weekday() in wardrobe.DEFAULT_OFFICE_WEEKDAYS
        else DayType.HOME
    )


def _get_reset_position(
    state: State, request: ResetRequest, day_type: DayType, on: date
) -> int:
    """Say which Position the date is being moved to.

    One Shirt on for a bare Reset; straight to a named one otherwise,
    in the Closet the date draws from. A Shirt that Closet does not
    hold is an error rather than a guess: the same Label can sit in
    the other Closet, or in neither.
    """
    if request.shirt is None:
        return (_get_position(state, day_type, on) + 1) % len(
            _CLOSETS[day_type].shirts
        )
    return _get_shirt_position(day_type, request.shirt)


def _get_position(state: State, day_type: DayType, on: date) -> int:
    """Derive where the Rotation stands on a date.

    From its Anchor and the calendar, and nothing else -- a Reset moved
    the Anchor, so there is no offset term to add back in.
    """
    anchor = _get_anchor(state, day_type)
    steps = _count_days_of_type_between(state, day_type, anchor.on, on)
    return (anchor.position + steps) % len(_CLOSETS[day_type].shirts)


def _get_shirt_position(day_type: DayType, label: str) -> int:
    """Give the Position a Shirt with this Label sits at.

    In the Closet the day draws from, so the same Label in the other
    Closet is not an answer to this question.
    """
    try:
        return next(
            position
            for position, shirt in enumerate(_CLOSETS[day_type].shirts)
            if shirt.label == label
        )
    except StopIteration:
        message = f"no {day_type} shirt named {label!r}"
        raise UnknownShirtError(message) from None


def _move_anchor(
    state: State, day_type: DayType, anchor: Anchor
) -> State:
    """Give back the State with one Shirt Anchor somewhere else.

    The other Rotation stays exactly where it stood, which is what
    lets a Reset be about the Closet the day drew from and nothing
    else.
    """
    return replace(state, **{_ANCHOR_FIELDS[day_type]: anchor})


def _get_office_response(state: State, on: date) -> Response:
    """Resolve an Office Day by walking its whole Week.

    Which sweater a Shirt gets depends on what the Week has already
    taken, so the Week is walked from Monday and this date's answer
    read off the end.
    """
    resolved: tuple[Response, ...] = ()
    for day in _get_office_days_of_week(state, on):
        resolved = _resolve_office_day(state, resolved, day)
    return next(response for response in resolved if response.on == on)


def _get_office_days_of_week(
    state: State, on: date
) -> tuple[date, ...]:
    """List the Office Days of the Week containing `on`.

    Monday-start, and in date order.
    """
    monday = on - timedelta(days=on.weekday())
    week = (monday + timedelta(days=offset) for offset in range(7))
    return tuple(
        day
        for day in week
        if _get_day_type(state, day) is DayType.OFFICE
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
    shirt = _get_shirt(state, DayType.OFFICE, on)
    taken = frozenset(response.outfit.sweater for response in resolved)
    sweater = _choose_office_sweater(
        _get_row_for_pants(wardrobe.DEFAULT_OFFICE, shirt.pants), taken
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
                shoes=_get_row_for_sweater(
                    wardrobe.DEFAULT_OFFICE, sweater
                ).shoes,
            ),
            unavoidable_repeat=sweater in taken,
        ),
    )


def _get_shirt(state: State, day_type: DayType, on: date) -> Shirt:
    """Take what Rotation offers on a date, before Resolution."""
    return _CLOSETS[day_type].shirts[_get_position(state, day_type, on)]


def _get_row_for_pants(closet: Closet, pants: str) -> PantsRow:
    """Give the row that dresses a pair of Pants."""
    return _get_row(closet, attrgetter("pants"), pants)


def _get_row(
    closet: Closet,
    get_label: Callable[[PantsRow], str | None],
    label: str,
) -> PantsRow:
    """Give the one row a Garment's Label picks out.

    Which Label is read is the caller's to say, because a row is
    reached by its Pants during Resolution and by its sweater when a
    Fallback is traced back.
    """
    return next(row for row in closet.rows if get_label(row) == label)


def _choose_office_sweater(row: PantsRow, taken: frozenset[str]) -> str:
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


def _get_row_for_sweater(closet: Closet, sweater: str) -> PantsRow:
    """Trace a sweater back to the row it belongs to.

    Office sweaters are one-to-one with office rows, so a Fallback
    can be traced back to the row whose shoes it borrows.
    """
    return _get_row(closet, attrgetter("sweater"), sweater)


def _get_home_response(state: State, on: date) -> Response:
    """Home has no no-repeat rule, so the pants say everything."""
    shirt = _get_shirt(state, DayType.HOME, on)
    row = _get_row_for_pants(wardrobe.DEFAULT_HOME, shirt.pants)
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


def _get_anchor(state: State, day_type: DayType) -> Anchor:
    """Give the Anchor a kind of day's Shirts are counted from."""
    anchor: Anchor = getattr(state, _ANCHOR_FIELDS[day_type])
    return anchor


def _count_days_of_type_between(
    state: State, day_type: DayType, start: date, end: date
) -> int:
    """Count days of `day_type` in [start, end).

    Negative when `end` precedes `start`. Whole weeks are counted
    arithmetically so that a date years out costs the same as
    tomorrow, which is why the weekly pattern is counted first and the
    Overrides corrected for afterwards.
    """
    if end < start:
        return -_count_days_of_type_between(state, day_type, end, start)
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
            _get_pattern_day_type(tail + timedelta(days=offset))
            is day_type
            for offset in range(remaining_days)
        )
        + _count_overridden_days(state, day_type, start, end)
    )


def _count_overridden_days(
    state: State, day_type: DayType, start: date, end: date
) -> int:
    """Count what the Overrides in [start, end) add or take away.

    Days of `day_type`, against the weekly pattern. This is what
    parks a Rotation: a day overridden away from its
    own kind stops counting, so the Shirt it would have worn falls
    to the next day of that kind instead of being lost.
    """
    return sum(
        (_get_day_type(state, on) is day_type)
        - (_get_pattern_day_type(on) is day_type)
        for on in state.overrides
        if start <= on < end
    )
