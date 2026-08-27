"""Where the State is kept: one JSON file the tool owns.

No human authors it, so there is no schema and nothing to validate --
a file that does not read back is a broken file rather than a wrong
one. A whole-file rewrite can truncate where the old append-only log
could not, so it is written beside the target and moved onto it, and a
write that fails partway leaves the previous State intact.
"""

import json
import os
from datetime import date
from pathlib import Path
from types import MappingProxyType
from typing import Any

from what2wear.errors import What2wearError
from what2wear.model import Anchor, DayType, State
from what2wear.wardrobe import get_default_state


def read_state(path: Path, today: date) -> State:
    """Read everything the tool has been told.

    A file that is not there is not an error and not a first run: it
    reads as the given Anchors with no Overrides. Nothing here creates
    a directory -- looking has no side effects.
    """
    try:
        text = path.read_text()
    except FileNotFoundError:
        return get_default_state(today)
    except OSError as error:
        message = f"could not read {path}: {error}"
        raise What2wearError(message) from None
    try:
        return _parse_state(json.loads(text))
    except (AttributeError, KeyError, TypeError, ValueError) as error:
        message = f"{path} does not read as a state file: {error}"
        raise What2wearError(message) from None


def write_state(path: Path, state: State) -> None:
    """Put everything the tool now knows back, all of it at once.

    Through a temporary file in the same directory and an atomic move,
    so a partial write is never observable. The move is only atomic
    against a crashed process; a crashed machine can land the rename
    ahead of the bytes, which is what the fsync rules out. The
    directory arrives with the first write and never merely because
    something looked.
    """
    temporary = path.with_name(f"{path.name}.tmp")
    text = json.dumps(_get_document(state), indent=2)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary.open("w") as file:
            file.write(text)
            file.flush()
            os.fsync(file.fileno())
        temporary.replace(path)
    except OSError as error:
        message = f"could not record to {path}: {error}"
        raise What2wearError(message) from None


def _parse_state(document: dict[str, Any]) -> State:
    """Read one document back as the State it was written from.

    Every kind of day is looked up by name, so a document missing one
    is a broken file rather than a State with a Rotation absent.
    """
    return State(
        anchors=MappingProxyType(
            {
                day_type: _parse_anchor(document["anchors"][day_type])
                for day_type in DayType
            }
        ),
        overrides=MappingProxyType(
            {
                date.fromisoformat(on): DayType(day_type)
                for on, day_type in document["overrides"].items()
            }
        ),
    )


def _parse_anchor(record: dict[str, Any]) -> Anchor:
    return Anchor(
        date.fromisoformat(record["date"]), record["position"]
    )


def _get_document(state: State) -> dict[str, Any]:
    """Lay a State out the way a person opening the file would read it.

    Nobody is expected to, but nothing here is a reason they could not.
    """
    return {
        "anchors": {
            day_type.value: {
                "date": anchor.on.isoformat(),
                "position": anchor.position,
            }
            for day_type, anchor in sorted(state.anchors.items())
        },
        "overrides": {
            on.isoformat(): day_type.value
            for on, day_type in sorted(state.overrides.items())
        },
    }
