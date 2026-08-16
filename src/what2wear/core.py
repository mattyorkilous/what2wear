"""The functional core: one pure entry point, no I/O of any kind.

Rotation picks the Shirt; Resolution decides everything else about
the day -- so far the sweater and the shoes that follow from its
pants. Layers and the weather that calls for them arrive later.
"""

from datetime import date, timedelta

from what2wear.model import (
    Closet,
    DayType,
    Outfit,
    PantsRow,
    Response,
    Shirt,
    Show,
    State,
)


def handle(command: Show, state: State, today: date) -> Response:
    """Answer a question about a date.

    The one seam every command routes through.
    """
    on = today if command.on is None else command.on
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


def _office_days_of_week(state: State, on: date) -> tuple[date, ...]:
    """The Office Days of the Monday-start Week containing `on`, in
    date order."""
    monday = on - timedelta(days=on.weekday())
    week = (monday + timedelta(days=offset) for offset in range(7))
    return tuple(
        day for day in week if state.day_type(day) is DayType.OFFICE
    )


def _resolve_office_day(
    state: State, resolved: tuple[Response, ...], on: date
) -> tuple[Response, ...]:
    """The Week resolved so far, plus this Office Day settled against
    the sweaters it has already spent.

    Shoes follow the sweater rather than the pants, so a Fallback
    brings the donor row's shoes along with it and shoes inherit the
    no-repeat guarantee instead of being checked for it.
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
    """The row's own sweater, its Fallback once that is taken, and the
    row's own again when both are.

    That last case means the Week has more Office Days than it has
    sweaters left to offer, and is the only way a sweater repeats.
    """
    if row.sweater not in taken:
        return row.sweater
    if row.fallback is not None and row.fallback not in taken:
        return row.fallback
    return row.sweater


def _shirt(state: State, day_type: DayType, on: date) -> Shirt:
    """What Rotation offers on a date, before Resolution touches it."""
    closet = state.closet_for(day_type)
    return closet.shirts[_position(state, closet, day_type, on)]


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
        state.day_type(tail + timedelta(days=offset)) is day_type
        for offset in range(remaining_days)
    )
