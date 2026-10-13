import dataclasses
import html
import json
import re
from collections.abc import Callable
from datetime import UTC, date, datetime, time, timedelta, tzinfo
from functools import reduce
from itertools import accumulate
from pathlib import Path
from typing import Any, Self
from unittest.mock import Mock
from urllib.parse import parse_qs, urlsplit

import pytest
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from what2wear import web
from what2wear.core import (
    answer,
    get_day_type,
    get_due_date,
    record_override,
)
from what2wear.model import DayType, State
from what2wear.store import read_state, write_state
from what2wear.wardrobe import (
    CLOSETS,
    COLORS,
    DEFAULT_COLD_THRESHOLD,
    TIMEZONE,
    build_default_colors,
    build_default_labels,
    get_default_state,
)

TOKEN = "s3cret"  # noqa: S105
SAT = 5
PINNED_TODAY = date(2026, 10, 13)
# Every Shirt, as the Closet page lists them: Home, then Office.
SHIRT_KEYS = [
    *(f"home.shirt.{place}" for place in range(9)),
    *(f"office.shirt.{place}" for place in range(5)),
]


@pytest.fixture
def state_path(tmp_path: Path) -> Path:
    return tmp_path / "state.json"


@pytest.fixture
def client(state_path: Path) -> FlaskClient:
    # No forecast, so no test here touches the network.
    return web.app(state_path, TOKEN, fetch_weather=dict).test_client()


@pytest.fixture
def pinned_client(
    client: FlaskClient, monkeypatch: pytest.MonkeyPatch
) -> FlaskClient:
    """The client, with today pinned to `PINNED_TODAY` in New York."""
    _pin_clock(monkeypatch, time(12))
    return client


def test_the_bare_url_is_todays_day_page(client: FlaskClient) -> None:
    page = _get_text(client, f"/{TOKEN}/")
    assert _get_shown_date(page) == _get_today()
    assert _get_title(page) in {"Office Day", "Home Day"}
    assert [kind for _, _, kind in _get_drawn_garments(page)][:3] == [
        "Shirt",
        "Pants",
        "Shoes",
    ]


