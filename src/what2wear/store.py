"""Reading and writing the state file."""

import json
import os
from datetime import date
from pathlib import Path
from types import MappingProxyType
from typing import Any

from what2wear.errors import What2wearError
from what2wear.model import Anchor, DayType, Rotation, State
from what2wear.wardrobe import (
    KEYS,
    build_default_labels,
    get_default_state,
)


def read_state(path: Path, today: date) -> State:
    """Read the recorded state.

    Args:
        path: The state file to read.
        today: The date a default state is anchored to when there is
            no file at `path`.

    Returns:
        The state at `path`, or a default state if there is no file.

    Raises:
        What2wearError: If the file is unreadable or malformed.
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
    """Record the state, replacing any file already there.

    Args:
        path: The state file to write.
        state: The state to record.

    Raises:
        What2wearError: If the file cannot be written.
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
    """Parse a state document.

    A document written before the home outerwear rotation had an anchor
    reads as position 0 on the home shirt anchor's date, which the file
    has already pinned, so nothing has to be migrated.
    """
    records = {
        Rotation.OUTERWEAR: {
            **document["anchors"][Rotation.HOME],
            "position": 0,
        },
        **document["anchors"],
    }
    return State(
        anchors=MappingProxyType(
            {
                rotation: _parse_anchor(records[rotation])
                for rotation in Rotation
            }
        ),
        labels=MappingProxyType(
            dict(build_default_labels())
            | {
                KEYS.get(recorded, recorded): label
                for recorded, label in document.get(
                    "labels", {}
                ).items()
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
    given_labels = build_default_labels()
    return {
        "anchors": {
            rotation.value: {
                "date": anchor.on.isoformat(),
                "position": anchor.position,
            }
            for rotation, anchor in sorted(state.anchors.items())
        },
        "labels": {
            key: label
            for key, label in sorted(state.labels.items())
            if label != given_labels.get(key)
        },
        "overrides": {
            on.isoformat(): day_type.value
            for on, day_type in sorted(state.overrides.items())
        },
    }
