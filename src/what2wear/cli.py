"""The imperative shell: reads the State, reads the clock, prints.

Deliberately disposable -- a thin renderer over the two seams, expected
to be replaced by something phone-friendly later. Every invocation is
about exactly one date, which is today unless `--on` says otherwise.
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
    shows its result without either knowing about the other. Both are
    handed the one date the invocation is about.
    """
    args = _parser().parse_args(argv)
    path = state_dir / "state.yaml"
    today = _today()
    on = getattr(args, "on", today)
    try:
        command = _command(args, on)
        state = _recorded(path, read_state(path, today), command, on)
        response = answer(state, on)
    except (StateError, UnknownShirtError) as error:
        print(error, file=sys.stderr)
        return 2
    print(_render(response, command, today))
    return 0


def _parser() -> argparse.ArgumentParser:
    dated = _dated()
    parser = argparse.ArgumentParser(
        prog="what2wear",
        description="What to wear today, or on any other date.",
        parents=[dated],
    )
    commands = parser.add_subparsers(dest="command")
    commands.add_parser(
        "stay-home",
        parents=[dated],
        help="record that a date is a home day",
    ).set_defaults(day_type=DayType.HOME)
    commands.add_parser(
        "go-in",
        parents=[dated],
        help="record that a date is an office day",
    ).set_defaults(day_type=DayType.OFFICE)
    reset = commands.add_parser(
        "reset",
        parents=[dated],
        help="move a date on to the next shirt, or to a named one",
    )
    reset.add_argument(
        "shirt",
        nargs="?",
        default=None,
        metavar="SHIRT",
        help="the shirt to move to; defaults to the next one",
    )
    return parser


def _dated() -> argparse.ArgumentParser:
    """Declare the `--on` that every invocation shares.

    One parent parser rather than a flag per command, so the date
    arrives the same way whatever is being asked. Suppressed rather
    than defaulted because a subcommand's own default would otherwise
    silently overwrite an `--on` given ahead of it, and record today.
    """
    dated = argparse.ArgumentParser(add_help=False)
    dated.add_argument(
        "--on",
        type=_date,
        default=argparse.SUPPRESS,
        metavar="YYYY-MM-DD",
        help="the date to act on; defaults to today",
    )
    return dated


def _date(text: str) -> date:
    try:
        return date.fromisoformat(text)
    except ValueError:
        message = f"{text!r} is not a date of the form YYYY-MM-DD"
        raise argparse.ArgumentTypeError(message) from None


def _today() -> date:
    """Give the wearer's own today.

    Local rather than UTC: the calendar this walks is the one on the
    wall, and a date is only ever a date here.
    """
    return datetime.now(UTC).astimezone().date()


def _command(args: argparse.Namespace, on: date) -> Command | None:
    """Say what the invocation asks to be recorded, if anything.

    Each command is known by what it brought with it rather than by
    its name, so the names live only on the parsers that declare them.
    """
    if "day_type" in args:
        return DayTypeOverride(on, args.day_type)
    if "shirt" in args:
        return ResetRequest(args.shirt)
    return None


def _recorded(
    path: Path, state: State, command: Command | None, on: date
) -> State:
    """Put what a command asked for into the State, and onto disk.

    Writing comes before printing so that a State the tool cannot
    write is reported rather than printed over.
    """
    if command is None:
        return state
    recorded = apply(state, command, on)
    write_state(path, recorded)
    return recorded


def _render(
    response: Response, command: Command | None, today: date
) -> str:
    return "\n".join(
        [
            f"{response.on:%a %d %b %Y} - {response.day_type} day",
            f"  shirt    {response.outfit.shirt}",
            f"  pants    {response.outfit.pants}",
            f"  sweater  {response.outfit.sweater}",
            f"  shoes    {response.outfit.shoes}",
            *_repeat_note(response),
            *_past_note(response, today),
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


def _past_note(response: Response, today: date) -> tuple[str, ...]:
    """Say that a past date answers from where things stand now.

    A Reset moves an Anchor and no wear history is kept, so a Position
    behind us is derived from the present rather than remembered. The
    date is answerable; what it is not is a record of what was worn.
    """
    if response.on >= today:
        return ()
    note = (
        "  note     a past date -- where the rotation stands now, "
        "not what was worn"
    )
    return (note,)


def _recorded_note(
    response: Response, command: Command | None
) -> tuple[str, ...]:
    """Say what a command that writes something wrote.

    A Reset names no Position, because the Shirt it moved to is the
    one printed above.
    """
    if command is None:
        return ()
    if isinstance(command, DayTypeOverride):
        return (f"  recorded {command.on} - {command.day_type} day",)
    return (f"  recorded {response.on} - shirt rotation reset",)
