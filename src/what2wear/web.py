"""The web shell: the pages the wearer opens on the phone."""

import hmac
import re
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
    get_due_date,
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
from what2wear.icons import get_icon
from what2wear.model import (
    DayType,
    Response,
    State,
    UpdateFunction,
)
from what2wear.store import read_state, write_state
from what2wear.wardrobe import (
    CLOSETS,
    KEYS,
    TIMEZONE,
    WEEKDAYS,
    get_garments,
)


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
        return record_day(
            partial(record_override, on=on, day_type=day_type),
            on,
            f"{_get_article(day_type)} {day_type.title()} Day",
        )

    @web.post("/<token>/day/<iso_date>/shirt")
    def set_shirt(iso_date: str) -> Reply | tuple[str, int]:
        on = _parse_date(iso_date)
        shirt = request.form["shirt"]
        return record_day(
            partial(reset, shirt=shirt, on=on),
            on,
            f"the Shirt Rotation reset to {shirt}",
        )

    @web.post("/<token>/outerwear")
    def switch_outerwear() -> Reply | tuple[str, int]:
        today = _get_today()
        return record_day(
            partial(reset_outerwear, today=today),
            today,
            "the Home Outerwear Rotation reset",
        )

    @web.get("/<token>/closet")
    def show_closet() -> str:
        return render_closet(request.args.get("notice", ""))

    @web.post("/<token>/closet/<closet>/swap")
    def swap_shirts(closet: str) -> Reply | tuple[str, int]:
        try:
            day_type = DayType(closet)
        except ValueError:
            abort(404)
        first, second = request.form["first"], request.form["second"]
        return record(
            partial(swap, closet=day_type, first=first, second=second),
            f"the {day_type.title()} {first} and {second} Shirts "
            "swapped",
            render_closet,
            lambda notice: url_for("show_closet", notice=notice),
        )

    @web.get("/<token>/closet/<key>")
    def show_garment(key: str) -> str:
        state = read_state(state_path, _get_today())
        if key not in state.labels:
            abort(404)
        color, stripe_color = state.colors[key]
        return render_garment(
            key,
            "",
            {
                "label": state.labels[key],
                "color": color,
                "stripe_color": stripe_color or color,
            }
            | ({"striped": "on"} if stripe_color else {}),
        )

    @web.post("/<token>/closet/<key>")
    def replace_garment(key: str) -> Reply | tuple[str, int]:
        state = read_state(state_path, _get_today())
        if key not in state.labels:
            abort(404)
        scope = key.rpartition(".")[0]
        label = request.form["label"]
        striped = "striped" in request.form
        color = _parse_color(request.form["color"])
        stripe_color = (
            _parse_color(request.form["stripe_color"])
            if striped
            else None
        )
        current = state.labels[key]
        name = _get_garment_name(key, current)
        return record(
            partial(
                replace_,
                garment=f"{scope}.{current}",
                label=label,
                color=color,
                stripe_color=stripe_color,
            ),
            f"the {name} replaced with {label}",
            lambda notice: render_garment(key, notice, request.form),
            lambda notice: url_for("show_closet", notice=notice),
        )

    @web.get("/<token>/settings")
    def show_settings() -> str:
        return render_settings(request.args.get("notice", ""))

    @web.post("/<token>/settings/office-weekdays")
    def save_office_weekdays() -> Reply | tuple[str, int]:
        weekdays = _parse_weekdays(request.form.getlist("weekday"))
        return record_settings(
            partial(
                set_office_weekdays,
                weekdays=weekdays,
                today=_get_today(),
            ),
            "Office Weekdays "
            + ", ".join(
                WEEKDAYS[weekday].title() for weekday in weekdays
            ),
        )

    @web.post("/<token>/settings/cold-threshold")
    def save_cold_threshold() -> Reply | tuple[str, int]:
        threshold = _parse_threshold(request.form["threshold"])
        return record_settings(
            partial(set_cold_threshold, threshold=threshold),
            f"a Cold Threshold of {_render_degrees(threshold)}°F",
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

    def record_day(
        update: UpdateFunction, on: date, confirmation: str
    ) -> Reply | tuple[str, int]:
        return record(
            update,
            confirmation,
            partial(render_day, on),
            lambda notice: (
                url_for("show_today", notice=notice)
                if on == _get_today()
                else url_for(
                    "show_day", iso_date=on.isoformat(), notice=notice
                )
            ),
        )

    def record(
        update: UpdateFunction,
        confirmation: str,
        render_page: Callable[[str], str],
        get_url: Callable[[str], str],
    ) -> Reply | tuple[str, int]:
        """Record a write, then send the wearer back to its page.

        The State is written only if it changed, and the notice says
        which. A refusal re-shows the page with its message instead.
        """
        state = read_state(state_path, _get_today())
        try:
            updated_state = update(state)
        except What2wearError as error:
            return render_page(str(error)), 422
        state_changed = updated_state != state
        if state_changed:
            write_state(state_path, updated_state)
        outcome = "Recorded" if state_changed else "Already"
        return redirect(get_url(f"{outcome}: {confirmation}"), code=303)

    def render_closet(notice: str) -> str:
        today = _get_today()
        state = read_state(state_path, today)
        return render_template(
            "closet.html",
            notice=notice,
            closets={
                day_type: _get_closet_rows(state, day_type, today)
                for day_type in DayType
            },
        )

    def render_garment(
        key: str, notice: str, form: Mapping[str, str]
    ) -> str:
        """Render a Garment's Replace form, filled in as `form`."""
        state = read_state(state_path, _get_today())
        return render_template(
            "garment.html",
            notice=notice,
            key=key,
            garment=_get_garment_name(key, state.labels[key]),
            form=form,
        )

    def render_settings(notice: str) -> str:
        state = read_state(state_path, _get_today())
        return render_template(
            "settings.html",
            notice=notice,
            weekdays=WEEKDAYS,
            office_weekdays=state.office_weekdays,
            threshold=_render_degrees(state.cold_threshold),
        )

    def record_settings(
        update: UpdateFunction, confirmation: str
    ) -> Reply | tuple[str, int]:
        return record(
            update,
            confirmation,
            render_settings,
            lambda notice: url_for("show_settings", notice=notice),
        )

    return web


def _get_today() -> date:
    return datetime.now(TIMEZONE).date()


def _parse_date(text: str) -> date:
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
        garments=_get_drawn_garments(response),
        past=on < today,
        prev_day=prev_day,
        next_day=next_day,
        other_day_type=other_day_type,
        other_article=_get_article(other_day_type),
        shirts=_get_shirt_labels(state, response.day_type),
        other_outerwear=_get_other_outerwear(response)
        if on == today
        and response.day_type is DayType.HOME
        and response.cold is not False
        else None,
    )


