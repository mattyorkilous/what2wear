"""The functional core: one pure entry point, no I/O of any kind.

Rotation picks the Shirt; Resolution decides everything else about
the day -- so far the sweater and the shoes that follow from its
pants. Outerwear and the weather that calls for them arrive later.
"""

from dataclasses import replace
from datetime import date, timedelta

from what2wear.model import (
    Closet,
    DayType,
    DayTypeOverride,
    Decision,
    Outfit,
    PantsRow,
    Reset,
    ResetRequest,
    Response,
    Rotation,
    Shirt,
    State,
)


def handle(
    on: date | None,
    state: State,
    today: date,
    record: DayType | ResetRequest | None = None,
) -> Response:
    """Answer a question about a date, defaulting to today.

    The one seam every command routes through. `record` asks for that
    date to become an Office Day or a Home Day, or for its Rotation to
    move: the answer is resolved as though the decision were already
    in force, and comes back with it for the shell to append.
    """
    day = today if on is None else on
    if record is None:
        return _response(state, day)
    decision = _decision(state, day, record)
    return replace(
        _response(_recorded(state, decision), day), decision=decision
    )


def _response(state: State, on: date) -> Response:
    return (
        _office_response(state, on)
        if state.day_type(on) is DayType.OFFICE
        else _home_response(state, on)
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
    sweater = _office_sweater(state.office.row_for(shirt.pants), taken)
    return (
        *resolved,
        Response(
            on=on,
            day_type=DayType.OFFICE,
            outfit=Outfit(
                shirt=shirt.name,
                pants=shirt.pants,
                sweater=sweater,
                shoes=state.office.row_wearing(sweater).shoes,
            ),
            unavoidable_repeat=sweater in taken,
        ),
    )


def _office_sweater(row: PantsRow, taken: frozenset[str]) -> str:
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
    row = state.home.row_for(shirt.pants)
    return Response(
        on=on,
        day_type=DayType.HOME,
        outfit=Outfit(
            shirt=shirt.name,
            pants=shirt.pants,
            sweater=row.sweater,
            shoes=row.shoes,
        ),
    )


def _shirt(state: State, day_type: DayType, on: date) -> Shirt:
    """Take what Rotation offers on a date, before Resolution."""
    closet = state.closet(day_type)
    return closet.shirts[_position(state, closet, day_type, on)]


def _position(
    state: State, closet: Closet, day_type: DayType, on: date
) -> int:
    """Derive where the Rotation stands on a date.

    From the calendar and the Resets recorded against it, never from
    a stored cursor, per ADR-0001.
    """
    steps = _days_of_type_between(
        state, day_type, closet.anchor_date, on
    )
    return (
        closet.index_of(closet.anchor_shirt)
        + steps
        + state.shirt_shift(day_type, on)
    ) % len(closet.shirts)


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
    office_per_week = len(state.office_weekdays)
    per_week = (
        office_per_week
        if day_type is DayType.OFFICE
        else 7 - office_per_week
    )
    tail = start + timedelta(days=whole_weeks * 7)
    return (
        whole_weeks * per_week
        + sum(
            state.pattern_day_type(tail + timedelta(days=offset))
            is day_type
            for offset in range(remaining_days)
        )
        + state.overridden_days(day_type, start, end)
    )


def _decision(
    state: State, on: date, record: DayType | ResetRequest
) -> Decision:
    """Settle what a command asked for into what gets written down."""
    return (
        DayTypeOverride(on, day_type=record)
        if isinstance(record, DayType)
        else Reset(on, Rotation.SHIRT, _offset(state, on, record.shirt))
    )


def _offset(state: State, on: date, shirt: str | None) -> int:
    """Say how far the Shirt Rotation is being asked to move.

    One Shirt on for a bare Reset; the distance round to a named one
    otherwise, always forwards, in the Closet the date draws from. A
    Shirt that Closet does not hold is an error rather than a guess:
    the same name can sit in the other Closet, or in neither.
    """
    if shirt is None:
        return 1
    day_type = state.day_type(on)
    closet = state.closet(day_type)
    return (
        _index_of(closet, day_type, shirt)
        - _position(state, closet, day_type, on)
    ) % len(closet.shirts)


def _index_of(closet: Closet, day_type: DayType, shirt: str) -> int:
    try:
        return closet.index_of(shirt)
    except StopIteration:
        message = f"no {day_type} shirt named {shirt!r}"
        raise UnknownShirtError(message) from None


def _recorded(state: State, decision: Decision) -> State:
    """Put a decision into the State as though it were logged."""
    return (
        replace(state, overrides=(*state.overrides, decision))
        if isinstance(decision, DayTypeOverride)
        else replace(state, resets=(*state.resets, decision))
    )


class UnknownShirtError(Exception):
    """A Reset named a Shirt the day's Closet does not hold."""
