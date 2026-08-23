"""The imperative shell: reads the log, reads the clock, prints.

Deliberately disposable -- a thin renderer over `handle`, expected to be
replaced by something phone-friendly later.
"""

import argparse
import sys
from collections.abc import Sequence
from datetime import UTC, date, datetime
from pathlib import Path

from platformdirs import user_config_path

from what2wear.core import PastDateError, UnknownShirtError, handle
from what2wear.decisions import (
    DecisionsError,
    append_decision,
    load_decisions,
)
from what2wear.model import (
    DayType,
    DayTypeOverride,
    Decision,
    Reset,
    ResetRequest,
    Response,
    State,
)


def run() -> int:
    """Answer from the log this platform keeps for the user.

    The one seam that reads the platform directory, so no invocation
    can point the tool's own file anywhere else.
    """
    return main(state_dir=user_config_path("what2wear"))


def main(argv: Sequence[str] | None = None, *, state_dir: Path) -> int:
    """Answer, then record what the answer decided.

    Recording comes before printing so that a log the tool cannot write
    to is reported rather than printed over.
    """
    args = _parser().parse_args(argv)
    log = state_dir / "decisions.jsonl"
    on, record = _command(args)
    try:
        state = _with_decisions(load_decisions(log))
        response = handle(on, state, today=_today(), record=record)
        if response.decision is not None:
            append_decision(log, response.decision)
    except (
        DecisionsError,
        PastDateError,
        UnknownShirtError,
    ) as error:
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
    dates.add_argument(
        "--reset",
        nargs="?",
        const=None,
        default=argparse.SUPPRESS,
        metavar="SHIRT",
        help="move today on to the next shirt, or to a named one",
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
) -> tuple[date | None, DayType | ResetRequest | None]:
    """Take the date being asked about, and what to record about it.

    A date of `None` means today, so the recording flags are suppressed
    when absent rather than defaulted -- absence is the missing
    attribute. A Reset takes a Shirt where the others take a date, and
    so is only ever about today.
    """
    if "stay_home" in args:
        return args.stay_home, DayType.HOME
    if "go_in" in args:
        return args.go_in, DayType.OFFICE
    if "reset" in args:
        return None, ResetRequest(args.reset)
    return args.on, None


def _with_decisions(decisions: tuple[Decision, ...]) -> State:
    """Read the one log into a State, each kind in its field.

    The log is written in the order decided; nothing here needs that
    order, because every decision carries the date it applies from.
    """
    return State(
        overrides=tuple(
            decision
            for decision in decisions
            if isinstance(decision, DayTypeOverride)
        ),
        resets=tuple(
            decision
            for decision in decisions
            if isinstance(decision, Reset)
        ),
    )


def _today() -> date:
    """Give the wearer's own today.

    Local rather than UTC: the calendar this walks is the one on the
    wall, and a date is only ever a date here.
    """
    return datetime.now(UTC).astimezone().date()


def _render(response: Response) -> str:
    return "\n".join(
        [
            f"{response.on:%a %d %b %Y} - {response.day_type} day",
            f"  shirt    {response.outfit.shirt}",
            f"  pants    {response.outfit.pants}",
            f"  sweater  {response.outfit.sweater}",
            f"  shoes    {response.outfit.shoes}",
            *_repeat_note(response),
            *_recorded_note(response.decision),
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


def _recorded_note(decision: Decision | None) -> tuple[str, ...]:
    """Say what a command that writes something wrote."""
    if decision is None:
        return ()
    if isinstance(decision, DayTypeOverride):
        return (f"  recorded {decision.on} - {decision.day_type} day",)
    return (
        (
            f"  recorded {decision.on} - {decision.rotation}"
            f" rotation {decision.offset:+d}"
        ),
    )
