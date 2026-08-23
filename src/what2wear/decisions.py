"""The decision log: append-only, and the tool's own.

The only file there is. One JSON record per line, so appending is a
write to the end and nothing else is ever touched.
"""

import json
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any

from what2wear.model import (
    DayType,
    DayTypeOverride,
    Decision,
    Reset,
    Rotation,
)


class DecisionsError(Exception):
    """The decision log cannot be read or written, or is not one."""


def load_decisions(path: Path) -> tuple[Decision, ...]:
    """Read every decision recorded so far, in the order recorded.

    Overrides and Resets share the one log and come back interleaved,
    each still carrying the date it applies from. A log that does not
    exist yet is an empty one -- nothing has been recorded, which is
    not an error.
    """
    try:
        text = path.read_text()
    except FileNotFoundError:
        return ()
    except OSError as error:
        message = f"could not read {path}: {error}"
        raise DecisionsError(message) from None

    try:
        return tuple(
            _decision(record)
            for record in (
                json.loads(line)
                for line in text.splitlines()
                if line.strip()
            )
        )
    except (KeyError, TypeError, ValueError) as error:
        message = f"{path} does not read as a decision log: {error}"
        raise DecisionsError(message) from None


def _decision(record: dict[str, Any]) -> Decision:
    """Read one record back as the decision it was written from.

    Which kind it is is what it carries: an Override says what the day
    became, a Reset which Rotation moved and by how much. A Rotation
    this version does not know is a bad record rather than a default.
    """
    on = date.fromisoformat(record["on"])
    if "day_type" in record:
        return DayTypeOverride(on, DayType(record["day_type"]))
    return Reset(
        on, Rotation(record["rotation"]), int(record["offset"])
    )


def append_decision(path: Path, decision: Decision) -> None:
    """Add one record to the end of the log.

    Whatever the decision carries is what gets written, so a new kind
    of decision needs nothing here. Starts the log, and the directory
    it lives in, if this is the first record -- a fresh installation
    has neither until something is recorded.
    """
    record = {**asdict(decision), "on": decision.on.isoformat()}
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a") as log:
            log.write(f"{json.dumps(record)}\n")
    except OSError as error:
        message = f"could not record to {path}: {error}"
        raise DecisionsError(message) from None
