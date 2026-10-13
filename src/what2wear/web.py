"""The web shell: the pages the wearer opens on the phone."""

import hmac
import math
import re
from collections.abc import Callable, Mapping
from datetime import date, datetime, timedelta
from functools import lru_cache, partial
from pathlib import Path
from types import MappingProxyType
from typing import Any

from flask import (
    Flask,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug import Response as Reply

from what2wear.core import (
    answer,
    get_day_type,
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
from what2wear.icons import Layer, get_art, get_art_template
from what2wear.model import (
    DayType,
    Garment,
    Response,
    State,
    UpdateFunction,
)
from what2wear.store import read_state, write_state
from what2wear.wardrobe import (
    CLOSETS,
    COLD_THRESHOLDS,
    TIMEZONE,
    WEEKDAYS,
    get_garments,
)

# How far each swipe moves the shown date: a day across the page, a
# Week across the strip.
SWIPE_DAYS = MappingProxyType(
    {"prev_week": -7, "prev_day": -1, "next_day": 1, "next_week": 7}
)
# The Closet page shows the Home Closet first, then the Office.
CLOSET_ORDER = (DayType.HOME, DayType.OFFICE)
# The rest of a Closet's Wardrobe, each kind in its own named grid.
OTHER_KINDS = MappingProxyType(
    {"sweater": "sweaters", "jacket": "jackets", "shoes": "shoes"}
)
# A Shirt due within this many days is due on a weekday by name.
WEEKDAY_DUE_DAYS = 6
# How long a fetched forecast is kept before it's fetched again.
FORECAST_SECONDS = 30 * 60


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
    fetch_kept_weather = _get_kept_fetch(fetch_weather)

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

    @web.get("/<token>/day/<iso_date>.json")
    def show_day_json(iso_date: str) -> Reply | tuple[Reply, int]:
        on = _parse_date(iso_date)
        try:
            state = read_state(state_path, _get_today())
            widget_day = _get_widget_day(
                state, on, fetch_kept_weather()
            )
        except What2wearError as error:
            return jsonify(error=str(error)), 500
        return jsonify(widget_day)

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

    @web.post("/<token>/closet/<key>")
    def replace_garment(key: str) -> Reply | tuple[str, int]:
        state = read_state(state_path, _get_today())
        if key not in state.labels:
            abort(404)
        label = request.form["label"]
        striped = "striped" in request.form
        color = _parse_color(request.form["color"])
        stripe_color = (
            _parse_color(request.form["stripe_color"])
            if striped
            else None
        )
        name = _get_garment_name(key, state.labels[key])
        return record(
            partial(
                replace_,
                key=key,
                label=label,
                color=color,
                stripe_color=stripe_color,
            ),
            f"the {name} replaced with {label}",
            lambda notice: render_closet(notice, (key, request.form)),
            lambda notice: url_for("show_closet", notice=notice),
        )

    # The home screen's icon, fetched with the page's own tokened URL,
    # since iOS's guess at the site's root would be refused.
    @web.get("/<token>/apple-touch-icon.png")
    def show_icon() -> Reply:
        return web.send_static_file("apple-touch-icon.png")

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
            fetch_kept_weather(),
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

    def render_closet(
        notice: str,
        refused_replace: tuple[str, Mapping[str, str]] | None = None,
    ) -> str:
        """Render the Closet, with a refused Replace's sheet open.

        `refused_replace` is the Garment's key and the form it posted,
        which its sheet is filled and drawn with.
        """
        today = _get_today()
        state = read_state(state_path, today)
        forms = {
            key: _get_replace_form(state, key) for key in state.labels
        } | dict([refused_replace] if refused_replace else [])
        shirt_grids = _get_shirt_grids(state, today, forms)
        garment_grids = _get_garment_grids(state, forms)
        return render_template(
            "closet.html",
            notice=notice,
            shirt_grids=shirt_grids,
            garment_grids=garment_grids,
            garments=tuple(
                garment
                for _, garments in (*shirt_grids, *garment_grids)
                for garment in garments
            ),
            art_templates=_get_art_templates(),
            open_sheet=(
                f"replace-{refused_replace[0]}"
                if refused_replace
                else ""
            ),
            today_title=_get_day_title(state, today),
        )

    def render_settings(notice: str) -> str:
        today = _get_today()
        state = read_state(state_path, today)
        return render_template(
            "settings.html",
            notice=notice,
            weekdays=WEEKDAYS,
            office_weekdays=state.office_weekdays,
            threshold=_round_degrees(state.cold_threshold),
            stored_threshold=_render_degrees(state.cold_threshold),
            thresholds=COLD_THRESHOLDS,
            today_title=_get_day_title(state, today),
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


def _get_kept_fetch(
    fetch_weather: Callable[[], Mapping[date, float]],
) -> Callable[[], Mapping[date, float]]:
    """Get a fetch that keeps its forecast for the half hour it's in.

    Each page would otherwise wait on fetching it. The half hour of the
    clock is the cache's key, and the fetch ignores it, so a new half
    hour fetches afresh. A failed fetch, which answers no forecast,
    isn't kept, so the next page tries again.
    """
    fetch_once = lru_cache(maxsize=1)(
        lambda _half_hour: fetch_weather()
    )

    def fetch_kept_weather() -> Mapping[date, float]:
        half_hour = int(
            datetime.now(TIMEZONE).timestamp() // FORECAST_SECONDS
        )
        forecast = fetch_once(half_hour)
        if not forecast:
            fetch_once.cache_clear()
        return forecast

    return fetch_kept_weather


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


def _get_widget_day(
    state: State, on: date, weather: Mapping[date, float]
) -> dict[str, Any]:
    """Answer for `on` as the widget draws it, from the same art."""
    try:
        response = answer(state, on, weather)
    except OverflowError:
        abort(404)
    return {
        "date": on.isoformat(),
        "day": str(response.day_type),
        "outfit": [
            {
                "garment": kind,
                "label": garment.label,
                **({"if_cold": True} if if_cold else {}),
                "art": get_art(kind, garment, response.day_type),
            }
            for kind, garment, if_cold in _get_worn_garments(response)
        ],
    }


def _get_worn_garments(
    response: Response,
) -> tuple[tuple[str, Garment, bool], ...]:
    """Each Garment worn, with its kind: Shirt, Pants, shoes, Outerwear.

    The essentials come first, and the Outerwear, which only the
    weather decides, last. Each carries whether it's Outerwear worn
    only if it's cold, which is when the forecast is unknown.
    """
    outfit = response.outfit
    cold_unknown = response.cold is None
    return tuple(
        (kind, garment, if_cold)
        for kind, garment, if_cold in (
            ("shirt", outfit.shirt, False),
            ("pants", outfit.pants, False),
            ("shoes", outfit.shoes, False),
            ("sweater", outfit.sweater, cold_unknown),
            ("jacket", outfit.jacket, cold_unknown),
        )
        if garment is not None
    )


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
        week = _get_week(state, on, today)
        swipes = {
            name: on + timedelta(days=days)
            for name, days in SWIPE_DAYS.items()
        }
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
        week=week,
        swipes=swipes,
        garments=_get_drawn_garments(response),
        past=on < today,
        is_today=on == today,
        other_day_type=other_day_type,
        other_article=_get_article(other_day_type),
        shirts=_get_shirt_tiles(state, response.day_type),
        other_outerwear=_get_other_outerwear(response)
        if on == today
        and response.day_type is DayType.HOME
        and response.cold is not False
        else None,
        today_title=_get_day_title(state, today),
    )


def _get_week(
    state: State, on: date, today: date
) -> tuple[dict[str, Any], ...]:
    """Each day of the Monday-start Week holding `on`, for the strip.

    Each carries its Day, and whether it's the day shown and today.
    """
    monday = on - timedelta(days=on.weekday())
    return tuple(
        {
            "on": day,
            "day_type": get_day_type(state, day),
            "shown": day == on,
            "today": day == today,
        }
        for day in (monday + timedelta(days=days) for days in range(7))
    )


def _get_drawn_garments(
    response: Response,
) -> tuple[dict[str, Any], ...]:
    """Each Garment worn: its Label, kind, art, and if only if cold."""
    return tuple(
        {
            "label": garment.label,
            "kind": kind.title(),
            "art": get_art(kind, garment, response.day_type),
            "if_cold": if_cold,
        }
        for kind, garment, if_cold in _get_worn_garments(response)
    )


def _get_shirt_tiles(
    state: State, day_type: DayType
) -> tuple[dict[str, Any], ...]:
    """Each Shirt in the `day_type` Closet: its Label and its art."""
    keys = tuple(
        f"{day_type}.shirt.{place}"
        for place in range(len(CLOSETS[day_type].shirts))
    )
    return tuple(
        {
            "label": state.labels[key],
            "art": get_art(
                "shirt",
                Garment(state.labels[key], *state.colors[key]),
                day_type,
            ),
        }
        for key in keys
    )


def _get_other_outerwear(response: Response) -> str:
    return (
        "jacket" if response.outfit.sweater is not None else "sweater"
    )


def _get_day_title(state: State, on: date) -> str:
    """Title `on`'s Day page as it opens: Home Day or Office Day.

    Every page's segment bar carries today's, so the Day segment can
    show it the moment it's tapped.
    """
    return f"{get_day_type(state, on).title()} Day"


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


def _get_replace_form(state: State, key: str) -> Mapping[str, str]:
    """Fill a Garment's Replace form as the State has it now."""
    color, stripe_color = state.colors[key]
    return {
        "label": state.labels[key],
        "color": color,
        "stripe_color": stripe_color or color,
    } | ({"striped": "on"} if stripe_color else {})


def _get_shirt_grids(
    state: State,
    today: date,
    forms: Mapping[str, Mapping[str, str]],
) -> tuple[tuple[DayType, tuple[dict[str, Any], ...]], ...]:
    """Each Closet's Shirts, Home first, for their tiles and sheets.

    A Shirt carries when it's next due, the rest of its Outfit on that
    date, and the Shirts sharing its Pants, which it may Swap with.
    The Outfit is answered without a forecast, its Outerwear worn if
    it's cold, so the Closet never waits on fetching one.
    """
    return tuple(
        (
            day_type,
            tuple(
                _get_shirt(state, day_type, place, today, forms)
                for place in range(len(CLOSETS[day_type].shirts))
            ),
        )
        for day_type in CLOSET_ORDER
    )


def _get_shirt(
    state: State,
    day_type: DayType,
    place: int,
    today: date,
    forms: Mapping[str, Mapping[str, str]],
) -> dict[str, Any]:
    key = f"{day_type}.shirt.{place}"
    shirts = CLOSETS[day_type].shirts
    due = get_due_date(state, day_type, state.labels[key], today)
    return _get_garment(state, key, day_type, forms) | {
        "closet": day_type,
        "due": due,
        "due_text": _get_due_text(due, today),
        "worn_garments": ()
        if due is None
        else tuple(
            garment | {"key": _get_key(state, day_type, garment)}
            for garment in _get_drawn_garments(answer(state, due, {}))
            if garment["kind"] != "Shirt"
        ),
        "partners": tuple(
            state.labels[f"{day_type}.shirt.{other}"]
            for other, shirt in enumerate(shirts)
            if other != place and shirt.pants == shirts[place].pants
        ),
    }


def _get_key(
    state: State, day_type: DayType, garment: Mapping[str, Any]
) -> str:
    """Find where a worn Garment hangs, by its Label within its kind."""
    kind = garment["kind"].lower()
    scope = kind if kind == "pants" else f"{day_type}.{kind}"
    return next(
        key
        for key, label in state.labels.items()
        if key.rpartition(".")[0] == scope and label == garment["label"]
    )


def _get_garment(
    state: State,
    key: str,
    day_type: DayType,
    forms: Mapping[str, Mapping[str, str]],
) -> dict[str, Any]:
    """A Garment's tile and its Replace sheet, filled as `forms`."""
    kind = key.split(".")[-2]
    label = state.labels[key]
    form = forms[key]
    return {
        "key": key,
        "label": label,
        "kind": kind.title(),
        "name": _get_garment_name(key, label),
        "art": get_art(
            kind, Garment(label, *state.colors[key]), day_type
        ),
        "preview": get_art(kind, _get_form_garment(form), day_type),
        "template": key.rpartition(".")[0],
        "form": form,
    }


def _get_form_garment(form: Mapping[str, str]) -> Garment:
    """The Garment a Replace form describes, its stripes if ticked."""
    return Garment(
        form["label"],
        form["color"],
        form["stripe_color"] if "striped" in form else None,
    )


def _get_due_text(due: date | None, today: date) -> str:
    """Say when a Shirt is next due, as near dates are spoken."""
    if due is None:
        return "Not due this year"
    days = (due - today).days
    if days == 0:
        return "Today"
    if days == 1:
        return "Tomorrow"
    if days <= WEEKDAY_DUE_DAYS:
        return f"{due:%A}"
    return f"{due:%a} {due.day} {due:%b}"


def _get_garment_grids(
    state: State, forms: Mapping[str, Mapping[str, str]]
) -> tuple[tuple[str, tuple[dict[str, Any], ...]], ...]:
    """The rest of the Wardrobe: the shared Pants, then each kind.

    Each grid is named and holds one kind from one Closet, Home first:
    sweaters, jackets, then shoes.
    """
    pants = tuple(
        _get_garment(state, f"pants.{place}", DayType.HOME, forms)
        for place in range(len(CLOSETS[DayType.OFFICE].rows))
    )
    return (
        ("Pants", pants),
        *(
            (
                f"{day_type.title()} {OTHER_KINDS[kind]}",
                tuple(
                    _get_garment(
                        state,
                        f"{day_type}.{kind}.{place}",
                        day_type,
                        forms,
                    )
                    for place in places
                ),
            )
            for day_type in CLOSET_ORDER
            for kind in OTHER_KINDS
            if (places := _get_places(day_type, kind))
        ),
    )


def _get_places(day_type: DayType, kind: str) -> tuple[int, ...]:
    """Where each `kind` hangs in the `day_type` Closet, once each."""
    return tuple(
        sorted(
            {
                place
                for garment_kind, place, _, _ in get_garments(
                    CLOSETS[day_type]
                )
                if garment_kind == kind
            }
        )
    )


def _get_art_templates() -> dict[str, tuple[Layer, ...]]:
    """Each Garment's art in paint roles, for the script to redraw.

    Keyed as a Garment's `template` names it: where it hangs, without
    its place.
    """
    return {"pants": get_art_template("pants", DayType.HOME)} | {
        f"{day_type}.{kind}": get_art_template(kind, day_type)
        for day_type in CLOSET_ORDER
        for kind in ("shirt", *OTHER_KINDS)
        if _get_places(day_type, kind)
    }


def _round_degrees(degrees: float) -> int:
    """Round `degrees` to a whole degree, a half up."""
    return math.floor(degrees + 0.5)
