"""The command line interface."""

import argparse
import sys
from collections.abc import Callable, Iterable, Mapping, Sequence
from datetime import UTC, date, datetime, timedelta
from functools import partial
from pathlib import Path

from platformdirs import user_config_path

from what2wear.core import (
    answer,
    get_due_date,
    get_due_shirt,
    record_override,
    replace_,
    reset,
    reset_outerwear,
    set_cold_threshold,
    set_office_weekdays,
    swap,
)
from what2wear.errors import What2wearError
from what2wear.forecast import fetch_forecast
from what2wear.model import (
    DayType,
    Response,
    State,
    UpdateFunction,
)
from what2wear.store import read_state, write_state
from what2wear.wardrobe import CLOSETS, KEYS, WEEKDAYS, get_garments


def main() -> int:
    """Run the CLI against the wearer's config directory.

    Returns:
        The process exit code.
    """
    return run(
        state_dir=user_config_path("what2wear"),
        fetch_weather=fetch_forecast,
    )


def run(
    argv: Sequence[str] | None = None,
    *,
    state_dir: Path,
    fetch_weather: Callable[[], Mapping[date, float]],
) -> int:
    """Run the CLI over the given arguments.

    Args:
        argv: The arguments to parse, or None to read `sys.argv`.
        state_dir: The directory holding the state file.
        fetch_weather: Fetches the forecast high for each date it
            reaches, or nothing if it cannot.

    Returns:
        The process exit code: 0, or 2 if the command failed.
    """
    today = datetime.now(UTC).astimezone().date()
    args = _get_parser(today).parse_args(argv)
    path = state_dir / "state.json"
    try:
        state = read_state(path, today)
        display = _get_display(args, state, today)
        if display is not None:
            print(display)
            return 0
        updated_state = _choose_update_function(args, today)(state)
        changed = updated_state != state
        if changed:
            write_state(path, updated_state)
        on = _get_date(args, updated_state, today)
        if on is None:
            print(_get_nothing_due(args))
            return 0
        weather = fetch_weather()
        response = answer(updated_state, on, weather)
    except What2wearError as error:
        print(error, file=sys.stderr)
        return 2
    confirmation = _get_confirmation(args)
    print(_render(response, confirmation, today, changed=changed))
    return 0


def _get_parser(today: date) -> argparse.ArgumentParser:
    date_parser = _get_date_parser(today)
    parser = argparse.ArgumentParser(
        prog="what2wear",
        description="What to wear today, or on any other date.",
        parents=[date_parser],
    )
    subparsers = parser.add_subparsers(dest="action")
    subparsers.add_parser(
        "stay-home",
        parents=[date_parser],
        help="record that a date is a home day",
    )
    subparsers.add_parser(
        "go-in",
        parents=[date_parser],
        help="record that a date is an office day",
    )
    reset_parser = subparsers.add_parser(
        "reset",
        parents=[date_parser],
        help="move a date's rotation to a named shirt",
    )
    reset_parser.add_argument(
        "shirt", metavar="SHIRT", help="the shirt to move to"
    )
    subparsers.add_parser(
        "reset-outerwear",
        help="move home outerwear on to the other kind",
    )
    replace_parser = subparsers.add_parser(
        "replace",
        help="give a garment a new label",
    )
    replace_parser.add_argument(
        "garment",
        metavar="GARMENT",
        help="the garment, as show-closet prints it",
    )
    replace_parser.add_argument(
        "label", metavar="LABEL", help="what it is called now"
    )
    swap_parser = subparsers.add_parser(
        "swap",
        help="exchange two shirts' labels, if they share pants",
    )
    swap_parser.add_argument(
        "closet",
        type=DayType,
        choices=tuple(DayType),
        metavar="CLOSET",
        help="office or home",
    )
    swap_parser.add_argument("first", metavar="LABEL")
    swap_parser.add_argument("second", metavar="LABEL")
    when_parser = subparsers.add_parser(
        "when",
        help="name the next date a shirt is due",
    )
    when_parser.add_argument(
        "garment",
        metavar="SHIRT",
        help="the shirt, as show-closet prints it",
    )
    subparsers.add_parser(
        "show-closet",
        help="list every garment and how to name it",
    )
    subparsers.add_parser(
        "office-weekdays",
        help="show the three weekdays you go in",
    )
    weekdays_parser = subparsers.add_parser(
        "set-office-weekdays",
        help="set the three weekdays you go in",
    )
    weekdays_parser.add_argument(
        "weekdays",
        nargs="+",
        type=_parse_weekday,
        metavar="WEEKDAY",
        help="mon to sun; name exactly three",
    )
    subparsers.add_parser(
        "cold-threshold",
        help="show the high below which outerwear is worn",
    )
    threshold_parser = subparsers.add_parser(
        "set-cold-threshold",
        help="set the high below which outerwear is worn",
    )
    threshold_parser.add_argument(
        "threshold",
        type=float,
        metavar="DEGREES",
        help="in Fahrenheit",
    )
    return parser


