"""The web shell: the pages the wearer opens on the phone."""

import hmac
from collections.abc import Callable, Mapping
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from flask import (
    Flask,
    abort,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug import Response as Reply

from what2wear.core import answer
from what2wear.errors import What2wearError
from what2wear.forecast import fetch_forecast
from what2wear.model import Response, State
from what2wear.store import read_state
from what2wear.wardrobe import TIMEZONE


def app(
    state_path: Path,
    token: str,
    fetch_weather: Callable[[], Mapping[date, float]] = fetch_forecast,
) -> Flask:
    """Build the web app.

    Every URL starts with the token, so whoever holds the URL can use
    the app and anyone else gets a plain 404.

    Args:
        state_path: The state file to read.
        token: The secret first segment of every URL.
        fetch_weather: Fetches the forecast high for each date it
            reaches, or nothing if it cannot.

    Returns:
        The app, for a WSGI server to serve.
    """
    web = Flask(__name__)

    @web.url_value_preprocessor
    def check_token(
        _endpoint: str | None, values: dict[str, Any] | None
    ) -> None:
        given = (values or {}).pop("token", "")
        if not hmac.compare_digest(given.encode(), token.encode()):
            abort(404)

    @web.url_defaults
    def add_token(_endpoint: str, values: dict[str, Any]) -> None:
        values.setdefault("token", token)

    @web.after_request
    def forbid_caching(reply: Reply) -> Reply:
        reply.headers["Cache-Control"] = "no-store"
        return reply

    @web.errorhandler(What2wearError)
    def show_error(error: What2wearError) -> tuple[str, int]:
        return render_template("base.html", message=str(error)), 500

    @web.get("/<token>/")
    def show_today() -> str:
        return render_day(_get_today())

    @web.get("/<token>/day")
    def pick_day() -> Reply:
        on = _parse_date(request.args.get("on", ""))
        return redirect(
            url_for("show_day", iso_date=on.isoformat()), code=303
        )

    @web.get("/<token>/day/<iso_date>")
    def show_day(iso_date: str) -> str:
        return render_day(_parse_date(iso_date))

    def render_day(on: date) -> str:
        today = _get_today()
        state = read_state(state_path, today)
        return _render_day(state, on, today, fetch_weather())

    return web


def _get_today() -> date:
    return datetime.now(TIMEZONE).date()


def _parse_date(text: str) -> date:
    """Parse a date spelled YYYY-MM-DD, so each date has one URL."""
    try:
        on = date.fromisoformat(text)
    except ValueError:
        abort(404)
    if on.isoformat() != text:
        abort(404)
    return on


def _render_day(
    state: State, on: date, today: date, weather: Mapping[date, float]
) -> str:
    """Render a date's Day page, or 404 at the calendar's ends.

    Answering walks the date's Week, and the page links the dates
    either side, so a date too near `date.min` or `date.max` has no
    page.
    """
    try:
        response = answer(state, on, weather)
        prev_day = on - timedelta(days=1)
        next_day = on + timedelta(days=1)
    except OverflowError:
        abort(404)
    return render_template(
        "day.html",
        response=response,
        garments=_get_garment_names(response),
        past=on < today,
        prev_day=prev_day,
        next_day=next_day,
    )


def _get_garment_names(response: Response) -> tuple[str, ...]:
    outfit = response.outfit
    hedge = ", if it's cold" if response.cold is None else ""
    return (
        f"{outfit.shirt.label} Shirt",
        f"{outfit.pants.label} Pants",
        *(
            f"{garment.label} {kind}{hedge}"
            for kind, garment in (
                ("Sweater", outfit.sweater),
                ("Jacket", outfit.jacket),
            )
            if garment is not None
        ),
        f"{outfit.shoes.label} Shoes",
    )
