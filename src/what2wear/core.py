"""Recording what the wearer tells the tool, and answering from it."""

import math
from collections.abc import Collection, Mapping
from dataclasses import replace
from datetime import date, timedelta
from functools import cache
from types import MappingProxyType

import holidays

from what2wear.errors import What2wearError
from what2wear.model import (
    Anchor,
    Closet,
    DayType,
    Garment,
    Outfit,
    PantsRow,
    Response,
    Rotation,
    Shirt,
    State,
)
from what2wear.wardrobe import (
    CLOSETS,
    COLORS,
    DEFAULT_OFFICE_WEEKDAYS,
    HOME_OUTERWEAR,
    KEYS,
)

HORIZON_DAYS = 365  # A year, beyond which a search gives up.


def record_override(state: State, on: date, day_type: DayType) -> State:
    """Record `on` as a `day_type` day.

    Args:
        state: The state to record into.
        on: The date to record.
        day_type: The kind of day to record it as.

    Returns:
        The state with the override recorded, less any override the
        weekday pattern and the holidays already give.
    """
    recorded_overrides = {**state.overrides, on: day_type}
    return replace(
        state,
        overrides=MappingProxyType(
            {
                on: day_type
                for on, day_type in recorded_overrides.items()
                if day_type is not _get_default_day_type(state, on)
            }
        ),
    )


def reset(state: State, shirt: str, on: date) -> State:
    """Move `on`'s rotation to a named shirt.

    Args:
        state: The state to move the anchor in.
        shirt: The label of the shirt to move to.
        on: The date the rotation is moved at.

    Returns:
        The state with the day type's anchor moved.

    Raises:
        What2wearError: If the closet has no shirt so labeled.
    """
    day_type = _get_day_type(state, on)
    position = _get_shirt_position(state, day_type, shirt)
    return _move_anchor(state, Rotation(day_type), Anchor(on, position))


def reset_outerwear(state: State, today: date) -> State:
    """Move the home outerwear rotation on by one from `today`.

    Over two kinds of outerwear, moving on by one and switching to the
    other are the same, so there is nothing to name. An office day
    moves no home rotation, so a reset there lands on the next home
    day.

    Args:
        state: The state to move the anchor in.
        today: The date the rotation is moved at.

    Returns:
        The state with the outerwear anchor moved, and the shirt
        anchors where they were.
    """
    rotation = Rotation.OUTERWEAR
    position = (
        _get_position(state, rotation, today) + 1
    ) % _get_length(rotation)
    return _move_anchor(state, rotation, Anchor(today, position))


def replace_(state: State, garment: str, label: str) -> State:
    """Give a garment a new label.

    Args:
        state: The state to replace_ in.
        garment: The garment, as show-closet prints it: its closet,
            what it is, and its label today.
        label: What it is called now.

    Returns:
        The state with the new label recorded.

    Raises:
        What2wearError: If the closet holds no such garment, or
            another of its kind already has the label.
    """
    scope, _, current_label = garment.rpartition(".")
    keys_by_label = _get_keys_by_label(state, scope)
    key = keys_by_label.get(current_label)
    if key is None:
        message = (
            f"no {scope.replace('.', ' ')} is called {current_label!r}"
            if keys_by_label
            else f"nothing is called {garment!r}"
        )
        raise What2wearError(message)
    key_already_holding_label = keys_by_label.get(label)
    if (
        key_already_holding_label is not None
        and key_already_holding_label != key
    ):
        message = f"{scope} already has a {label!r}"
        raise What2wearError(message)
    return replace(
        state,
        labels=MappingProxyType({**state.labels, key: label}),
    )


