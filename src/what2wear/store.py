"""Where the State is kept: one YAML file the tool owns.

No human authors it, so there is no schema and nothing to validate --
a file that does not read back is a broken file rather than a wrong
one. A whole-file rewrite can truncate where the old append-only log
could not, so it is written beside the target and moved onto it, and a
write that fails partway leaves the previous State intact.
"""

import os
from datetime import date
from pathlib import Path
from types import MappingProxyType
from typing import Any

import yaml

from what2wear import wardrobe
from what2wear.model import DayType, State, default_state


def read_state(path: Path, today: date) -> State:
    """Read everything the tool has been told.

    A file that is not there is not an error and not a first run: it
    reads as the given Anchors with no Overrides, and so does one
    written before a later version added a field. Nothing here creates
    a directory -- looking has no side effects.
    """
    try:
        text = path.read_text()
    except FileNotFoundError:
        return default_state(today)
    except OSError as error:
        message = f"could not read {path}: {error}"
        raise StateError(message) from None
    try:
        return _state(yaml.safe_load(text) or {}, today)
    except (
        yaml.YAMLError,
        AttributeError,
        KeyError,
        TypeError,
        ValueError,
    ) as error:
        message = f"{path} does not read as a state file: {error}"
        raise StateError(message) from None


def write_state(path: Path, state: State) -> None:
    """Put everything the tool now knows back, all of it at once.

    Through a temporary file in the same directory and an atomic move,
    so a partial write is never observable. The directory arrives with
    the first write and never merely because something looked.
    """
    temporary = path.with_name(f"{path.name}.tmp")
    document = yaml.safe_dump(_document(state), sort_keys=False)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        _write_document(temporary, document)
        temporary.replace(path)
    except OSError as error:
        message = f"could not record to {path}: {error}"
        raise StateError(message) from None


def _state(document: dict[str, Any], today: date) -> State:
    """Read one document back as the State it was written from.

    Anything it does not say is what a fresh installation would have
    said, so a file from before a field existed needs no migrating.
    """
    given = default_state(today)
    anchors = document.get("anchors") or {}
    return State(
        office_anchor=_anchor(
            anchors.get("office"), given.office_anchor
        ),
        home_anchor=_anchor(anchors.get("home"), given.home_anchor),
        overrides=MappingProxyType(
            {
                date.fromisoformat(on): DayType(day_type)
                for on, day_type in (
                    document.get("overrides") or {}
                ).items()
            }
        ),
    )


def _anchor(
    record: dict[str, Any] | None, given: wardrobe.Anchor
) -> wardrobe.Anchor:
    return (
        given
        if record is None
        else wardrobe.Anchor(
            date.fromisoformat(record["date"]), record["position"]
        )
    )


def _document(state: State) -> dict[str, Any]:
    """Lay a State out the way a person opening the file would read it.

    Nobody is expected to, but nothing here is a reason they could not.
    Dates are written out rather than left as dates so that two
    Anchors on one day read as two rather than as a YAML back-
    reference to the first.
    """
    return {
        "anchors": {
            "office": _record(state.office_anchor),
            "home": _record(state.home_anchor),
        },
        "overrides": {
            on.isoformat(): day_type.value
            for on, day_type in sorted(state.overrides.items())
        },
    }


def _record(anchor: wardrobe.Anchor) -> dict[str, Any]:
    return {
        "date": anchor.on.isoformat(),
        "position": anchor.position,
    }


def _write_document(path: Path, document: str) -> None:
    """Get a document all the way onto the disk before returning.

    The move is only atomic against a crashed process; a crashed
    machine can land the rename ahead of the bytes, which would leave
    an empty State where the previous one was. The flush is what makes
    the guarantee hold either way.
    """
    with path.open("w") as file:
        file.write(document)
        file.flush()
        os.fsync(file.fileno())


class StateError(Exception):
    """The State file cannot be read or written, or is not one."""
