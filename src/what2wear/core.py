"""The functional core: one pure entry point, no I/O of any kind.

Rotation picks the Shirt; Resolution decides everything else about
the day. Only Rotation exists so far -- Resolution arrives with
sweaters and shoes.
"""

from datetime import date, timedelta

from what2wear.model import (
    Closet,
    DayType,
    Outfit,
    Response,
    Show,
    State,
)


def handle(command: Show, state: State, today: date) -> Response:
    """Answer a question about a date.

    The one seam every command routes through.
    """
    on = today if command.on is None else command.on
    day_type = _day_type(state, on)
    closet = state.closet_for(day_type)
    shirt = closet.shirts[_position(state, closet, day_type, on)]
    return Response(
        on=on,
        day_type=day_type,
        outfit=Outfit(shirt=shirt.name, pants=shirt.pants),
    )


def _position(
    state: State, closet: Closet, day_type: DayType, on: date
) -> int:
    """Where the Rotation stands on a date -- derived from the
    calendar, per ADR-0001."""
    steps = _days_of_type_between(
        state, day_type, closet.anchor_date, on
    )
    return (closet.index_of(closet.anchor_shirt) + steps) % len(
        closet.shirts
    )


def _days_of_type_between(
    state: State, day_type: DayType, start: date, end: date
) -> int:
    """Count days of `day_type` in [start, end), negative when `end`
    precedes `start`.

    Whole weeks are counted arithmetically so that a date years out
    costs the same as tomorrow.
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
    return whole_weeks * per_week + sum(
        _day_type(state, tail + timedelta(days=offset)) is day_type
        for offset in range(remaining_days)
    )


def _day_type(state: State, on: date) -> DayType:
    """Office Days follow the weekday pattern; every other date is a
    Home Day."""
    return (
        DayType.OFFICE
        if on.weekday() in state.office_weekdays
        else DayType.HOME
    )
