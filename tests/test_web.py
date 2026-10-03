import html
import re
from datetime import UTC, date, datetime, timedelta, tzinfo
from pathlib import Path
from typing import Self
from urllib.parse import parse_qs, urlsplit

import pytest
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from what2wear import web
from what2wear.core import get_due_date, record_override
from what2wear.model import DayType
from what2wear.store import read_state, write_state
from what2wear.wardrobe import (
    COLORS,
    DEFAULT_COLD_THRESHOLD,
    TIMEZONE,
    get_default_state,
)

TOKEN = "s3cret"  # noqa: S105
SAT = 5


@pytest.fixture
def state_path(tmp_path: Path) -> Path:
    return tmp_path / "state.json"


@pytest.fixture
def client(state_path: Path) -> FlaskClient:
    # No forecast, so no test here touches the network.
    return web.app(state_path, TOKEN, fetch_weather=dict).test_client()


def test_the_bare_url_is_todays_day_page(client: FlaskClient) -> None:
    page = _get_text(client, f"/{TOKEN}/")
    assert f"{_get_today():%a %d %b %Y}" in page
    assert " Day" in page
    assert "Shirt" in page
    assert "Pants" in page
    assert "Shoes" in page


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
    assert "Sun 27 Sep 2026" in _get_text(client, f"/{TOKEN}/")


def test_a_day_page_shows_that_date(client: FlaskClient) -> None:
    day = _get_today() + timedelta(days=400)
    page = _get_text(client, f"/{TOKEN}/day/{day}")
    assert f"{day:%a %d %b %Y}" in page


def test_the_day_type_is_named(client: FlaskClient) -> None:
    page = _get_text(client, f"/{TOKEN}/day/{_get_next(SAT)}")
    assert "Home Day" in page


def test_a_garment_reads_as_its_label_and_kind(
    client: FlaskClient,
) -> None:
    page = _get_text(client, f"/{TOKEN}/day/{_get_next(SAT)}")
    labels = get_default_state(_get_today()).labels
    assert any(
        f"{label} Pants" in page
        for key, label in labels.items()
        if key.startswith("pants.")
    )


def test_prev_and_next_step_one_calendar_day(
    client: FlaskClient,
) -> None:
    day = _get_today() + timedelta(days=10)
    page = _get_text(client, f"/{TOKEN}/day/{day}")
    assert f'href="/{TOKEN}/day/{day - timedelta(days=1)}"' in page
    assert f'href="/{TOKEN}/day/{day + timedelta(days=1)}"' in page


def test_the_date_picker_lands_on_the_day_page(
    client: FlaskClient,
) -> None:
    page = _get_text(client, f"/{TOKEN}/")
    assert 'type="date"' in page
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
    # and their Fallbacks cannot cover however the Week is walked.
    saturday = _get_next(SAT)
    write_state(
        state_path,
        record_override(
            get_default_state(_get_today()), saturday, DayType.OFFICE
        ),
    )
    page = _get_text(client, f"/{TOKEN}/day/{saturday}")
    assert "already worn this week" in page


def test_an_unknown_forecast_hedges_the_outerwear(
    client: FlaskClient,
) -> None:
    assert "if it's cold" in _get_text(client, f"/{TOKEN}/")


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
    assert "if it's cold" not in page
    assert "Sweater" in page or "Jacket" in page


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
    assert {name.rpartition(" ")[2] for _, name, _ in rows} >= {
        "Shirt",
        "Pants",
        "Shoes",
    }
    for paths, name, _ in rows:
        label = name.removesuffix(", if it's cold").rpartition(" ")[0]
        assert paths[0][1] == COLORS[label][0]


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
        paths
        for paths, name, _ in _get_drawn_garments(page)
        if name == "Striped Shirt"
    )
    color, stripe_color = COLORS["Striped"]
    assert [fill for _, fill in shirt] == [color, stripe_color, "none"]
    plain = [
        paths
        for paths, name, _ in _get_drawn_garments(page)
        if name != "Striped Shirt"
    ]
    assert all(len(paths) == 2 for paths in plain)


def test_icons_are_drawn_with_only_lines_and_curves(
    client: FlaskClient,
) -> None:
    page = _get_text(client, f"/{TOKEN}/")
    paths = re.findall(r' d="([^"]*)"', page)
    assert paths
    assert all(re.fullmatch(r"[MLQZ\d. ]+", path) for path in paths)
    assert "dasharray" not in page


def test_outerwear_worn_only_if_its_cold_is_dimmed(
    client: FlaskClient,
) -> None:
    rows = _get_drawn_garments(_get_text(client, f"/{TOKEN}/"))
    dimmed = [name for _, name, dim in rows if dim]
    assert len(dimmed) == 1
    assert dimmed[0].endswith(", if it's cold")


