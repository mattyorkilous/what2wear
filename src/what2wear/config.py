"""The config boundary: hand-authored YAML in, validated State out.

This module reads the file and never writes it -- comments and
formatting are the author's, not ours.
"""

from collections import Counter
from datetime import date
from pathlib import Path
from typing import Annotated

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from what2wear.model import Closet, Shirt, State

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


class _Closet(_Strict):
    anchor: _Anchor
    shirts: Annotated[list[_Shirt], Field(min_length=1)]


class _Config(_Strict):
    office_weekdays: Annotated[list[str], Field(min_length=1)]
    office: _Closet
    home: _Closet


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
        office=_closet(config.office, "office"),
        home=_closet(config.home, "home"),
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


def _closet(config: _Closet, setting: str) -> Closet:
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
    return Closet(
        shirts=tuple(
            Shirt(name=shirt.name, pants=shirt.pants)
            for shirt in config.shirts
        ),
        anchor_date=config.anchor.date,
        anchor_shirt=config.anchor.shirt,
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
    if state.office.anchor_date.weekday() not in state.office_weekdays:
        raise ConfigError(
            f"office anchor: {state.office.anchor_date} is not an"
            " office day under office_weekdays"
        )
    if state.home.anchor_date.weekday() in state.office_weekdays:
        raise ConfigError(
            f"home anchor: {state.home.anchor_date} is not a home day"
            " under office_weekdays"
        )
