"""The config boundary: hand-authored YAML in, validated State out.

This module reads the file and never writes it -- comments and
formatting are the author's, not ours.
"""

from collections import Counter
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from typing import Annotated

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from what2wear.model import Closet, DayType, PantsRow, Shirt, State

WEEKDAYS = {
    "mon": 0,
    "tue": 1,
    "wed": 2,
    "thu": 3,
    "fri": 4,
    "sat": 5,
    "sun": 6,
}


class ConfigError(Exception):
    """The config is missing, unparseable, or does not describe a
    usable wardrobe."""


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class _Anchor(_Strict):
    date: date
    shirt: str


class _Shirt(_Strict):
    name: str
    pants: str


class _Pants(_Strict):
    sweater: str
    shoes: str


class _OfficePants(_Pants):
    fallback: str | None = None


class _HomePants(_Pants):
    jacket: str


class _Closet(_Strict):
    anchor: _Anchor
    shirts: Annotated[list[_Shirt], Field(min_length=1)]


class _OfficeCloset(_Closet):
    pants: dict[str, _OfficePants]


class _HomeCloset(_Closet):
    pants: dict[str, _HomePants]


class _Config(_Strict):
    office_weekdays: Annotated[list[str], Field(min_length=1)]
    office: _OfficeCloset
    home: _HomeCloset


def load_state(path: Path) -> State:
    """Parse and validate the closet config, or raise ConfigError with
    a clear message."""
    try:
        text = path.read_text()
    except FileNotFoundError:
        raise ConfigError(f"no config file at {path}") from None
    except UnicodeDecodeError:
        raise ConfigError(
            f"{path} is not UTF-8 text -- is it really the config file?"
        ) from None
    except OSError as error:
        raise ConfigError(f"could not read {path}: {error}") from None

    try:
        document = yaml.safe_load(text)
    except yaml.YAMLError as error:
        raise ConfigError(
            f"{path} is not valid YAML: {error}"
        ) from None

    try:
        config = _Config.model_validate(document)
    except ValidationError as error:
        raise ConfigError(
            f"{path} is not a valid config:\n{_explain(error)}"
        ) from None

    state = State(
        office=_office_closet(config.office),
        home=_home_closet(config.home),
        office_weekdays=_weekdays(config.office_weekdays),
    )
    _check_anchor_day_types(state)
    return state


def _explain(error: ValidationError) -> str:
    return "\n".join(
        f"  {'.'.join(str(part) for part in item['loc']) or '(root)'}"
        f": {item['msg']}"
        for item in error.errors()
    )


def _office_closet(config: _OfficeCloset) -> Closet:
    rows = _rows(config.pants)
    _check_office_pants(rows)
    return _closet(config, rows, "office")


def _home_closet(config: _HomeCloset) -> Closet:
    rows = _rows(config.pants)
    return _closet(config, rows, "home")


def _rows(pants: Mapping[str, _Pants]) -> tuple[PantsRow, ...]:
    """Turn the pants-keyed mapping into rows that know their own
    colour.

    Whichever of `fallback` and `jacket` the setting allows comes
    across with the rest; the other one was never parsed.
    """
    return tuple(
        PantsRow(pants=colour, **row.model_dump())
        for colour, row in pants.items()
    )


def _weekdays(names: list[str]) -> frozenset[int]:
    unknown = [name for name in names if name.lower() not in WEEKDAYS]
    if unknown:
        raise ConfigError(
            "office_weekdays: unknown weekday"
            f" {', '.join(repr(name) for name in unknown)}"
            f" -- use {', '.join(WEEKDAYS)}"
        )
    weekdays = frozenset(WEEKDAYS[name.lower()] for name in names)
    if len(weekdays) == len(WEEKDAYS):
        raise ConfigError(
            "office_weekdays: every weekday is an office day, leaving"
            " no home days"
        )
    return weekdays


def _check_anchor_day_types(state: State) -> None:
    """An Anchor Date has to be a day of its own Closet's kind, or it
    counts nothing."""
    if state.day_type(state.office.anchor_date) is not DayType.OFFICE:
        raise ConfigError(
            f"office anchor: {state.office.anchor_date} is not an"
            " office day under office_weekdays"
        )
    if state.day_type(state.home.anchor_date) is not DayType.HOME:
        raise ConfigError(
            f"home anchor: {state.home.anchor_date} is not a home day"
            " under office_weekdays"
        )


def _check_office_pants(rows: tuple[PantsRow, ...]) -> None:
    """Office sweaters pair one-to-one with office shoes, and a
    Fallback is always another row's sweater.

    Together those are what let a Fallback bring the donor row's shoes
    along with it, and what makes no-repeat shoes follow from
    no-repeat sweaters.
    """
    sweaters = Counter(row.sweater for row in rows)
    shared = tuple(
        sweater for sweater, count in sweaters.items() if count > 1
    )
    if shared:
        raise ConfigError(
            "office pants: more than one row wears sweater"
            f" {', '.join(repr(sweater) for sweater in shared)}, so"
            " its shoes are ambiguous"
        )
    stray = tuple(
        row
        for row in rows
        if row.fallback is not None
        and row.fallback
        not in {
            other.sweater for other in rows if other.pants != row.pants
        }
    )
    if stray:
        described = ", ".join(
            f"{row.fallback!r} for {row.pants} pants" for row in stray
        )
        raise ConfigError(
            f"office pants: fallback {described} is no other row's"
            " sweater"
        )


def _closet(
    config: _Closet, rows: tuple[PantsRow, ...], setting: str
) -> Closet:
    names = Counter(shirt.name for shirt in config.shirts)
    duplicates = [name for name, count in names.items() if count > 1]
    if duplicates:
        raise ConfigError(
            f"{setting} closet: duplicate shirt name"
            f" {', '.join(repr(name) for name in duplicates)}"
        )
    if config.anchor.shirt not in names:
        raise ConfigError(
            f"{setting} anchor shirt {config.anchor.shirt!r} is not in"
            f" the {setting} closet"
        )
    unmapped = sorted(
        {shirt.pants for shirt in config.shirts}
        - {row.pants for row in rows}
    )
    if unmapped:
        raise ConfigError(
            f"{setting} closet: no pants row for"
            f" {', '.join(repr(pants) for pants in unmapped)}"
        )
    return Closet(
        shirts=tuple(
            Shirt(name=shirt.name, pants=shirt.pants)
            for shirt in config.shirts
        ),
        pants=rows,
        anchor_date=config.anchor.date,
        anchor_shirt=config.anchor.shirt,
    )
