"""The imperative shell: reads the config, reads the clock, prints.

Deliberately disposable -- a thin renderer over `handle`, expected to be
replaced by something phone-friendly later.
"""

import argparse
import sys
from collections.abc import Sequence
from dataclasses import replace
from datetime import UTC, date, datetime
from pathlib import Path

from platformdirs import user_config_path

from what2wear.config import (
    ConfigError,
    MissingWardrobeError,
    load_state,
)
from what2wear.core import handle
from what2wear.decisions import (
    DecisionsError,
    append_decision,
    load_decisions,
)
from what2wear.model import DayType, Response


def run() -> int:
    """Answer from the Wardrobe this platform keeps for the user.

    The one seam that reads the platform directory, so no invocation
    can point the Wardrobe anywhere else.
    """
    return main(config_dir=user_config_path("what2wear"))


def main(argv: Sequence[str] | None = None, *, config_dir: Path) -> int:
    """Read the two files, answer, record what the answer decided.

    Recording comes before printing so that a log the tool cannot write
    to is reported rather than printed over. Nothing here creates the
    directory: the Wardrobe is read first, so a successful read has
    already proved it exists.
    """
    args = _parser().parse_args(argv)
    config = config_dir / "config.yaml"
    log = config_dir / "decisions.jsonl"
    on, record = _command(args)
    try:
        state = load_state(config)
        response = handle(
            on,
            replace(state, overrides=load_decisions(log)),
            today=_today(),
            record=record,
        )
        if response.decision is not None:
            append_decision(log, response.decision)
    except MissingWardrobeError:
        print(_first_run(config), file=sys.stderr)
        return 2
    except (ConfigError, DecisionsError) as error:
        print(error, file=sys.stderr)
        return 2
    print(_render(response))
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="what2wear",
        description="What to wear today, or on any other date.",
    )
    dates = parser.add_mutually_exclusive_group()
    dates.add_argument(
        "--on",
        type=_date,
        default=None,
        metavar="YYYY-MM-DD",
        help="the date to resolve; defaults to today",
    )
    dates.add_argument(
        "--stay-home",
        type=_date,
        nargs="?",
        const=None,
        default=argparse.SUPPRESS,
        metavar="YYYY-MM-DD",
        help="record that a date is a home day; defaults to today",
    )
    dates.add_argument(
        "--go-in",
        type=_date,
        nargs="?",
        const=None,
        default=argparse.SUPPRESS,
        metavar="YYYY-MM-DD",
        help="record that a date is an office day; defaults to today",
    )
    return parser


def _date(text: str) -> date:
    try:
        return date.fromisoformat(text)
    except ValueError:
        message = f"{text!r} is not a date of the form YYYY-MM-DD"
        raise argparse.ArgumentTypeError(message) from None


def _command(
    args: argparse.Namespace,
) -> tuple[date | None, DayType | None]:
    """Take the date being asked about, and what to record about it.

    A date of `None` means today, so the recording flags are suppressed
    when absent rather than defaulted -- absence is the missing
    attribute.
    """
    if "stay_home" in args:
        return args.stay_home, DayType.HOME
    if "go_in" in args:
        return args.go_in, DayType.OFFICE
    return args.on, None


def _today() -> date:
    """Give the wearer's own today.

    Local rather than UTC: the calendar this walks is the one on the
    wall, and a date is only ever a date here.
    """
    return datetime.now(UTC).astimezone().date()


def _first_run(config: Path) -> str:
    """Say where the Wardrobe goes and what to start it from.

    Nothing is configured yet, which is a first run rather than a
    failure, so it reads as an invitation and not as an error.
    """
    return "\n".join(
        [
            f"no wardrobe at {config}",
            (
                "write one there to get started -- copy example.yaml"
                " from the what2wear repo and make it yours"
            ),
        ]
    )


def _render(response: Response) -> str:
    decision = response.decision
    return "\n".join(
        [
            f"{response.on:%a %d %b %Y} - {response.day_type} day",
            f"  shirt    {response.outfit.shirt}",
            f"  pants    {response.outfit.pants}",
            f"  sweater  {response.outfit.sweater}",
            f"  shoes    {response.outfit.shoes}",
            *_repeat_note(response),
            # A command that writes something says what it wrote.
            *(
                (f"  recorded {decision.on} - {decision.day_type} day",)
                if decision is not None
                else ()
            ),
        ]
    )


def _repeat_note(response: Response) -> tuple[str, ...]:
    """Call out a Week with no sweater left to offer.

    Said rather than left to be noticed, so a repeat never looks like
    the tool having simply lost track.
    """
    return (
        ("  note     already worn this week -- no free sweater left",)
        if response.unavoidable_repeat
        else ()
    )