def swap(
    state: State, closet: DayType, first: str, second: str
) -> State:
    """Exchange two shirts' labels and colors.

    Args:
        state: The state to swap in.
        closet: The closet both shirts hang in.
        first: One shirt's label.
        second: The other's.

    Returns:
        The state with the two labels and colors exchanged.

    Raises:
        What2wearError: If either label names no shirt in the closet,
            or the two do not share pants.
    """
    shirts = CLOSETS[closet].shirts
    first_position, second_position = (
        _get_shirt_position(state, closet, label)
        for label in (first, second)
    )
    if shirts[first_position].pants != shirts[second_position].pants:
        message = (
            f"{first!r} and {second!r} do not share "
            f"pants, so swapping them would change more than a name"
        )
        raise What2wearError(message)
    first_key, second_key = (
        f"{closet}.shirt.{position}"
        for position in (first_position, second_position)
    )
    return replace(
        state,
        labels=MappingProxyType(
            {**state.labels, first_key: second, second_key: first}
        ),
        colors=MappingProxyType(
            {
                **state.colors,
                first_key: state.colors[second_key],
                second_key: state.colors[first_key],
            }
        ),
    )


def set_office_weekdays(
    state: State, weekdays: Collection[int], today: date
) -> State:
    """Set which weekdays are office days, moving no rotation.

    A position counts days of its kind since its anchor, so a new
    pattern would reclassify the past and move every rotation. Each
    anchor is therefore moved to `today`, at the position it held
    there under the old pattern. Recorded overrides are left alone.
    Restating the current weekdays changes nothing, anchors included.

    Args:
        state: The state to set them in.
        weekdays: The new office weekdays, Monday 0, as typed.
        today: The date every anchor is moved to.

    Returns:
        The state with the new weekdays and every anchor moved.

    Raises:
        What2wearError: If `weekdays` does not name exactly as many
            days as the given pattern, each once.
    """
    count = len(DEFAULT_OFFICE_WEEKDAYS)
    if len(weekdays) != count or len(frozenset(weekdays)) != count:
        message = (
            f"office weekdays must be exactly {count} different days; "
            "the count is a change to the source"
        )
        raise What2wearError(message)
    if frozenset(weekdays) == state.office_weekdays:
        return state
    return replace(
        state,
        office_weekdays=frozenset(weekdays),
        anchors=MappingProxyType(
            {
                rotation: Anchor(
                    today, _get_position(state, rotation, today)
                )
                for rotation in Rotation
            }
        ),
    )


def set_cold_threshold(state: State, threshold: float) -> State:
    """Set the high below which outerwear is worn.

    It decides only whether outerwear is worn, never which, so no
    rotation moves: a warm home day still spends its outerwear turn.

    Args:
        state: The state to set it in.
        threshold: The new threshold, in degrees Fahrenheit.

    Returns:
        The state with the threshold replaced.

    Raises:
        What2wearError: If `threshold` is not a finite number.
    """
    if not math.isfinite(threshold):
        message = f"{threshold} is not a temperature"
        raise What2wearError(message)
    return replace(state, cold_threshold=threshold)


def answer(
    state: State, on: date, weather: Mapping[date, float]
) -> Response:
    """Work out what to wear on a date.

    Args:
        state: The state to answer from.
        on: The date to answer for.
        weather: The forecast high, in degrees Fahrenheit, for each
            date the forecast reaches. A date it does not reach names
            its sweater and leaves open whether it is cold.

    Returns:
        The response for `on`, its garments named by the wearer's
        labels and drawn in the wearer's colors.
    """
    response = (
        _get_office_response(state, on)
        if _get_day_type(state, on) is DayType.OFFICE
        else _get_home_response(state, on)
    )
    labeled_response = _get_labeled_response(state, response)
    return _apply_weather(
        labeled_response, weather.get(on), state.cold_threshold
    )


def get_due_shirt(state: State, day_type: DayType, on: date) -> str:
    """Work out which shirt a closet's rotation is due to offer.

    Args:
        state: The state to read the rotation from.
        day_type: The closet to read.
        on: The date to read it on. A date of the other kind reads as
            the next date of this one, because a day of another kind
            does not move this rotation.

    Returns:
        The shirt's own name, not the wearer's label for it.
    """
    return _get_shirt(state, day_type, on).garment