def _get_drawn_garments(
    response: Response,
) -> tuple[dict[str, Any], ...]:
    """Each Garment worn: its name, its icon, and whether it's dimmed.

    Outerwear worn only if it's cold is dimmed and says so.
    """
    outfit = response.outfit
    cold_unknown = response.cold is None
    return tuple(
        {
            "name": f"{garment.label} {kind.title()}"
            + (", if it's cold" if dim else ""),
            "icon": get_icon(kind, garment),
            "dim": dim,
        }
        for kind, garment, dim in (
            ("shirt", outfit.shirt, False),
            ("pants", outfit.pants, False),
            ("sweater", outfit.sweater, cold_unknown),
            ("jacket", outfit.jacket, cold_unknown),
            ("shoes", outfit.shoes, False),
        )
        if garment is not None
    )


def _get_shirt_labels(
    state: State, day_type: DayType
) -> tuple[str, ...]:
    return tuple(
        state.labels[f"{day_type}.shirt.{place}"]
        for place in range(len(CLOSETS[day_type].shirts))
    )


def _get_other_outerwear(response: Response) -> str:
    return (
        "jacket" if response.outfit.sweater is not None else "sweater"
    )


def _parse_color(text: str) -> str:
    """Parse a color as an `<input type="color">` posts it."""
    if re.fullmatch(r"#[0-9a-fA-F]{6}", text) is None:
        abort(400)
    return text.lower()


def _get_garment_name(key: str, label: str) -> str:
    """Name a Garment as the wearer reads it: Office White Shirt."""
    closet, _, kind = key.rpartition(".")[0].rpartition(".")
    return f"{closet.title()} {label} {kind.title()}".lstrip()


def _parse_weekdays(texts: list[str]) -> tuple[int, ...]:
    """Parse ticked weekdays, Monday 0, each one a day of the week."""
    try:
        weekdays = tuple(int(text) for text in texts)
    except ValueError:
        abort(400)
    if not all(weekday in range(len(WEEKDAYS)) for weekday in weekdays):
        abort(400)
    return weekdays


def _parse_threshold(text: str) -> float:
    try:
        return float(text)
    except ValueError:
        abort(400)


def _render_degrees(degrees: float) -> str:
    """Render degrees exactly, without a trailing `.0`."""
    return str(degrees).removesuffix(".0")


def _get_closet_rows(
    state: State, day_type: DayType, today: date
) -> tuple[dict[str, Any], ...]:
    """Each Pants Row: its Pants, its Shirts and what else it wears.

    A Shirt carries its next due date and the Shirts it may Swap
    with, which are those sharing its Pants.
    """
    garments = get_garments(CLOSETS[day_type])
    return tuple(
        {
            "pants": state.labels[KEYS[f"pants.{row.pants}"]],
            "pants_key": KEYS[f"pants.{row.pants}"],
            "shirts": _get_row_shirts(
                state,
                day_type,
                tuple(
                    f"{day_type}.shirt.{place}"
                    for kind, place, _, pants in garments
                    if kind == "shirt" and pants == row.pants
                ),
                today,
            ),
            "others": tuple(
                (
                    f"{day_type}.{kind}.{place}",
                    (
                        f"{state.labels[f'{day_type}.{kind}.{place}']} "
                        f"{kind.title()}"
                    ),
                )
                for kind, place, _, pants in garments
                if kind != "shirt" and pants == row.pants
            ),
        }
        for row in CLOSETS[day_type].rows
    )


def _get_row_shirts(
    state: State,
    day_type: DayType,
    keys: tuple[str, ...],
    today: date,
) -> tuple[dict[str, Any], ...]:
    labels = tuple(state.labels[key] for key in keys)
    return tuple(
        {
            "key": key,
            "label": label,
            "due": get_due_date(state, day_type, label, today),
            "partners": tuple(
                other for other in labels if other != label
            ),
        }
        for key, label in zip(keys, labels, strict=True)
    )
