"""The decision log: append-only, and the tool's own.

Kept apart from the hand-authored closet config on purpose -- writing
a decision can never reach the file the author wrote by hand. One JSON
record per line, so appending is a write to the end and nothing else
is ever touched.
"""

import json
from datetime import date
from pathlib import Path

from what2wear.model import DayType, DayTypeOverride


class DecisionsError(Exception):
    """The decision log cannot be read, written, or does not read as a
    log at all."""


def load_decisions(path: Path) -> tuple[DayTypeOverride, ...]:
    """Every decision recorded so far, in the order recorded.

    A log that does not exist yet is an empty one -- nothing has been
    recorded, which is not an error.
    """
    try:
        text = path.read_text()
    except FileNotFoundError:
        return ()
    except OSError as error:
        raise DecisionsError(
            f"could not read {path}: {error}"
        ) from None

    try:
        return tuple(
            DayTypeOverride(
                on=date.fromisoformat(record["on"]),
                day_type=DayType(record["day_type"]),
            )
            for record in (
                json.loads(line)
                for line in text.splitlines()
                if line.strip()
            )
        )
    except (KeyError, TypeError, ValueError) as error:
        raise DecisionsError(
            f"{path} does not read as a decision log: {error}"
        ) from None


def append_decision(path: Path, decision: DayTypeOverride) -> None:
    """Add one record to the end of the log, starting it if this is the
    first."""
    record = {
        "on": decision.on.isoformat(),
        "day_type": decision.day_type,
    }
    try:
        with path.open("a") as log:
            log.write(f"{json.dumps(record)}\n")
    except OSError as error:
        raise DecisionsError(
            f"could not record to {path}: {error}"
        ) from None