def _get_date_parser(today: date) -> argparse.ArgumentParser:
    date_parser = argparse.ArgumentParser(add_help=False)
    date_parser.add_argument(
        "--on",
        type=partial(_parse_date, today=today),
        default=today,
        metavar="DATE",
        help=(
            "the date to act on: YYYY-MM-DD, tomorrow, yesterday, or "
            "a weekday name for the soonest such date; defaults to "
            "today"
        ),
    )
    return date_parser


def _parse_date(text: str, *, today: date) -> date:
    weekday = _get_weekday(text)
    match text.lower():
        case "tomorrow":
            return today + timedelta(days=1)
        case "yesterday":
            return today - timedelta(days=1)
        case _ if weekday is not None:
            ahead = (weekday - today.weekday()) % 7
            return today + timedelta(days=ahead)
        case _:
            try:
                return date.fromisoformat(text)
            except ValueError:
                problem = (
                    f"{text!r} is not a date: give YYYY-MM-DD, "
                    "tomorrow, yesterday, or a weekday "
                    f"({' '.join(WEEKDAYS)})"
                )
                raise argparse.ArgumentTypeError(problem) from None


def _get_weekday(text: str) -> int | None:
    names = (
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    )
    word = text.lower()
    return next(
        (
            weekday
            for weekday, name in enumerate(names)
            if word in {name, name[:3]}
        ),
        None,
    )


def _parse_weekday(text: str) -> int:
    weekday = _get_weekday(text)
    if weekday is None:
        problem = f"{text!r} is not a weekday: {' '.join(WEEKDAYS)}"
        raise argparse.ArgumentTypeError(problem)
    return weekday


def _get_display(
    args: argparse.Namespace, state: State, today: date
) -> str | None:
    """Return everything a command that only shows prints, or None."""
    match args.action:
        case "show-closet":
            return _render_wardrobe(state, today)
        case "office-weekdays":
            weekdays = _render_weekdays(state.office_weekdays)
            return f"office weekdays {weekdays}"
        case "cold-threshold":
            return f"cold threshold {state.cold_threshold:g}°F"
        case _:
            return None


def _render_wardrobe(state: State, today: date) -> str:
    return "\n".join(
        (
            "> the shirt each closet is due to give you",
            "",
            *_get_closet_lines(state, DayType.OFFICE, today),
            *_get_closet_lines(state, DayType.HOME, today),
            "pants",
            *(
                _get_garment_line(state, "pants", place, "")
                for place in range(len(CLOSETS[DayType.OFFICE].rows))
            ),
        )
    )


def _get_closet_lines(
    state: State, day_type: DayType, today: date
) -> tuple[str, ...]:
    due = get_due_shirt(state, day_type, today)
    return (
        f"{day_type}",
        *(
            _get_garment_line(
                state,
                f"{day_type}.{kind}",
                place,
                state.labels[KEYS[f"pants.{pants}"]],
                due=kind == "shirt" and garment == due,
            )
            for kind, place, garment, pants in get_garments(
                CLOSETS[day_type]
            )
        ),
        "",
    )


def _get_garment_line(
    state: State,
    scope: str,
    place: int,
    pants: str,
    *,
    due: bool = False,
) -> str:
    label = state.labels[f"{scope}.{place}"]
    kind = scope.rpartition(".")[2]
    gutter = "> " if due else "  "
    return f"{gutter}{kind:<8} {label:<12} {pants:<12} {scope}.{label}"


def _render_weekdays(weekdays: Iterable[int]) -> str:
    return " ".join(WEEKDAYS[weekday] for weekday in sorted(weekdays))