def test_outerwear_on_a_cold_day_is_not_dimmed(
    state_path: Path,
) -> None:
    today = _get_today()
    client = web.app(
        state_path,
        TOKEN,
        fetch_weather=lambda: {today: DEFAULT_COLD_THRESHOLD - 10},
    ).test_client()
    rows = _get_drawn_garments(_get_text(client, f"/{TOKEN}/"))
    assert len(rows) == 4
    assert not any(dim for _, _, dim in rows)


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
    assert [item["garment"] for item in outfit][:2] == [
        "shirt",
        "pants",
    ]
    assert outfit[-1]["garment"] == "shoes"
    assert outfit[2]["garment"] in {"sweater", "jacket"}
    for item in outfit:
        assert set(item) - {"if_cold"} == {"garment", "label", "icon"}
        icon = item["icon"]
        assert set(icon) == {"shape", "fill", "detail"}
        assert icon["fill"] == COLORS[item["label"]][0]
        assert all(
            re.fullmatch(r"[MLQZ\d. ]+", icon[path])
            for path in ("shape", "detail")
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
    assert shirt["icon"]["fill"] == color
    assert shirt["icon"]["pattern_fill"] == stripe_color
    assert re.fullmatch(r"[MLQZ\d. ]+", shirt["icon"]["pattern"])


def test_the_widget_json_marks_outerwear_if_cold_when_unknown(
    client: FlaskClient,
) -> None:
    reply = client.get(f"/{TOKEN}/day/{_get_today()}.json")
    assert reply.json is not None
    assert [
        item["garment"]
        for item in reply.json["outfit"]
        if "if_cold" in item
    ] == [reply.json["outfit"][2]["garment"]]
    assert reply.json["outfit"][2]["if_cold"] is True


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


def test_the_shirt_list_holds_the_dates_closets_shirts(
    client: FlaskClient,
) -> None:
    page = _get_text(client, f"/{TOKEN}/day/{_get_next(SAT)}")
    labels = get_default_state(_get_today()).labels
    assert all(
        f">{label}</option>" in page
        for key, label in labels.items()
        if key.startswith("home.shirt.")
    )


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
    other = next(
        shirt for shirt in shirts if f"{shirt} Shirt" not in page
    )
    page = _post_text(
        client, f"/{TOKEN}/day/{saturday}/shirt", {"shirt": other}
    )
    assert f"Recorded: the Shirt Rotation reset to {other}" in page
    assert f"{other} Shirt" in page


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
    assert f"{saturday:%a %d %b %Y}" in page
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


def test_settings_tick_the_current_office_weekdays(
    client: FlaskClient,
) -> None:
    page = _get_text(client, f"/{TOKEN}/settings")
    assert page.count('type="checkbox"') == 7
    assert page.count("checked") == 3


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


def test_settings_prefill_the_cold_threshold(
    client: FlaskClient,
) -> None:
    page = _get_text(client, f"/{TOKEN}/settings")
    assert 'type="number" step="any"' in page
    assert f'value="{DEFAULT_COLD_THRESHOLD:g}"' in page


def test_setting_the_cold_threshold_records_it(
    client: FlaskClient,
) -> None:
    page = _post_text(
        client,
        f"/{TOKEN}/settings/cold-threshold",
        {"threshold": "42.5"},
    )
    assert "Recorded: a Cold Threshold of 42.5°F" in page
    assert 'value="42.5"' in page


def test_the_cold_threshold_is_prefilled_exactly(
    client: FlaskClient,
) -> None:
    page = _post_text(
        client,
        f"/{TOKEN}/settings/cold-threshold",
        {"threshold": "50.123456"},
    )
    assert "Recorded: a Cold Threshold of 50.123456°F" in page
    assert 'value="50.123456"' in page


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


def test_a_threshold_that_is_no_temperature_is_refused(
    client: FlaskClient,
) -> None:
    reply = client.post(
        f"/{TOKEN}/settings/cold-threshold", data={"threshold": "nan"}
    )
    assert reply.status_code == 422
    assert "is not a temperature" in reply.get_data(as_text=True)


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


def test_the_closet_page_groups_each_closet_by_pants(
    client: FlaskClient,
) -> None:
    page = _get_text(client, f"/{TOKEN}/closet")
    assert "Office Closet" in page
    assert "Home Closet" in page
    # The office closet's Blue Pants hang White and Striped, and
    # nothing hangs between them but those.
    office = _get_office_closet(page)
    blue = office[
        office.index("Blue Pants") : office.index("Tan Pants")
    ]
    assert "White Shirt" in blue
    assert "Striped Shirt" in blue
    assert "Black Shirt" not in blue


def test_each_shirt_links_to_the_day_it_is_next_due(
    client: FlaskClient,
) -> None:
    today = _get_today()
    due = get_due_date(
        get_default_state(today), DayType.OFFICE, "Striped", today
    )
    page = _get_text(client, f"/{TOKEN}/closet")
    assert f'href="/{TOKEN}/day/{due}">{due:%a %d %b}</a>' in page


def test_swap_offers_only_shirts_sharing_pants(
    client: FlaskClient,
) -> None:
    page = _get_text(client, f"/{TOKEN}/closet")
    office = _get_office_closet(page)
    white = office[
        office.index("White Shirt") : office.index("Striped Shirt")
    ]
    assert ">Striped</option>" in white
    assert ">Dark Blue</option>" not in white
    assert ">White</option>" not in white


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
    assert "Office Closet" in page
    assert not state_path.exists()


def test_an_unknown_closet_is_not_found(client: FlaskClient) -> None:
    reply = client.post(
        f"/{TOKEN}/closet/gala/swap",
        data={"first": "White", "second": "Striped"},
    )
    assert reply.status_code == 404


def test_each_garment_opens_a_prefilled_replace_form(
    client: FlaskClient,
) -> None:
    page = _open_replace_form(client, "White Shirt")
    assert 'name="label" value="White"' in page
    assert 'type="color" name="color" value="#f4f4f1"' in page
    assert 'type="checkbox" name="striped" checked' not in page


def test_a_striped_garments_form_ticks_striped(
    client: FlaskClient,
) -> None:
    page = _open_replace_form(client, "Striped Shirt")
    assert 'type="checkbox" name="striped" checked' in page
    assert 'name="stripe_color" value="#3c67b4"' in page


def test_pants_and_the_rest_of_a_row_open_replace_forms_too(
    client: FlaskClient,
) -> None:
    assert 'name="label" value="Blue"' in _open_replace_form(
        client, "Blue Pants"
    )
    assert 'name="label" value="Beige"' in _open_replace_form(
        client, "Beige Sweater"
    )


def test_a_replace_records_the_label_and_colors(
    client: FlaskClient, state_path: Path
) -> None:
    reply = _post_replace(
        client,
        "White Shirt",
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
    assert "Pinstripe Shirt" in page
    state = read_state(state_path, _get_today())
    assert state.colors["office.shirt.0"] == ("#ffffff", "#000080")


def test_an_unticked_striped_ignores_the_stripe_color(
    client: FlaskClient, state_path: Path
) -> None:
    _post_replace(
        client,
        "Striped Shirt",
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
        client, "Blue Pants", {"label": "Blue", "color": "#3c67b4"}
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
def test_a_refused_replace_reshows_the_form_with_the_message(
    client: FlaskClient, state_path: Path, label: str, message: str
) -> None:
    reply = _post_replace(
        client, "White Shirt", {"label": label, "color": "#ffffff"}
    )
    assert reply.status_code == 422
    page = html.unescape(reply.get_data(as_text=True))
    assert message in page
    assert f'name="label" value="{label}"' in page
    assert not state_path.exists()


def test_a_color_that_is_no_color_is_a_bad_request(
    client: FlaskClient,
) -> None:
    reply = _post_replace(
        client, "White Shirt", {"label": "White", "color": "red"}
    )
    assert reply.status_code == 400


def test_an_unknown_garment_has_no_replace_form(
    client: FlaskClient,
) -> None:
    for url in (
        f"/{TOKEN}/closet/office.shirt.99",
        f"/{TOKEN}/closet/nothing",
    ):
        assert client.get(url).status_code == 404


def _open_replace_form(client: FlaskClient, name: str) -> str:
    return _get_text(client, _get_replace_url(client, name))


def _post_replace(
    client: FlaskClient, name: str, data: dict[str, str]
) -> TestResponse:
    return client.post(_get_replace_url(client, name), data=data)


def _get_replace_url(client: FlaskClient, name: str) -> str:
    """Follow the Office Closet's link on the Garment called `name`."""
    office = _get_office_closet(_get_text(client, f"/{TOKEN}/closet"))
    match = re.search(f'<a href="([^"]+)">{name}</a>', office)
    assert match is not None
    return match[1]


def _get_office_closet(page: str) -> str:
    return page[page.index("Office Closet") : page.index("Home Closet")]


def _post_text(
    client: FlaskClient, url: str, data: dict[str, str | list[str]]
) -> str:
    reply = client.post(url, data=data, follow_redirects=True)
    assert reply.status_code == 200
    return html.unescape(reply.get_data(as_text=True))


def _get_drawn_garments(
    page: str,
) -> list[tuple[list[tuple[str, str]], str, bool]]:
    """Each drawn Garment: its paths' `d` and fill, name, dimming."""
    return [
        (
            re.findall(r'<path d="([^"]*)" fill="([^"]*)"', svg),
            name.strip(),
            "dim" in attrs,
        )
        for attrs, svg, name in re.findall(
            r"<li([^>]*)>\s*<svg[^>]*>(.*?)</svg>(.*?)</li>",
            page,
            re.DOTALL,
        )
    ]


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