def get_due_date(
    state: State, day_type: DayType, shirt: str, today: date
) -> date | None:
    """Work out when a closet's rotation is next due to offer a shirt.

    The inverse of `get_due_shirt`: one asks a date for its shirt, this
    asks a shirt for its date.

    Args:
        state: The state to read the rotation from.
        day_type: The closet the shirt hangs in.
        shirt: The wearer's label for the shirt.
        today: The date to search forward from, itself included.

    Returns:
        The first day of that kind whose due shirt is the one named, or
        None if no day within a year of `today` wears it.

    Raises:
        What2wearError: If the closet has no shirt so labeled.
    """
    position = _get_shirt_position(state, day_type, shirt)
    days = (
        today + timedelta(days=offset) for offset in range(HORIZON_DAYS)
    )
    return next(
        (
            on
            for on in days
            if _get_day_type(state, on) is day_type
            and _get_position(state, Rotation(day_type), on) == position
        ),
        None,
    )


def _move_anchor(
    state: State, rotation: Rotation, anchor: Anchor
) -> State:
    return replace(
        state,
        anchors=MappingProxyType({**state.anchors, rotation: anchor}),
    )


def _get_keys_by_label(state: State, scope: str) -> Mapping[str, str]:
    """Map each label in one closet and kind to the key under it."""
    return MappingProxyType(
        {
            label: key
            for key, label in state.labels.items()
            if key.rpartition(".")[0] == scope
        }
    )


def _get_day_type(state: State, on: date) -> DayType:
    return state.overrides.get(on, _get_default_day_type(state, on))


def _get_default_day_type(state: State, on: date) -> DayType:
    return (
        DayType.HOME
        if on in _get_holidays(on.year)
        else _get_pattern_day_type(state, on)
    )


@cache
def _get_holidays(year: int) -> frozenset[date]:
    """Federal holidays, observed, and the Friday after Thanksgiving."""
    federal_holidays = holidays.country_holidays("US", years=year)
    return frozenset(federal_holidays) | {
        on + timedelta(days=1)
        for on in federal_holidays.get_named("Thanksgiving")
    }


def _get_pattern_day_type(state: State, on: date) -> DayType:
    return (
        DayType.OFFICE
        if on.weekday() in state.office_weekdays
        else DayType.HOME
    )


def _get_shirt_position(
    state: State, day_type: DayType, label: str
) -> int:
    try:
        return next(
            position
            for position in range(len(CLOSETS[day_type].shirts))
            if state.labels[f"{day_type}.shirt.{position}"] == label
        )
    except StopIteration:
        message = f"no {day_type} shirt named {label!r}"
        raise What2wearError(message) from None


def _get_office_response(state: State, on: date) -> Response:
    resolved_days: tuple[Response, ...] = ()
    for day in _get_office_days_of_week(state, on):
        resolved_days = _resolve_office_day(state, resolved_days, day)
    return next(
        response for response in resolved_days if response.on == on
    )


def _get_office_days_of_week(
    state: State, on: date
) -> tuple[date, ...]:
    monday = on - timedelta(days=on.weekday())
    week = (monday + timedelta(days=offset) for offset in range(7))
    return tuple(
        day
        for day in week
        if _get_day_type(state, day) is DayType.OFFICE
    )


def _resolve_office_day(
    state: State, resolved_days: tuple[Response, ...], on: date
) -> tuple[Response, ...]:
    shirt = _get_shirt(state, DayType.OFFICE, on)
    worn_sweaters = frozenset(
        response.outfit.sweater.label
        for response in resolved_days
        if response.outfit.sweater is not None
    )
    sweater = _choose_office_sweater(
        _get_row_for_pants(CLOSETS[DayType.OFFICE], shirt.pants),
        worn_sweaters,
    )
    return (
        *resolved_days,
        Response(
            on=on,
            day_type=DayType.OFFICE,
            outfit=Outfit(
                shirt=_get_given_garment(shirt.garment),
                pants=_get_given_garment(shirt.pants),
                sweater=_get_given_garment(sweater),
                shoes=_get_given_garment(
                    _get_row_for_sweater(
                        CLOSETS[DayType.OFFICE], sweater
                    ).shoes
                ),
            ),
            unavoidable_repeat=sweater in worn_sweaters,
        ),
    )


def _get_shirt(state: State, day_type: DayType, on: date) -> Shirt:
    position = _get_position(state, Rotation(day_type), on)
    return CLOSETS[day_type].shirts[position]


