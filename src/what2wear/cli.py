"""The imperative shell: reads the State, reads the clock, prints.

Deliberately disposable -- a thin renderer over the two seams, expected
to be replaced by something phone-friendly later. It is also where the
past is refused: `answer` counts from an Anchor and so has no idea
what today is.
"""

import argparse
import sys
from collections.abc import Sequence
from datetime import UTC, date, datetime
from pathlib import Path

from platformdirs import user_config_path

from what2wear.core import UnknownShirtError, answer, apply
from what2wear.model import (
    Command,
    DayType,
    DayTypeOverride,
    ResetRequest,
    Response,
    State,
)
from what2wear.store import StateError, read_state, write_state


def main() -> int:
    """Answer from the State this platform keeps for the user.

    The one seam that reads the platform directory, so no invocation
    can point the tool's own file anywhere else.
    """
    return run(state_dir=user_config_path("what2wear"))


def run(argv: Sequence[str] | None = None, *, state_dir: Path) -> int:
    """Answer, and record first if the command asked for that.

    The two seams composed: `apply` says what the State becomes and
    `answer` says what the date calls for, so a command that records
    shows its result without either knowing about the other.
    """
    parser = _parser()
    args = parser.parse_args(argv)
    _refuse_on_with_a_command(parser, args)
    path = state_dir / "state.yaml"
    today = _today()
    try:
        on, command = _command(args, today)
        state = _recorded(path, read_state(path, today), command, today)
        response = answer(state, on)
    except (StateError, PastDateError, UnknownShirtError) as error:
        print(error, file=sys.stderr)
        return 2
    print(_render(response, command))
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
    command.set_defaults(day_type=day_type)
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


def _today() -> date:
    """Give the wearer's own today.

    Local rather than UTC: the calendar this walks is the one on the
    wall, and a date is only ever a date here.
    """
    return datetime.now(UTC).astimezone().date()


def _command(
    args: argparse.Namespace, today: date
) -> tuple[date, Command | None]:
    """Take the date being answered about, and what to record on it.

    Each command is known by what it brought with it rather than by
    its name, so the names live only on the parsers that declare them.
    A command carries its own date, defaulting to today; a Reset is
    only ever about today. Only the bare question can name a past
    date, and that is the one thing refused -- correcting what a date
    now behind us was still has to be possible.
    """
    if "day_type" in args:
        on = today if args.date is None else args.date
        return on, DayTypeOverride(on, args.day_type)
    if "shirt" in args:
        return today, ResetRequest(args.shirt)
    return _answerable(args.on, today), None


def _answerable(on: date | None, today: date) -> date:
    """Settle which date a bare invocation is asking about.

    None is today. A date behind today is refused here rather than in
    the core, which counts from an Anchor and never reads a clock.
    """
    if on is not None and on < today:
        message = (
            f"{on} is in the past, and the past is not answerable."
        )
        raise PastDateError(message)
    return today if on is None else on


def _recorded(
    path: Path, state: State, command: Command | None, today: date
) -> State:
    """Put what a command asked for into the State, and onto disk.

    Writing comes before printing so that a State the tool cannot
    write is reported rather than printed over.
    """
    if command is None:
        return state
    recorded = apply(state, command, today)
    write_state(path, recorded)
    return recorded


def _render(response: Response, command: Command | None) -> str:
    return "\n".join(
        [
            f"{response.on:%a %d %b %Y} - {response.day_type} day",
            f"  shirt    {response.outfit.shirt}",
            f"  pants    {response.outfit.pants}",
            f"  sweater  {response.outfit.sweater}",
            f"  shoes    {response.outfit.shoes}",
            *_repeat_note(response),
            *_recorded_note(response, command),
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


def _recorded_note(
    response: Response, command: Command | None
) -> tuple[str, ...]:
    """Say what a command that writes something wrote.

    A Reset names no Position, because the Shirt it moved to is the
    one printed two lines up.
    """
    if command is None:
        return ()
    if isinstance(command, DayTypeOverride):
        return (f"  recorded {command.on} - {command.day_type} day",)
    return (f"  recorded {response.on} - shirt rotation reset",)


class PastDateError(Exception):
    """A date before today was asked about.

    A Reset rewrites what a past Position was and no wear history is
    kept, so the answer would be a fact about the present dressed up
    as one about the past.
    """
