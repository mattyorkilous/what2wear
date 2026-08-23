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
    parser = _parser()
    args = parser.parse_args(argv)
    _refuse_on_with_a_command(parser, args)
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
    parser.add_argument(
        "--on",
        type=_date,
        default=None,
        metavar="YYYY-MM-DD",
        help="the date to resolve; defaults to today",
    )
    commands = parser.add_subparsers(dest="command")
    stay_home = commands.add_parser(
        "stay-home",
        help="record that a date is a home day; defaults to today",
    )
    _overriding(stay_home, DayType.HOME)
    go_in = commands.add_parser(
        "go-in",
        help="record that a date is an office day; defaults to today",
    )
    _overriding(go_in, DayType.OFFICE)
    reset = commands.add_parser(
        "reset",
        help="move today on to the next shirt, or to a named one",
    )
    reset.add_argument(
        "shirt",
        nargs="?",
        default=None,
        metavar="SHIRT",
        help="the shirt to move to; defaults to the next one",
    )
    return parser


def _overriding(
    command: argparse.ArgumentParser, day_type: DayType
) -> None:
    """Set up a command that records a Day Type Override.

    The Day Type rides on the parser that names it, so a command's
    name and what it records are declared in one place rather than
    restated in a mapping that has to be kept in step.
    """
    command.set_defaults(record=day_type)
    command.add_argument(
        "date",
        type=_date,
        nargs="?",
        default=None,
        metavar="YYYY-MM-DD",
        help="the date to record against; defaults to today",
    )


def _date(text: str) -> date:
    try:
        return date.fromisoformat(text)
    except ValueError:
        message = f"{text!r} is not a date of the form YYYY-MM-DD"
        raise argparse.ArgumentTypeError(message) from None


def _refuse_on_with_a_command(
    parser: argparse.ArgumentParser, args: argparse.Namespace
) -> None:
    """Refuse an `--on` given alongside a command.

    `--on` is the date a bare invocation asks about. Every command
    either carries the date it is about or is only ever about today,
    so an `--on` beside one would have to be ignored or guessed at.
    """
    if args.on is not None and args.command is not None:
        parser.error(f"--on cannot be combined with {args.command}")


def _command(
    args: argparse.Namespace,
) -> tuple[date | None, DayType | ResetRequest | None]:
    """Take the date being asked about, and what to record about it.

    A date of `None` means today. A Reset takes a Shirt where the
    others take a date, and so is only ever about today.
    """
    if "record" in args:
        return args.date, args.record
    if args.command == "reset":
        return None, ResetRequest(args.shirt)
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
