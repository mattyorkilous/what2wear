"""The imperative shell: reads the config, reads the clock, prints.

Deliberately disposable -- a thin renderer over `handle`, expected to be
replaced by something phone-friendly later.
"""

import argparse
import sys
from collections.abc import Sequence
from dataclasses import replace
from datetime import date
from pathlib import Path

from platformdirs import user_config_path

from what2wear.config import ConfigError, MissingWardrobe, load_state
from what2wear.core import handle
from what2wear.decisions import (
    DecisionsError,
    append_decision,
    load_decisions,
)
from what2wear.model import DayType, Response


def run() -> int:
    """The entry point: the Wardrobe lives where this platform keeps a
    user's config, and no invocation can point it elsewhere."""
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
            today=date.today(),
            record=record,
        )
        if response.decision is not None:
            append_decision(log, response.decision)
    except MissingWardrobe:
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


def _command(
    args: argparse.Namespace,
) -> tuple[date | None, DayType | None]:
    """The date being asked about, and what to record about it.

    A date of `None` means today, so the recording flags are suppressed
    when absent rather than defaulted -- absence is the missing
    attribute.
    """
    if "stay_home" in args:
        return args.stay_home, DayType.HOME
    if "go_in" in args:
        return args.go_in, DayType.OFFICE
    return args.on, None


def _first_run(config: Path) -> str:
    """Nothing is configured yet, which is not a failure -- so say
    where the Wardrobe goes and what to start it from."""
    return "\n".join(
        [
            f"no wardrobe at {config}",
            "write one there to get started -- copy example.yaml from"
            " the what2wear repo and make it yours",
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


def _date(text: str) -> date:
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"{text!r} is not a date of the form YYYY-MM-DD"
        ) from None


def _repeat_note(response: Response) -> tuple[str, ...]:
    """Say so when the Week has no sweater left to offer, rather than
    letting the repeat pass unremarked."""
    return (
        ("  note     already worn this week -- no free sweater left",)
        if response.unavoidable_repeat
        else ()
    )