def _choose_update_function(
    args: argparse.Namespace, today: date
) -> UpdateFunction:
    """Return the core function that records what was typed.

    Args:
        args: The parsed arguments.
        today: The date a command that takes no date acts on.

    Returns:
        The function recording it, or one that hands back the state it
        was given if nothing was typed.
    """
    match args.action:
        case None | "when":
            return lambda state: state
        case "stay-home":
            return partial(
                record_override, on=args.on, day_type=DayType.HOME
            )
        case "go-in":
            return partial(
                record_override, on=args.on, day_type=DayType.OFFICE
            )
        case "reset":
            return partial(reset, shirt=args.shirt, on=args.on)
        case "reset-outerwear":
            return partial(reset_outerwear, today=today)
        case "replace":
            return partial(
                replace_, garment=args.garment, label=args.label
            )
        case "swap":
            return partial(
                swap,
                closet=args.closet,
                first=args.first,
                second=args.second,
            )
        case "set-office-weekdays":
            return partial(
                set_office_weekdays,
                weekdays=args.weekdays,
                today=today,
            )
        case "set-cold-threshold":
            return partial(set_cold_threshold, threshold=args.threshold)
        case _:
            raise AssertionError(args.action)


def _get_date(
    args: argparse.Namespace, state: State, today: date
) -> date | None:
    if args.action != "when":
        return args.on
    day_type, label = _get_named_shirt(args.garment)
    return get_due_date(state, day_type, label, today)


def _get_named_shirt(garment: str) -> tuple[DayType, str]:
    closet, _, label = garment.partition(".shirt.")
    if not label or closet not in tuple(DayType):
        message = (
            f"when asks about shirts, and {garment!r} is not one: name "
            "a shirt the way show-closet prints it, such as "
            "office.shirt.white"
        )
        raise What2wearError(message)
    return DayType(closet), label


def _get_nothing_due(args: argparse.Namespace) -> str:
    closet, label = _get_named_shirt(args.garment)
    return f"no {closet} day in the next year wears {label}"


def _get_confirmation(args: argparse.Namespace) -> str:
    """Return the line describing what was typed, or "" if none."""
    match args.action:
        case None | "when":
            return ""
        case "stay-home":
            return f"{args.on} - {DayType.HOME} day"
        case "go-in":
            return f"{args.on} - {DayType.OFFICE} day"
        case "reset":
            return f"{args.on} - shirt rotation reset to {args.shirt}"
        case "reset-outerwear":
            return "home outerwear rotation reset"
        case "replace":
            return f"{args.garment} is {args.label}"
        case "swap":
            return (
                f"{args.closet} {args.first} and {args.second} swapped"
            )
        case "set-office-weekdays":
            return (
                f"office weekdays {_render_weekdays(args.weekdays)}, "
                "every rotation re-anchored to today"
            )
        case "set-cold-threshold":
            return f"cold threshold {args.threshold:g}°F"
        case _:
            raise AssertionError(args.action)


def _render(
    response: Response, confirmation: str, today: date, *, changed: bool
) -> str:
    return "\n".join(
        [
            f"{response.on:%a %d %b %Y} - {response.day_type} day",
            f"  shirt    {response.outfit.shirt.label}",
            f"  pants    {response.outfit.pants.label}",
            *_get_outerwear_lines(response),
            f"  shoes    {response.outfit.shoes.label}",
            *_get_notes(response, confirmation, today, changed=changed),
        ]
    )


def _get_outerwear_lines(response: Response) -> tuple[str, ...]:
    outfit = response.outfit
    hedge = ", if it's cold" if response.cold is None else ""
    return tuple(
        f"  {kind:<8} {garment.label}{hedge}"
        for kind, garment in (
            ("sweater", outfit.sweater),
            ("jacket", outfit.jacket),
        )
        if garment is not None
    )


def _get_notes(
    response: Response,
    confirmation: str,
    today: date,
    *,
    changed: bool,
) -> tuple[str, ...]:
    repeat = (
        ("  note     already worn this week -- no free sweater left",)
        if response.unavoidable_repeat
        else ()
    )
    past = (
        "  note     a past date -- where the rotation stands now, "
        "not what was worn"
    )
    behind = (past,) if response.on < today else ()
    confirmed = (
        (f"  {'recorded' if changed else 'already':<8} {confirmation}",)
        if confirmation
        else ()
    )
    return (*repeat, *behind, *confirmed)