def _get_position(state: State, rotation: Rotation, on: date) -> int:
    anchor = state.anchors[rotation]
    steps = _count_days_of_type_between(
        state, rotation.day_type, anchor.on, on
    )
    return (anchor.position + steps) % _get_length(rotation)


def _get_length(rotation: Rotation) -> int:
    return (
        len(HOME_OUTERWEAR)
        if rotation is Rotation.OUTERWEAR
        else len(CLOSETS[rotation.day_type].shirts)
    )


def _get_row_for_pants(closet: Closet, pants: str) -> PantsRow:
    return next(row for row in closet.rows if row.pants == pants)


def _choose_office_sweater(
    row: PantsRow, worn_sweaters: frozenset[str]
) -> str:
    if row.sweater not in worn_sweaters:
        return row.sweater
    if row.fallback is not None and row.fallback not in worn_sweaters:
        return row.fallback
    return row.sweater


def _get_row_for_sweater(closet: Closet, sweater: str) -> PantsRow:
    return next(row for row in closet.rows if row.sweater == sweater)


def _get_given_garment(name: str) -> Garment:
    """The garment as given, before any label or color is told."""
    return Garment(name, *COLORS[name])


def _get_home_response(state: State, on: date) -> Response:
    shirt = _get_shirt(state, DayType.HOME, on)
    row = _get_row_for_pants(CLOSETS[DayType.HOME], shirt.pants)
    outerwear = HOME_OUTERWEAR[
        _get_position(state, Rotation.OUTERWEAR, on)
    ]
    return Response(
        on=on,
        day_type=DayType.HOME,
        outfit=Outfit(
            shirt=_get_given_garment(shirt.garment),
            pants=_get_given_garment(shirt.pants),
            sweater=_get_given_garment(row.sweater)
            if outerwear == "sweater"
            else None,
            shoes=_get_given_garment(row.shoes),
            jacket=_get_given_garment(row.jacket)
            if outerwear == "jacket" and row.jacket is not None
            else None,
        ),
    )


def _get_labeled_response(state: State, response: Response) -> Response:
    scope = response.day_type
    outfit = response.outfit
    return replace(
        response,
        outfit=Outfit(
            shirt=_get_told_garment(
                state, f"{scope}.shirt", outfit.shirt
            ),
            pants=_get_told_garment(state, "pants", outfit.pants),
            sweater=_get_told_garment(
                state, f"{scope}.sweater", outfit.sweater
            )
            if outfit.sweater is not None
            else None,
            shoes=_get_told_garment(
                state, f"{scope}.shoes", outfit.shoes
            ),
            jacket=_get_told_garment(
                state, f"{scope}.jacket", outfit.jacket
            )
            if outfit.jacket is not None
            else None,
        ),
    )


def _get_told_garment(
    state: State, scope: str, given: Garment
) -> Garment:
    key = KEYS[f"{scope}.{given.label}"]
    return Garment(state.labels[key], *state.colors[key])


def _apply_weather(
    response: Response, high: float | None, threshold: float
) -> Response:
    if high is None:
        return response
    cold = high < threshold
    return replace(
        response,
        outfit=response.outfit
        if cold
        else replace(response.outfit, sweater=None, jacket=None),
        cold=cold,
    )


def _count_days_of_type_between(
    state: State, day_type: DayType, start: date, end: date
) -> int:
    """Count `day_type` days in [start, end), negative if reversed."""
    if end < start:
        return -_count_days_of_type_between(state, day_type, end, start)
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
            _get_pattern_day_type(state, tail + timedelta(days=offset))
            is day_type
            for offset in range(remaining_days)
        )
        + _count_days_off_pattern(state, day_type, start, end)
    )


def _count_days_off_pattern(
    state: State, day_type: DayType, start: date, end: date
) -> int:
    """Correct the pattern's count for overrides and holidays.

    A date both overridden and a holiday is counted once.
    """
    holidays_in_range = (
        on
        for year in range(start.year, end.year + 1)
        for on in _get_holidays(year)
    )
    return sum(
        (_get_day_type(state, on) is day_type)
        - (_get_pattern_day_type(state, on) is day_type)
        for on in {*state.overrides, *holidays_in_range}
        if start <= on < end
    )
