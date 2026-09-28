"""The web shell: the pages the wearer opens on the phone."""

import hmac
from collections.abc import Callable, Mapping
from datetime import date, datetime, timedelta
from functools import partial
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

from what2wear.core import (
    answer,
    record_override,
    reset,
    reset_outerwear,
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
from what2wear.wardrobe import CLOSETS, TIMEZONE


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
        return render_day(_get_today(), request.args.get("notice", ""))

    @web.get("/<token>/day")
    def pick_day() -> Reply:
        on = _parse_date(request.args.get("on", ""))
        return redirect(
            url_for("show_day", iso_date=on.isoformat()), code=303
        )

    @web.get("/<token>/day/<iso_date>")
    def show_day(iso_date: str) -> str:
        return render_day(
            _parse_date(iso_date), request.args.get("notice", "")
        )

    @web.post("/<token>/day/<iso_date>/day-type")
    def set_day_type(iso_date: str) -> Reply | tuple[str, int]:
        on = _parse_date(iso_date)
        try:
            day_type = DayType(request.form["day_type"])
        except ValueError:
            abort(400)
        return record(
            partial(record_override, on=on, day_type=day_type),
            on,
            f"{_get_article(day_type)} {day_type.title()} Day",
        )

    @web.post("/<token>/day/<iso_date>/shirt")
    def set_shirt(iso_date: str) -> Reply | tuple[str, int]:
        on = _parse_date(iso_date)
        shirt = request.form["shirt"]
        return record(
            partial(reset, shirt=shirt, on=on),
            on,
            f"the Shirt Rotation reset to {shirt}",
        )

    @web.post("/<token>/outerwear")
    def switch_outerwear() -> Reply | tuple[str, int]:
        today = _get_today()
        return record(
            partial(reset_outerwear, today=today),
            today,
            "the Home Outerwear Rotation reset",
        )

    def render_day(on: date, notice: str) -> str:
        today = _get_today()
        state = read_state(state_path, today)
        return _render_day(
            state,
            on,
            today,
            fetch_weather(),
            notice,
        )

    def record(
        update: UpdateFunction, on: date, confirmation: str
    ) -> Reply | tuple[str, int]:
        """Record a write, then send the wearer back to its Day page.

        The State is written only if it changed, and the notice says
        which. A refusal re-shows the page with its message instead.
        """
        today = _get_today()
        state = read_state(state_path, today)
        try:
            updated_state = update(state)
        except What2wearError as error:
            return render_day(on, str(error)), 422
        state_changed = updated_state != state
        if state_changed:
            write_state(state_path, updated_state)
        outcome = "Recorded" if state_changed else "Already"
        notice = f"{outcome}: {confirmation}"
        destination = (
            url_for("show_today", notice=notice)
            if on == today
            else url_for(
                "show_day", iso_date=on.isoformat(), notice=notice
            )
        )
        return redirect(destination, code=303)

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


def _get_article(day_type: DayType) -> str:
    return "an" if day_type is DayType.OFFICE else "a"


def _render_day(
    state: State,
    on: date,
    today: date,
    weather: Mapping[date, float],
    notice: str,
) -> str:
    try:
        response = answer(state, on, weather)
        prev_day = on - timedelta(days=1)
        next_day = on + timedelta(days=1)
    except OverflowError:
        abort(404)
    other_day_type = (
        DayType.HOME
        if response.day_type is DayType.OFFICE
        else DayType.OFFICE
    )
    return render_template(
        "day.html",
        notice=notice,
        response=response,
        garments=_get_garment_names(response),
        past=on < today,
        prev_day=prev_day,
        next_day=next_day,
        other_day_type=other_day_type,
        other_article=_get_article(other_day_type),
        shirts=_get_shirt_labels(state, response.day_type),
        other_outerwear=_get_other_outerwear(state, today)
        if on == today and response.day_type is DayType.HOME
        else None,
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


def _get_shirt_labels(
    state: State, day_type: DayType
) -> tuple[str, ...]:
    return tuple(
        state.labels[f"{day_type}.shirt.{place}"]
        for place in range(len(CLOSETS[day_type].shirts))
    )


def _get_other_outerwear(state: State, today: date) -> str:
    due_outfit = answer(state, today, {}).outfit
    return "jacket" if due_outfit.sweater is not None else "sweater"