def test_today_is_todays_date_in_new_york(
    client: FlaskClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    # 2 am UTC on the 28th is still the evening of the 27th in New
    # York, so a page reading the server's UTC clock shows the 28th.
    class Evening(datetime):
        @classmethod
        def now(cls, tz: tzinfo | None = None) -> Self:
            return cls(2026, 9, 28, 2, tzinfo=UTC).astimezone(tz)

    monkeypatch.setattr(web, "datetime", Evening)
    page = _get_text(client, f"/{TOKEN}/")
    assert _get_shown_date(page) == date(2026, 9, 27)


def test_a_day_page_shows_that_date(client: FlaskClient) -> None:
    day = _get_today() + timedelta(days=400)
    page = _get_text(client, f"/{TOKEN}/day/{day}")
    assert _get_shown_date(page) == day


def test_the_title_is_the_day(client: FlaskClient) -> None:
    saturday = _get_next(SAT)
    page = _get_text(client, f"/{TOKEN}/day/{saturday}")
    assert _get_title(page) == "Home Day"
    page = _post_text(
        client,
        f"/{TOKEN}/day/{saturday}/day-type",
        {"day_type": "office"},
    )
    assert _get_title(page) == "Office Day"


def test_a_garment_reads_as_its_label_over_its_kind(
    client: FlaskClient,
) -> None:
    page = _get_text(client, f"/{TOKEN}/day/{_get_next(SAT)}")
    labels = get_default_state(_get_today()).labels
    pants = next(
        label
        for _, label, kind in _get_drawn_garments(page)
        if kind == "Pants"
    )
    assert pants in {
        label
        for key, label in labels.items()
        if key.startswith("pants.")
    }


@pytest.mark.parametrize("high", [None, DEFAULT_COLD_THRESHOLD - 10])
def test_the_outfit_reads_shirt_pants_shoes_then_outerwear(
    state_path: Path, high: float | None
) -> None:
    saturday = _get_next(SAT)
    client = web.app(
        state_path,
        TOKEN,
        fetch_weather=lambda: {} if high is None else {saturday: high},
    ).test_client()
    page = _get_text(client, f"/{TOKEN}/day/{saturday}")
    kinds = [
        kind.partition(" · ")[0]
        for _, _, kind in _get_drawn_garments(page)
    ]
    assert kinds[:3] == ["Shirt", "Pants", "Shoes"]
    assert kinds[3] in {"Sweater", "Jacket"}
    assert len(kinds) == 4
    reply = client.get(f"/{TOKEN}/day/{saturday}.json")
    assert reply.json is not None
    assert [
        item["garment"].title() for item in reply.json["outfit"]
    ] == kinds


def test_the_week_strip_links_each_day_of_the_week(
    client: FlaskClient, state_path: Path
) -> None:
    # A Tuesday made an Office Day, which no Holiday can undo, so one
    # of the strip's H turns to O.
    day = _get_next(SAT) + timedelta(days=11)
    monday = day - timedelta(days=day.weekday())
    tuesday = monday + timedelta(days=1)
    state = record_override(
        get_default_state(_get_today()), tuesday, DayType.OFFICE
    )
    write_state(state_path, state)
    page = _get_text(client, f"/{TOKEN}/day/{day}")
    strip = _get_week_strip(page)
    assert strip == [
        (
            f"/{TOKEN}/day/{on}",
            f"{on:%a}"[0],
            str(on.day),
            str(get_day_type(state, on))[0].upper(),
        )
        for on in (
            monday + timedelta(days=offset) for offset in range(7)
        )
    ]
    assert strip[1][3] == "O"


def test_a_weeks_strip_is_the_same_from_any_of_its_days(
    client: FlaskClient,
) -> None:
    sunday = _get_next(SAT) + timedelta(days=8)
    monday = sunday - timedelta(days=6)
    assert _get_week_strip(
        _get_text(client, f"/{TOKEN}/day/{sunday}")
    ) == _get_week_strip(_get_text(client, f"/{TOKEN}/day/{monday}"))


def test_the_outfit_is_one_block_apart_from_the_strip_and_title(
    client: FlaskClient,
) -> None:
    # A past date with no forecast, so a caption shows and the
    # Outerwear is worn only if it's cold, under its own heading.
    day = _get_today() - timedelta(days=1)
    page = _get_text(client, f"/{TOKEN}/day/{day}")
    block = _get_element(page, '<div class="outfit"')
    worn_garments, if_cold_garments = _split_if_cold(page)
    assert if_cold_garments
    assert _split_if_cold(block) == (worn_garments, if_cold_garments)
    assert 'aria-label="Week"' not in block
    assert "<h1" not in block
    assert "not what was worn" not in block


def test_today_links_back_only_from_another_day(
    client: FlaskClient,
) -> None:
    today_link = re.compile(
        f'<a [^>]*href="/{TOKEN}/"[^>]*>\\s*Today\\s*</a>'
    )
    assert not today_link.search(_get_text(client, f"/{TOKEN}/"))
    assert not today_link.search(
        _get_text(client, f"/{TOKEN}/day/{_get_today()}")
    )
    tomorrow = _get_today() + timedelta(days=1)
    assert today_link.search(
        _get_text(client, f"/{TOKEN}/day/{tomorrow}")
    )


def test_the_menu_posts_to_the_day_routes(
    client: FlaskClient, state_path: Path
) -> None:
    today = _get_today()
    write_state(
        state_path,
        record_override(get_default_state(today), today, DayType.HOME),
    )
    page = _get_text(client, f"/{TOKEN}/")
    assert f'action="/{TOKEN}/day/{today}/day-type"' in page
    assert f'action="/{TOKEN}/day/{today}/shirt"' in page
    assert f'action="/{TOKEN}/outerwear"' in page


def test_the_date_picker_lands_on_the_day_page(
    client: FlaskClient,
) -> None:
    page = _get_text(client, f"/{TOKEN}/")
    assert f'<form action="/{TOKEN}/day">' in page
    assert 'type="date" name="on"' in page
    reply = client.get(f"/{TOKEN}/day?on=2026-12-25")
    assert reply.status_code == 303
    assert reply.headers["Location"] == f"/{TOKEN}/day/2026-12-25"


@pytest.mark.parametrize(
    "text",
    ["the-21st", "20260928", "2026-W40-1", "0001-01-01", "9999-12-31"],
)
def test_a_date_without_a_day_page_is_not_found(
    client: FlaskClient, text: str
) -> None:
    # Only YYYY-MM-DD, so every date has one URL, and only dates whose
    # Week and neighbors the calendar can hold.
    assert client.get(f"/{TOKEN}/day/{text}").status_code == 404
    picked = client.get(
        f"/{TOKEN}/day?on={text}", follow_redirects=True
    )
    assert picked.status_code == 404


def test_the_picker_with_no_date_is_not_found(
    client: FlaskClient,
) -> None:
    assert client.get(f"/{TOKEN}/day?on=").status_code == 404


def test_every_page_links_to_day_closet_and_settings(
    client: FlaskClient,
) -> None:
    page = _get_text(client, f"/{TOKEN}/")
    assert f'href="/{TOKEN}/"' in page
    assert f'href="/{TOKEN}/closet"' in page
    assert f'href="/{TOKEN}/settings"' in page


@pytest.mark.parametrize(
    ("record_today", "title"),
    [
        (lambda state: state, "Home Day"),
        (
            lambda state: dataclasses.replace(
                state, office_weekdays=(0, 1, 2)
            ),
            "Office Day",
        ),
        (
            lambda state: record_override(
                state, PINNED_TODAY, DayType.OFFICE
            ),
            "Office Day",
        ),
    ],
)
@pytest.mark.parametrize("url", ["/", "/closet", "/settings"])
def test_each_segment_carries_the_title_of_the_page_it_opens(
    pinned_client: FlaskClient,
    state_path: Path,
    record_today: Callable[[State], State],
    title: str,
    url: str,
) -> None:
    # The pinned today is a Tuesday: a Home Day unless the Office
    # Weekdays or an Override make it an Office Day.
    write_state(
        state_path, record_today(get_default_state(PINNED_TODAY))
    )
    page = _get_text(pinned_client, f"/{TOKEN}{url}")
    assert _get_segments(page) == [
        (f"/{TOKEN}/", title, "Day"),
        (f"/{TOKEN}/closet", "Closet", "Closet"),
        (f"/{TOKEN}/settings", "Settings", "Settings"),
    ]


def test_a_past_date_says_what_it_shows(client: FlaskClient) -> None:
    day = _get_today() - timedelta(days=1)
    assert "not what was worn" in _get_text(
        client, f"/{TOKEN}/day/{day}"
    )


def test_today_is_not_the_past(client: FlaskClient) -> None:
    assert "not what was worn" not in _get_text(client, f"/{TOKEN}/")


def test_an_unavoidable_repeat_is_called_out(
    client: FlaskClient, state_path: Path
) -> None:
    # A fourth Office Day in the Week, which the three office sweaters
    # and their Fallbacks cannot cover however the Week is walked. The
    # Office Weekdays are recorded too, so a Holiday can't take one.
    saturday = _get_next(SAT)
    state = get_default_state(_get_today())
    monday = saturday - timedelta(days=SAT)
    office_days = [
        *(
            monday + timedelta(days=weekday)
            for weekday in state.office_weekdays
        ),
        saturday,
    ]
    write_state(
        state_path,
        reduce(
            lambda recorded, on: record_override(
                recorded, on, DayType.OFFICE
            ),
            office_days,
            state,
        ),
    )
    page = _get_text(client, f"/{TOKEN}/day/{saturday}")
    assert "already worn this week" in page


def test_an_unknown_forecast_puts_the_outerwear_if_its_cold(
    client: FlaskClient,
) -> None:
    page = _get_text(client, f"/{TOKEN}/")
    worn_garments, if_cold_garments = _split_if_cold(page)
    assert [kind for _, _, kind in worn_garments] == [
        "Shirt",
        "Pants",
        "Shoes",
    ]
    assert [kind for _, _, kind in if_cold_garments] in (
        ["Sweater · no forecast yet"],
        ["Jacket · no forecast yet"],
    )
    assert ", if it's cold" not in page


def test_a_cold_day_names_its_outerwear_plainly(
    state_path: Path,
) -> None:
    today = _get_today()
    client = web.app(
        state_path,
        TOKEN,
        fetch_weather=lambda: {today: DEFAULT_COLD_THRESHOLD - 10},
    ).test_client()
    page = _get_text(client, f"/{TOKEN}/")
    worn_garments, if_cold_garments = _split_if_cold(page)
    assert "If it's cold" not in page
    assert not if_cold_garments
    assert worn_garments[3][2] in {"Sweater", "Jacket"}


def test_a_warm_day_names_no_outerwear(state_path: Path) -> None:
    today = _get_today()
    client = web.app(
        state_path,
        TOKEN,
        fetch_weather=lambda: {today: DEFAULT_COLD_THRESHOLD},
    ).test_client()
    page = _get_text(client, f"/{TOKEN}/")
    assert "Sweater" not in page
    assert "Jacket" not in page


def test_each_garment_is_drawn_in_its_color(
    client: FlaskClient,
) -> None:
    page = _get_text(client, f"/{TOKEN}/day/{_get_next(SAT)}")
    rows = _get_drawn_garments(page)
    assert {kind for _, _, kind in rows} >= {"Shirt", "Pants", "Shoes"}
    assert all(
        COLORS[label][0] in _get_fills(art) for art, label, _ in rows
    )


def test_a_striped_shirt_is_drawn_with_stripes_in_its_stripe_color(
    client: FlaskClient,
) -> None:
    saturday = _get_next(SAT)
    _post_text(
        client,
        f"/{TOKEN}/day/{saturday}/day-type",
        {"day_type": "office"},
    )
    page = _post_text(
        client, f"/{TOKEN}/day/{saturday}/shirt", {"shirt": "Striped"}
    )
    shirt = next(
        art
        for art, label, kind in _get_drawn_garments(page)
        if (label, kind) == ("Striped", "Shirt")
    )
    color, stripe_color = COLORS["Striped"]
    assert stripe_color is not None
    assert {color, stripe_color} <= set(_get_fills(shirt))


def test_the_page_draws_art_with_only_lines_and_curves(
    client: FlaskClient,
) -> None:
    page = _get_text(client, f"/{TOKEN}/")
    paths = re.findall(r' d="([^"]*)"', page)
    assert paths
    assert all(re.fullmatch(r"[MLQCZ\d. -]+", path) for path in paths)
    assert "dasharray" not in page


def test_the_page_and_the_widget_draw_the_same_art(
    client: FlaskClient,
) -> None:
    saturday = _get_next(SAT)
    page = _get_text(client, f"/{TOKEN}/day/{saturday}")
    reply = client.get(f"/{TOKEN}/day/{saturday}.json")
    assert reply.json is not None
    assert [art for art, _, _ in _get_drawn_garments(page)] == [
        item["art"] for item in reply.json["outfit"]
    ]


def test_an_office_shirt_is_cut_unlike_a_home_shirt(
    client: FlaskClient, state_path: Path
) -> None:
    _dress_all_in(state_path, "#9cc3e6")
    saturday = _get_next(SAT)
    home = _get_shirt_art(client, saturday)
    _post_text(
        client,
        f"/{TOKEN}/day/{saturday}/day-type",
        {"day_type": "office"},
    )
    office = _get_shirt_art(client, saturday)
    assert "#9cc3e6" in _get_fills(home)
    assert "#9cc3e6" in _get_fills(office)
    assert office != home


@pytest.mark.parametrize(
    ("label", "outline_is_lighter"),
    [("White", False), ("Tan", False), ("Black", True)],
)
def test_a_dark_color_is_outlined_lighter_and_any_other_darker(
    client: FlaskClient,
    state_path: Path,
    label: str,
    outline_is_lighter: bool,  # noqa: FBT001
) -> None:
    color = COLORS[label][0]
    _dress_all_in(state_path, color)
    art = _get_shirt_art(client, _get_next(SAT))
    body = next(
        layer["d"] for layer in art if layer.get("fill") == color
    )
    outline = next(
        layer["stroke"]
        for layer in art
        if "stroke" in layer and layer["d"] == body
    )
    assert (_get_brightness(outline) > _get_brightness(color)) is (
        outline_is_lighter
    )


@pytest.mark.parametrize(
    "url",
    [
        "/",
        "/wrong/",
        f"/{TOKEN}x/",
        "/wrong/day/2026-09-28",
        "/wrong/day/2026-09-28.json",
        "/é/",
    ],
)
def test_a_wrong_token_is_a_plain_404(
    client: FlaskClient, url: str
) -> None:
    reply = client.get(url)
    assert reply.status_code == 404
    assert "Shirt" not in reply.get_data(as_text=True)


@pytest.mark.parametrize(
    "url",
    [
        f"/{TOKEN}/",
        f"/{TOKEN}/day/2026-09-28",
        f"/{TOKEN}/day/2026-09-28.json",
        "/wrong/",
    ],
)
def test_every_response_is_uncached(
    client: FlaskClient, url: str
) -> None:
    assert client.get(url).headers["Cache-Control"] == "no-store"


def test_an_unreadable_state_is_a_500_with_the_message_and_nav(
    client: FlaskClient, state_path: Path
) -> None:
    state_path.write_text('{"overrides": {"x": "gala"}}')
    reply = client.get(f"/{TOKEN}/")
    assert reply.status_code == 500
    assert reply.headers["Cache-Control"] == "no-store"
    page = reply.get_data(as_text=True)
    assert "state file" in page
    assert f'href="/{TOKEN}/closet"' in page


def test_the_widget_json_answers_for_its_date(
    client: FlaskClient,
) -> None:
    saturday = _get_next(SAT)
    reply = client.get(f"/{TOKEN}/day/{saturday}.json")
    assert reply.status_code == 200
    assert reply.json is not None
    assert reply.json["date"] == saturday.isoformat()
    assert reply.json["day"] == "home"
    outfit = reply.json["outfit"]
    assert [item["garment"] for item in outfit][:3] == [
        "shirt",
        "pants",
        "shoes",
    ]
    assert outfit[3]["garment"] in {"sweater", "jacket"}
    for item in outfit:
        assert set(item) - {"if_cold"} == {"garment", "label", "art"}
        assert item["label"] in COLORS
        assert COLORS[item["label"]][0] in _get_fills(item["art"])


def test_art_is_drawn_with_only_lines_and_curves(
    client: FlaskClient,
) -> None:
    reply = client.get(f"/{TOKEN}/day/{_get_next(SAT)}.json")
    assert reply.json is not None
    layers = [
        layer for item in reply.json["outfit"] for layer in item["art"]
    ]
    assert layers
    assert all(
        re.fullmatch(r"[MLQCZ\d. -]+", layer["d"]) for layer in layers
    )
    assert all(
        ("fill" in layer) != ("stroke" in layer) for layer in layers
    )
    assert all(
        isinstance(layer["width"], int | float)
        for layer in layers
        if "stroke" in layer
    )


def test_the_widget_json_draws_a_striped_shirts_stripes(
    client: FlaskClient,
) -> None:
    saturday = _get_next(SAT)
    _post_text(
        client,
        f"/{TOKEN}/day/{saturday}/day-type",
        {"day_type": "office"},
    )
    _post_text(
        client, f"/{TOKEN}/day/{saturday}/shirt", {"shirt": "Striped"}
    )
    reply = client.get(f"/{TOKEN}/day/{saturday}.json")
    assert reply.json is not None
    assert reply.json["day"] == "office"
    shirt = reply.json["outfit"][0]
    assert shirt["label"] == "Striped"
    color, stripe_color = COLORS["Striped"]
    assert stripe_color is not None
    assert {color, stripe_color} <= set(_get_fills(shirt["art"]))


def test_the_widget_json_marks_outerwear_if_cold_when_unknown(
    client: FlaskClient,
) -> None:
    reply = client.get(f"/{TOKEN}/day/{_get_today()}.json")
    assert reply.json is not None
    assert [
        item["garment"]
        for item in reply.json["outfit"]
        if "if_cold" in item
    ] == [reply.json["outfit"][3]["garment"]]
    assert reply.json["outfit"][3]["if_cold"] is True


def test_the_widget_json_on_a_cold_day_has_no_if_cold(
    state_path: Path,
) -> None:
    today = _get_today()
    client = web.app(
        state_path,
        TOKEN,
        fetch_weather=lambda: {today: DEFAULT_COLD_THRESHOLD - 10},
    ).test_client()
    reply = client.get(f"/{TOKEN}/day/{today}.json")
    assert reply.json is not None
    assert len(reply.json["outfit"]) == 4
    assert not any("if_cold" in item for item in reply.json["outfit"])


def test_the_widget_json_for_an_unreadable_state_is_an_error(
    client: FlaskClient, state_path: Path
) -> None:
    state_path.write_text('{"overrides": {"x": "gala"}}')
    reply = client.get(f"/{TOKEN}/day/{_get_today()}.json")
    assert reply.status_code == 500
    assert reply.json is not None
    assert set(reply.json) == {"error"}
    assert "state file" in reply.json["error"]


def test_the_widget_json_for_no_date_is_not_found(
    client: FlaskClient,
) -> None:
    assert client.get(f"/{TOKEN}/day/20260928.json").status_code == 404


def test_a_fresh_install_answers_and_writes_nothing(
    tmp_path: Path,
) -> None:
    absent = tmp_path / "absent" / "state.json"
    client = web.app(absent, TOKEN, fetch_weather=dict).test_client()
    assert "Shirt" in _get_text(client, f"/{TOKEN}/")
    assert not absent.parent.exists()


def test_the_day_type_button_offers_the_other_type(
    client: FlaskClient,
) -> None:
    page = _get_text(client, f"/{TOKEN}/day/{_get_next(SAT)}")
    assert "Make this an Office Day" in page
    assert "Make this a Home Day" not in page


def test_a_day_type_write_answers_303_with_the_notice(
    client: FlaskClient, state_path: Path
) -> None:
    saturday = _get_next(SAT)
    reply = client.post(
        f"/{TOKEN}/day/{saturday}/day-type", data={"day_type": "office"}
    )
    assert reply.status_code == 303
    location = urlsplit(reply.headers["Location"])
    assert location.path == f"/{TOKEN}/day/{saturday}"
    assert parse_qs(location.query)["notice"] == [
        "Recorded: an Office Day"
    ]
    page = _get_text(client, reply.headers["Location"])
    assert "Recorded: an Office Day" in page
    assert "Make this a Home Day" in page
    assert state_path.exists()


def test_a_write_already_the_case_says_so_and_writes_nothing(
    client: FlaskClient, state_path: Path
) -> None:
    page = _post_text(
        client,
        f"/{TOKEN}/day/{_get_next(SAT)}/day-type",
        {"day_type": "home"},
    )
    assert "Already: a Home Day" in page
    assert not state_path.exists()


def test_an_unknown_day_type_is_a_bad_request(
    client: FlaskClient,
) -> None:
    reply = client.post(
        f"/{TOKEN}/day/{_get_next(SAT)}/day-type",
        data={"day_type": "gala"},
    )
    assert reply.status_code == 400


@pytest.mark.parametrize("closet", ["home", "office"])
def test_the_shirt_sheet_offers_the_dates_closets_shirts(
    client: FlaskClient, closet: str
) -> None:
    saturday = _get_next(SAT)
    page = _post_text(
        client,
        f"/{TOKEN}/day/{saturday}/day-type",
        {"day_type": closet},
    )
    labels = get_default_state(_get_today()).labels
    shirt = _get_drawn_garments(page)[0][1]
    assert _get_shirt_choices(page) == [
        (label, label == shirt)
        for key, label in labels.items()
        if key.startswith(f"{closet}.shirt.")
    ]
    assert "<select" not in page


def test_wearing_a_different_shirt_resets_to_it(
    client: FlaskClient,
) -> None:
    saturday = _get_next(SAT)
    labels = get_default_state(_get_today()).labels
    shirts = [
        label
        for key, label in labels.items()
        if key.startswith("home.shirt.")
    ]
    page = _get_text(client, f"/{TOKEN}/day/{saturday}")
    worn_shirt = _get_drawn_garments(page)[0][1]
    other = next(shirt for shirt in shirts if shirt != worn_shirt)
    page = _post_text(
        client, f"/{TOKEN}/day/{saturday}/shirt", {"shirt": other}
    )
    assert f"Recorded: the Shirt Rotation reset to {other}" in page
    assert _get_drawn_garments(page)[0][1] == other
    assert (other, True) in _get_shirt_choices(page)


def test_a_refusal_reshows_the_page_with_the_message(
    client: FlaskClient, state_path: Path
) -> None:
    saturday = _get_next(SAT)
    reply = client.post(
        f"/{TOKEN}/day/{saturday}/shirt", data={"shirt": "Nope"}
    )
    assert reply.status_code == 422
    page = html.unescape(reply.get_data(as_text=True))
    assert "no home shirt named 'Nope'" in page
    assert _get_shown_date(page) == saturday
    assert not state_path.exists()


def test_the_outerwear_switch_shows_only_today_on_a_home_day(
    client: FlaskClient, state_path: Path
) -> None:
    today = _get_today()
    tomorrow = today + timedelta(days=1)
    home = record_override(
        record_override(get_default_state(today), today, DayType.HOME),
        tomorrow,
        DayType.HOME,
    )
    write_state(state_path, home)
    assert "Switch to the" in _get_text(client, f"/{TOKEN}/")
    assert "Switch to the" not in _get_text(
        client, f"/{TOKEN}/day/{tomorrow}"
    )
    write_state(
        state_path, record_override(home, today, DayType.OFFICE)
    )
    assert "Switch to the" not in _get_text(client, f"/{TOKEN}/")


def test_a_warm_day_offers_no_outerwear_switch(
    state_path: Path,
) -> None:
    today = _get_today()
    write_state(
        state_path,
        record_override(get_default_state(today), today, DayType.HOME),
    )
    client = web.app(
        state_path,
        TOKEN,
        fetch_weather=lambda: {today: DEFAULT_COLD_THRESHOLD},
    ).test_client()
    assert "Switch to the" not in _get_text(client, f"/{TOKEN}/")


def test_switching_outerwear_offers_the_other_kind(
    client: FlaskClient, state_path: Path
) -> None:
    today = _get_today()
    write_state(
        state_path,
        record_override(get_default_state(today), today, DayType.HOME),
    )
    before = _get_text(client, f"/{TOKEN}/")
    reply = client.post(f"/{TOKEN}/outerwear")
    assert reply.status_code == 303
    assert urlsplit(reply.headers["Location"]).path == f"/{TOKEN}/"
    after = _get_text(client, reply.headers["Location"])
    assert "Recorded: the Home Outerwear Rotation reset" in after
    assert ("Switch to the jacket" in before) == (
        "Switch to the sweater" in after
    )


def test_settings_check_the_chips_of_the_office_weekdays(
    client: FlaskClient,
) -> None:
    page = _get_text(client, f"/{TOKEN}/settings")
    chips = re.findall(
        r'<input type="checkbox" name="weekday"[^>]*>', page
    )
    assert len(chips) == 7
    assert [
        _get_fields(chip)["value"]
        for chip in chips
        if "checked" in chip
    ] == ["0", "2", "4"]
    assert "Changing these keeps every Rotation where it is." in page


def test_settings_hold_only_the_two_cards(client: FlaskClient) -> None:
    page = _get_text(client, f"/{TOKEN}/settings")
    assert re.findall(r"<h2>(.*?)</h2>", page) == [
        "Office Weekdays",
        "Cold Threshold",
    ]
    assert re.findall(r'<form [^>]*action="([^"]+)"', page) == [
        f"/{TOKEN}/settings/office-weekdays",
        f"/{TOKEN}/settings/cold-threshold",
    ]


def test_setting_office_weekdays_records_them(
    client: FlaskClient, state_path: Path
) -> None:
    reply = client.post(
        f"/{TOKEN}/settings/office-weekdays",
        data={"weekday": ["1", "3", "5"]},
    )
    assert reply.status_code == 303
    location = urlsplit(reply.headers["Location"])
    assert location.path == f"/{TOKEN}/settings"
    after = _get_text(client, reply.headers["Location"])
    assert "Recorded: Office Weekdays Tue, Thu, Sat" in after
    assert state_path.exists()


def test_restating_office_weekdays_is_already_the_case(
    client: FlaskClient, state_path: Path
) -> None:
    page = _post_text(
        client,
        f"/{TOKEN}/settings/office-weekdays",
        {"weekday": ["0", "2", "4"]},
    )
    assert "Already: Office Weekdays Mon, Wed, Fri" in page
    assert not state_path.exists()


def test_other_than_three_weekdays_is_refused(
    client: FlaskClient, state_path: Path
) -> None:
    reply = client.post(
        f"/{TOKEN}/settings/office-weekdays", data={"weekday": ["0"]}
    )
    assert reply.status_code == 422
    page = html.unescape(reply.get_data(as_text=True))
    assert "exactly 3 different days" in page
    assert page.count('type="checkbox"') == 7
    assert not state_path.exists()


def test_settings_show_the_cold_threshold_on_a_stepper(
    client: FlaskClient,
) -> None:
    fields = _get_fields(_get_threshold_input(client))
    assert fields["value"] == f"{DEFAULT_COLD_THRESHOLD}"
    assert (fields["min"], fields["max"], fields["step"]) == (
        "0",
        "100",
        "1",
    )


def test_a_stored_decimal_threshold_shows_rounded(
    client: FlaskClient, state_path: Path
) -> None:
    _store_threshold(state_path, 52.5)
    assert _get_fields(_get_threshold_input(client))["value"] == "53"
    assert read_state(state_path, _get_today()).cold_threshold == 52.5


def test_setting_the_cold_threshold_records_it(
    client: FlaskClient, state_path: Path
) -> None:
    page = _post_text(
        client, f"/{TOKEN}/settings/cold-threshold", {"threshold": "42"}
    )
    assert "Recorded: a Cold Threshold of 42°F" in page
    assert 'name="threshold" value="42"' in page
    assert read_state(state_path, _get_today()).cold_threshold == 42


def test_restating_the_cold_threshold_is_already_the_case(
    client: FlaskClient, state_path: Path
) -> None:
    page = _post_text(
        client,
        f"/{TOKEN}/settings/cold-threshold",
        {"threshold": f"{DEFAULT_COLD_THRESHOLD}"},
    )
    assert (
        f"Already: a Cold Threshold of {DEFAULT_COLD_THRESHOLD:g}°F"
        in page
    )
    assert not state_path.exists()


@pytest.mark.parametrize("threshold", ["101", "52.5", "-1", "nan"])
def test_a_threshold_outside_whole_degrees_0_to_100_is_refused(
    client: FlaskClient, state_path: Path, threshold: str
) -> None:
    _store_threshold(state_path, 52.5)
    reply = client.post(
        f"/{TOKEN}/settings/cold-threshold",
        data={"threshold": threshold},
    )
    assert reply.status_code == 422
    assert "a whole degree from 0 to 100" in reply.get_data(
        as_text=True
    )
    assert read_state(state_path, _get_today()).cold_threshold == 52.5


@pytest.mark.parametrize(
    ("url", "data"),
    [
        ("office-weekdays", {"weekday": ["mon", "1", "2"]}),
        ("office-weekdays", {"weekday": ["7", "1", "2"]}),
        ("cold-threshold", {"threshold": "warm"}),
    ],
)
def test_a_setting_that_is_no_number_is_a_bad_request(
    client: FlaskClient, url: str, data: dict[str, object]
) -> None:
    reply = client.post(f"/{TOKEN}/settings/{url}", data=data)
    assert reply.status_code == 400


def test_the_closet_shows_home_shirts_then_office_shirts(
    pinned_client: FlaskClient,
) -> None:
    page = _get_text(pinned_client, f"/{TOKEN}/closet")
    assert [key for key, _, _ in _get_shirt_tiles(page)] == SHIRT_KEYS
    assert _get_grid_names(page) == [
        "Home Shirts",
        "Office Shirts",
        "Pants",
        "Home sweaters",
        "Home jackets",
        "Home shoes",
        "Office sweaters",
        "Office shoes",
    ]


def test_each_shirt_says_when_it_is_next_due(
    pinned_client: FlaskClient,
) -> None:
    # Pinned to Tuesday 13 October 2026, a Home Day: Monday the 19th
    # is six days on, and Tuesday the 20th seven.
    page = _get_text(pinned_client, f"/{TOKEN}/closet")
    due_texts = {
        key: (label, due_text)
        for key, label, due_text in _get_shirt_tiles(page)
    }
    assert [due_texts[f"home.shirt.{place}"] for place in range(5)] == [
        ("White", "Today"),
        ("Brown", "Thursday"),
        ("Dark Green", "Saturday"),
        ("Black", "Sunday"),
        ("Purple", "Tue 20 Oct"),
    ]
    assert [
        due_texts[f"office.shirt.{place}"] for place in range(4)
    ] == [
        ("White", "Tomorrow"),
        ("Black", "Friday"),
        ("Light Blue", "Monday"),
        ("Striped", "Wed 21 Oct"),
    ]


@pytest.mark.parametrize("key", SHIRT_KEYS)
def test_each_shirt_sheet_links_to_the_day_it_is_next_due(
    pinned_client: FlaskClient, key: str
) -> None:
    page = _get_text(pinned_client, f"/{TOKEN}/closet")
    due = _get_pinned_due_date(key)
    due_text = next(
        due_text
        for tile_key, _, due_text in _get_shirt_tiles(page)
        if tile_key == key
    )
    assert (
        f'href="/{TOKEN}/day/{due}">Next due {due_text} ›</a>'  # noqa: RUF001
        in _get_sheet(page, f"shirt-{key}")
    )


@pytest.mark.parametrize("key", SHIRT_KEYS)
def test_each_shirt_sheet_holds_its_outfit_on_that_date(
    pinned_client: FlaskClient, key: str
) -> None:
    page = _get_text(pinned_client, f"/{TOKEN}/closet")
    outfit = answer(
        get_default_state(PINNED_TODAY), _get_pinned_due_date(key), {}
    ).outfit
    worn, if_cold = _split_if_cold(_get_sheet(page, f"shirt-{key}"))
    assert [(label, kind) for _, label, kind in worn] == [
        (outfit.pants.label, "Pants"),
        (outfit.shoes.label, "Shoes"),
    ]
    outerwear = outfit.sweater or outfit.jacket
    assert outerwear is not None
    assert [label for _, label, _ in if_cold] == [outerwear.label]
    assert all(
        kind.endswith(" · no forecast yet") for _, _, kind in if_cold
    )


def test_the_forecast_is_fetched_once_in_half_an_hour(
    state_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fetch_weather = Mock(return_value={PINNED_TODAY: 60.0})
    client = web.app(state_path, TOKEN, fetch_weather).test_client()
    _pin_clock(monkeypatch, time(12))
    _get_text(client, f"/{TOKEN}/day/{PINNED_TODAY}")
    assert client.get(f"/{TOKEN}/day/{PINNED_TODAY}.json").json
    _pin_clock(monkeypatch, time(12, 29))
    _get_text(client, f"/{TOKEN}/")
    assert fetch_weather.call_count == 1
    _pin_clock(monkeypatch, time(12, 31))
    _get_text(client, f"/{TOKEN}/")
    assert fetch_weather.call_count == 2


def test_a_failed_forecast_is_fetched_again_next_time(
    state_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fetch_weather = Mock(return_value={})
    client = web.app(state_path, TOKEN, fetch_weather).test_client()
    _pin_clock(monkeypatch, time(12))
    _get_text(client, f"/{TOKEN}/")
    _get_text(client, f"/{TOKEN}/")
    assert fetch_weather.call_count == 2


def test_the_closet_fetches_no_forecast(state_path: Path) -> None:
    # Each sheet's Outerwear is under "If it's cold" whatever the
    # weather, so the Closet never waits on the forecast.
    def fetch_weather() -> dict[date, float]:
        pytest.fail("the Closet fetched the forecast")

    client = web.app(
        state_path, TOKEN, fetch_weather=fetch_weather
    ).test_client()
    page = _get_text(client, f"/{TOKEN}/closet")
    assert "If it's cold" in _get_sheet(page, "shirt-office.shirt.0")


def test_a_shirt_not_due_this_year_says_so_and_wears_nothing(
    state_path: Path, pinned_client: FlaskClient
) -> None:
    year = (PINNED_TODAY + timedelta(days=days) for days in range(366))
    write_state(
        state_path,
        dataclasses.replace(
            get_default_state(PINNED_TODAY),
            overrides=dict.fromkeys(year, DayType.HOME),
        ),
    )
    page = _get_text(pinned_client, f"/{TOKEN}/closet")
    assert {
        due_text
        for key, _, due_text in _get_shirt_tiles(page)
        if key.startswith("office.")
    } == {"Not due this year"}
    sheet = _get_sheet(page, "shirt-office.shirt.0")
    assert "Next due" not in sheet
    assert "Worn with" not in sheet


def test_swap_offers_only_shirts_sharing_pants(
    client: FlaskClient,
) -> None:
    sheet = _get_sheet(
        _get_text(client, f"/{TOKEN}/closet"), "shirt-office.shirt.0"
    )
    assert f'action="/{TOKEN}/closet/office/swap"' in sheet
    assert 'name="first" value="White"' in sheet
    assert re.findall(r'name="second" value="([^"]+)"', sheet) == [
        "Striped"
    ]


def test_a_shirt_sharing_no_pants_says_it_cannot_swap(
    client: FlaskClient,
) -> None:
    # The Office Light Blue is the only Shirt on the Black Pants.
    sheet = _get_sheet(
        _get_text(client, f"/{TOKEN}/closet"), "shirt-office.shirt.2"
    )
    assert "No other Shirt shares its Pants, so it can't Swap." in sheet
    assert 'name="second"' not in sheet


def test_a_swap_carries_colors_with_labels(
    client: FlaskClient, state_path: Path
) -> None:
    page = _post_text(
        client,
        f"/{TOKEN}/closet/office/swap",
        {"first": "White", "second": "Striped"},
    )
    assert "Recorded: the Office White and Striped Shirts swapped" in (
        page
    )
    state = read_state(state_path, _get_today())
    colors = get_default_state(_get_today()).colors
    assert (
        state.labels["office.shirt.0"],
        state.colors["office.shirt.0"],
    ) == (
        "Striped",
        colors["office.shirt.3"],
    )
    assert (
        state.labels["office.shirt.3"],
        state.colors["office.shirt.3"],
    ) == (
        "White",
        colors["office.shirt.0"],
    )


def test_a_refused_swap_reshows_the_closet_with_the_message(
    client: FlaskClient, state_path: Path
) -> None:
    reply = client.post(
        f"/{TOKEN}/closet/office/swap",
        data={"first": "White", "second": "Black"},
    )
    assert reply.status_code == 422
    page = html.unescape(reply.get_data(as_text=True))
    assert "do not share pants" in page
    assert "Office Shirts" in page
    assert not state_path.exists()


def test_an_unknown_closet_is_not_found(client: FlaskClient) -> None:
    reply = client.post(
        f"/{TOKEN}/closet/gala/swap",
        data={"first": "White", "second": "Striped"},
    )
    assert reply.status_code == 404


@pytest.mark.parametrize("key", build_default_labels())
def test_every_garment_has_a_prefilled_replace_form(
    client: FlaskClient, key: str
) -> None:
    page = _get_text(client, f"/{TOKEN}/closet")
    assert page.count(f'id="replace-{key}"') == 1
    form = _get_replace_form(page, key)
    color, stripe_color = build_default_colors()[key]
    assert form["action"] == f"/{TOKEN}/closet/{key}"
    assert form["label"] == build_default_labels()[key]
    assert form["color"] == color
    assert form["striped"] == (stripe_color is not None)
    assert form["stripe_color"] == (stripe_color or color)
    assert form["button"] == f"Replace the {key.split('.')[-2].title()}"


def test_each_garment_tile_opens_its_replace_sheet(
    client: FlaskClient,
) -> None:
    page = _get_text(client, f"/{TOKEN}/closet")
    tiles = page[: page.index('class="sheet"')]
    assert re.findall(r'popovertarget="replace-([^"]+)"', tiles) == [
        "pants.0",
        "pants.1",
        "pants.2",
        "home.sweater.0",
        "home.sweater.1",
        "home.sweater.2",
        "home.jacket.0",
        "home.jacket.1",
        "home.shoes.0",
        "home.shoes.1",
        "office.sweater.0",
        "office.sweater.1",
        "office.sweater.2",
        "office.shoes.0",
        "office.shoes.1",
        "office.shoes.2",
    ]
    assert 'popovertarget="replace-office.shirt.3"' in _get_sheet(
        page, "shirt-office.shirt.3"
    )


def test_each_garment_is_drawn_once_and_shown_wherever_it_hangs(
    client: FlaskClient,
) -> None:
    page = _get_text(client, f"/{TOKEN}/closet")
    symbols = re.findall(r'<symbol id="art-([^"]+)"', page)
    assert sorted(symbols) == sorted(build_default_labels())
    assert COLORS["Striped"][1] in _get_fills(
        _get_symbol_art(page, "office.shirt.3")
    )
    shown = re.findall(r'<use href="#art-([^"]+)"', page)
    assert set(shown) == set(symbols)
    # Its tile, its sheet, its Replace sheet, and the White's Swap.
    assert shown.count("office.shirt.3") == 4


def test_the_replace_art_redraws_from_the_same_layers(
    client: FlaskClient,
) -> None:
    page = _get_text(client, f"/{TOKEN}/closet")
    match = re.search(
        r'<script type="application/json" id="art-templates">(.*?)'
        r"</script>",
        page,
        re.DOTALL,
    )
    assert match is not None
    templates = json.loads(match[1])
    sheet = _get_sheet(page, "replace-office.shirt.3")
    assert '<use href="#art-office.shirt.3"/>' in sheet
    art = _get_symbol_art(page, "office.shirt.3")
    template = templates[
        _get_fields(sheet[sheet.index("<form") :])["data-art"]
    ]
    assert [layer["d"] for layer in template] == [
        layer["d"] for layer in art
    ]
    assert {
        layer.get("fill", layer.get("stroke")) for layer in template
    } == {
        "#000000",
        "color",
        "stripe",
        "tone",
        "button",
    }
    assert COLORS["Striped"][1] in _get_fills(art)


def test_a_replace_records_the_label_and_colors(
    client: FlaskClient, state_path: Path
) -> None:
    reply = _post_replace(
        client,
        "office.shirt.0",
        {
            "label": "Pinstripe",
            "color": "#ffffff",
            "striped": "on",
            "stripe_color": "#000080",
        },
    )
    assert reply.status_code == 303
    location = reply.headers["Location"]
    assert urlsplit(location).path == f"/{TOKEN}/closet"
    page = _get_text(client, location)
    assert (
        "Recorded: the Office White Shirt replaced with Pinstripe"
        in page
    )
    assert _get_replace_form(page, "office.shirt.0")["label"] == (
        "Pinstripe"
    )
    state = read_state(state_path, _get_today())
    assert state.colors["office.shirt.0"] == ("#ffffff", "#000080")


def test_an_unticked_striped_ignores_the_stripe_color(
    client: FlaskClient, state_path: Path
) -> None:
    _post_replace(
        client,
        "office.shirt.3",
        {
            "label": "Plain",
            "color": "#ffffff",
            "stripe_color": "#3c67b4",
        },
    )
    state = read_state(state_path, _get_today())
    assert state.colors["office.shirt.3"] == ("#ffffff", None)


def test_restating_a_garment_is_already_the_case(
    client: FlaskClient, state_path: Path
) -> None:
    reply = _post_replace(
        client, "pants.0", {"label": "Blue", "color": "#3c67b4"}
    )
    page = _get_text(client, reply.headers["Location"])
    assert "Already: the Blue Pants replaced with Blue" in page
    assert not state_path.exists()


@pytest.mark.parametrize(
    ("label", "message"),
    [
        ("St. Patrick", "cannot contain '.'"),
        ("Black", "already has a 'Black'"),
    ],
)
def test_a_refused_replace_reopens_its_sheet_as_posted(
    client: FlaskClient, state_path: Path, label: str, message: str
) -> None:
    reply = _post_replace(
        client,
        "office.shirt.0",
        {
            "label": label,
            "color": "#123456",
            "striped": "on",
            "stripe_color": "#abcdef",
        },
    )
    assert reply.status_code == 422
    page = html.unescape(reply.get_data(as_text=True))
    assert message in page
    assert "Office Shirts" in page
    form = _get_replace_form(page, "office.shirt.0")
    assert (
        form["label"],
        form["color"],
        form["striped"],
        form["stripe_color"],
    ) == (label, "#123456", True, "#abcdef")
    assert re.findall(r'<div id="([^"]+)" [^>]*data-open', page) == [
        "replace-office.shirt.0"
    ]
    preview = _get_sheet(page, "replace-office.shirt.0")
    assert {"#123456", "#abcdef"} <= set(
        _get_fills(
            [
                _parse_layer(path)
                for path in re.findall(
                    r"<path[^>]*>", preview[: preview.index("</svg>")]
                )
            ]
        )
    )
    assert not state_path.exists()


def test_a_color_that_is_no_color_is_a_bad_request(
    client: FlaskClient,
) -> None:
    reply = _post_replace(
        client, "office.shirt.0", {"label": "White", "color": "red"}
    )
    assert reply.status_code == 400


def test_an_unknown_garment_cannot_be_replaced(
    client: FlaskClient,
) -> None:
    for url in (
        f"/{TOKEN}/closet/office.shirt.99",
        f"/{TOKEN}/closet/nothing",
    ):
        reply = client.post(
            url, data={"label": "X", "color": "#ffffff"}
        )
        assert reply.status_code == 404


def test_the_garment_page_is_gone(client: FlaskClient) -> None:
    reply = client.get(f"/{TOKEN}/closet/office.shirt.0")
    assert reply.status_code == 404


def _pin_clock(monkeypatch: pytest.MonkeyPatch, at: time) -> None:
    """Pin the clock to `at` on `PINNED_TODAY` in New York."""

    class Pinned(datetime):
        @classmethod
        def now(cls, tz: tzinfo | None = None) -> Self:
            return cls.combine(PINNED_TODAY, at, TIMEZONE).astimezone(
                tz
            )

    monkeypatch.setattr(web, "datetime", Pinned)


def _get_pinned_due_date(key: str) -> date:
    closet, _, place = key.partition(".shirt.")
    due = get_due_date(
        get_default_state(PINNED_TODAY),
        DayType(closet),
        CLOSETS[DayType(closet)].shirts[int(place)].garment,
        PINNED_TODAY,
    )
    assert due is not None
    return due


def _get_threshold_input(client: FlaskClient) -> str:
    match = re.search(
        r'<input type="number" name="threshold"[^>]*>',
        _get_text(client, f"/{TOKEN}/settings"),
    )
    assert match is not None
    return match[0]


def _store_threshold(state_path: Path, threshold: float) -> None:
    write_state(
        state_path,
        dataclasses.replace(
            get_default_state(_get_today()), cold_threshold=threshold
        ),
    )


def _get_shirt_tiles(page: str) -> list[tuple[str, str, str]]:
    """Each Shirt's tile in order: its key, its Label, its due text."""
    return re.findall(
        r'popovertarget="shirt-([^"]+)">\s*<svg.*?</svg>\s*<b>(.*?)</b>'
        r"\s*<small[^>]*>(.*?)</small>",
        page,
        re.DOTALL,
    )


def _get_grid_names(page: str) -> list[str]:
    return re.findall(
        r"<h2>(.*?)</h2>", page[: page.index('class="sheet"')]
    )


def _get_sheet(page: str, sheet_id: str) -> str:
    """The sheet `sheet_id`, up to the next sheet or the script."""
    match = re.search(
        rf'<div id="{re.escape(sheet_id)}"[^>]*>(.*?)'
        r'(?=<div id="|<script)',
        page,
        re.DOTALL,
    )
    assert match is not None
    return match[0]


def _get_symbol_art(page: str, key: str) -> list[dict[str, Any]]:
    """The layers of the art drawn once for the Garment at `key`."""
    match = re.search(
        rf'<symbol id="art-{re.escape(key)}"[^>]*>(.*?)</symbol>', page
    )
    assert match is not None
    return [
        _parse_layer(path)
        for path in re.findall(r"<path[^>]*>", match[1])
    ]


def _get_replace_form(page: str, key: str) -> dict[str, Any]:
    """What a Garment's Replace sheet posts, and its button's text."""
    sheet = _get_sheet(page, f"replace-{key}")
    inputs = {
        fields["name"]: fields
        for fields in map(
            _get_fields, re.findall(r"<input[^>]*>", sheet)
        )
    }
    button = re.search(r"<button>(.*?)</button>", sheet)
    assert button is not None
    return {
        "action": _get_fields(sheet[sheet.index("<form") :])["action"],
        "label": inputs["label"]["value"],
        "color": inputs["color"]["value"],
        "striped": "checked" in inputs["striped"],
        "stripe_color": inputs["stripe_color"]["value"],
        "button": button[1],
    }


def _get_fields(tag: str) -> dict[str, str]:
    """The attributes of the first tag in `tag`, a bare one as ''."""
    match = re.match(r"\s*<[^>]*>", tag)
    assert match is not None
    return {
        name: value
        for name, _, value in re.findall(
            r'([\w-]+)(="([^"]*)")?', match[0][1:-1]
        )
    }


def _post_replace(
    client: FlaskClient, key: str, data: dict[str, str]
) -> TestResponse:
    page = _get_text(client, f"/{TOKEN}/closet")
    return client.post(
        _get_replace_form(page, key)["action"], data=data
    )


def _post_text(
    client: FlaskClient, url: str, data: dict[str, str | list[str]]
) -> str:
    reply = client.post(url, data=data, follow_redirects=True)
    assert reply.status_code == 200
    return html.unescape(reply.get_data(as_text=True))


def _dress_all_in(state_path: Path, color: str) -> None:
    state = get_default_state(_get_today())
    write_state(
        state_path,
        dataclasses.replace(
            state, colors=dict.fromkeys(state.colors, (color, None))
        ),
    )


def _get_shirt_art(
    client: FlaskClient, on: date
) -> list[dict[str, Any]]:
    reply = client.get(f"/{TOKEN}/day/{on}.json")
    assert reply.json is not None
    return reply.json["outfit"][0]["art"]


def _get_brightness(color: str) -> int:
    return sum(int(color[at : at + 2], 16) for at in (1, 3, 5))


def _get_title(page: str) -> str:
    match = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.DOTALL)
    assert match is not None
    return match[1].strip()


def _get_shown_date(page: str) -> date:
    """Read the date the toolbar's date picker opens on."""
    match = re.search(
        r'<input type="date" name="on" value="([^"]+)"', page
    )
    assert match is not None
    return date.fromisoformat(match[1])


def _get_week_strip(page: str) -> list[tuple[str, ...]]:
    """Each day in the strip: its link, letter, number and O/H."""
    match = re.search(
        r'<nav [^>]*aria-label="Week"[^>]*>(.*?)</nav>', page, re.DOTALL
    )
    assert match is not None
    return [
        (href, *re.sub(r"<[^>]*>", " ", text).split())
        for href, text in re.findall(
            r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>',
            match[1],
            re.DOTALL,
        )
    ]


def _get_segments(page: str) -> list[tuple[str, str, str]]:
    """Each segment: its link, the title it carries, and its text."""
    nav = _get_element(page, '<nav class="segments"')
    return [
        (fields["href"], fields.get("data-title", ""), text)
        for tag, text in re.findall(r"(<a [^>]*>)(.*?)</a>", nav)
        for fields in [_get_fields(tag)]
    ]


def _get_element(page: str, opening: str) -> str:
    """The element whose tag starts with `opening`, closed and all."""
    start = page.index(opening)
    tag_name = re.match(r"<(\w+)", opening)
    assert tag_name is not None
    tags = list(
        re.finditer(rf"<(/?){tag_name[1]}\b[^>]*>", page[start:])
    )
    depths = accumulate(-1 if tag[1] else 1 for tag in tags)
    end = next(
        tag.end()
        for tag, depth in zip(tags, depths, strict=True)
        if depth == 0
    )
    return page[start : start + end]


def _get_shirt_choices(page: str) -> list[tuple[str, bool]]:
    """Each Shirt the sheet offers, and whether it's the one worn."""
    return [
        (
            dict(re.findall(r'([\w-]+)="([^"]*)"', button))["value"],
            "aria-current" in button,
        )
        for button in re.findall(
            r'<button [^>]*name="shirt"[^>]*>', page
        )
    ]


def _split_if_cold(
    page: str,
) -> tuple[list[tuple[list[dict[str, Any]], str, str]], ...]:
    """The rows worn whatever the weather, and those if it's cold."""
    worn, _, if_cold = page.partition("If it's cold")
    return _get_drawn_garments(worn), _get_drawn_garments(if_cold)


def _get_drawn_garments(
    page: str,
) -> list[tuple[list[dict[str, Any]], str, str]]:
    """Each Garment's row: its art's layers, its Label, its kind."""
    return [
        (
            [
                _parse_layer(path)
                for path in re.findall(r"<path[^>]*>", svg)
            ],
            label.strip(),
            kind.strip(),
        )
        for svg, label, kind in re.findall(
            r"<li[^>]*>\s*<svg[^>]*>(.*?)</svg>\s*<div>\s*<b>(.*?)</b>"
            r"\s*<small>(.*?)</small>",
            page,
            re.DOTALL,
        )
    ]


def _parse_layer(path: str) -> dict[str, Any]:
    """Read an SVG `<path>` back as the layer the widget is sent."""
    fields = dict(re.findall(r'([\w-]+)="([^"]*)"', path))
    alpha = fields.get("fill-opacity") or fields.get("stroke-opacity")
    paint = (
        {"fill": fields["fill"]}
        if fields["fill"] != "none"
        else {
            "stroke": fields["stroke"],
            "width": float(fields["stroke-width"]),
        }
    )
    return {
        "d": fields["d"],
        **paint,
        **({"alpha": float(alpha)} if alpha else {}),
    }


def _get_fills(art: list[dict[str, Any]]) -> list[str]:
    return [layer["fill"] for layer in art if "fill" in layer]


def _get_text(client: FlaskClient, url: str) -> str:
    reply = client.get(url)
    assert reply.status_code == 200
    return html.unescape(reply.get_data(as_text=True))


def _get_today() -> date:
    return datetime.now(TIMEZONE).date()


def _get_next(weekday: int) -> date:
    """Return the soonest date after today falling on `weekday`."""
    today = _get_today()
    return today + timedelta(
        days=(weekday - today.weekday() - 1) % 7 + 1
    )


def test_every_page_names_its_home_screen_icon(
    client: FlaskClient,
) -> None:
    page = client.get(f"/{TOKEN}/settings").text
    icon = re.search(r'rel="apple-touch-icon" href="([^"]+)"', page)

    assert icon is not None
    reply = client.get(icon[1])
    assert reply.status_code == 200
    assert reply.mimetype == "image/png"


def test_the_icon_needs_the_token(client: FlaskClient) -> None:
    assert client.get("/nope/apple-touch-icon.png").status_code == 404
