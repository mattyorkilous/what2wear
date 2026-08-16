"""The imperative shell: reads the config, reads the clock, prints.

Deliberately disposable -- a thin renderer over `handle`, expected to be
replaced by something phone-friendly later.
"""

import argparse
import os
import sys
from collections.abc import Sequence
from datetime import date, datetime
from pathlib import Path

from what2wear.config import ConfigError, load_state
from what2wear.core import handle
from what2wear.model import Response, Show

CONFIG_ENV_VAR = "WHAT2WEAR_CONFIG"
DEFAULT_CONFIG = Path("what2wear.yaml")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        state = load_state(
            args.config
            if args.config is not None
            else _default_config()
        )
    except ConfigError as error:
        print(error, file=sys.stderr)
        return 2
    print(_render(handle(Show(on=args.on), state, today=date.today())))
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


def _default_config() -> Path:
    """Where to look when no --config is given.

    Relative to the working directory unless $WHAT2WEAR_CONFIG says
    otherwise, so the command works from anywhere without the core
    knowing where files live.
    """
    return Path(os.environ.get(CONFIG_ENV_VAR) or DEFAULT_CONFIG)


def _render(response: Response) -> str:
    return "\n".join(
        [
            f"{response.on:%a %d %b %Y} - {response.day_type} day",
            f"  shirt  {response.outfit.shirt}",
            f"  pants  {response.outfit.pants}",
        ]
    )


def _date(text: str) -> date:
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"{text!r} is not a date of the form YYYY-MM-DD"
        ) from None
