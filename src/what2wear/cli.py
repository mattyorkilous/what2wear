"""The imperative shell: reads the config, reads the clock, prints.

Deliberately disposable -- a thin renderer over `handle`, expected to be
replaced by something phone-friendly later.
"""

import argparse
import os
import sys
from collections.abc import Sequence
from dataclasses import replace
from datetime import date
from pathlib import Path

from what2wear.config import ConfigError, load_state
from what2wear.core import handle
from what2wear.decisions import (
    DecisionsError,
    append_decision,
    load_decisions,
)
from what2wear.model import DayType, Response

CONFIG_ENV_VAR = "WHAT2WEAR_CONFIG"
DEFAULT_CONFIG = Path("what2wear.yaml")
DECISIONS_ENV_VAR = "WHAT2WEAR_DECISIONS"
DEFAULT_DECISIONS = Path("what2wear.decisions.jsonl")


def main(argv: Sequence[str] | None = None) -> int:
    """Read the two files, answer, record what the answer decided.

    Recording comes before printing so that a log the tool cannot write
    to is reported rather than printed over.
    """
    args = _parser().parse_args(argv)
    log = Path(os.environ.get(DECISIONS_ENV_VAR) or DEFAULT_DECISIONS)
    on, record = _command(args)
    try:
        state = load_state(_config_path(args.config))
        response = handle(
            on,
            replace(state, overrides=load_decisions(log)),
            today=date.today(),
            record=record,
        )
        if response.decision is not None:
            append_decision(log, response.decision)
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
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        metavar="PATH",
        help=(
            "the closet config to read; defaults to"
            f" ${CONFIG_ENV_VAR}, or {DEFAULT_CONFIG}"
        ),
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


def _config_path(given: Path | None) -> Path:
    """The flag, then the environment, then the default.

    The default is relative to the working directory, so the command
    works from anywhere without the core knowing where files live.
    """
    if given is not None:
        return given
    return Path(os.environ.get(CONFIG_ENV_VAR) or DEFAULT_CONFIG)


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
