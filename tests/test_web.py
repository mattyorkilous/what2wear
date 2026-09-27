import html
from datetime import UTC, date, datetime, timedelta, tzinfo
from pathlib import Path
from typing import Self

import pytest
from flask.testing import FlaskClient

from what2wear import web
from what2wear.core import record_override
from what2wear.model import DayType
from what2wear.store import write_state
from what2wear.wardrobe import (
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


@pytest.mark.parametrize(
    "url",
    ["/", "/wrong/", f"/{TOKEN}x/", "/wrong/day/2026-09-28", "/é/"],
)
def test_a_wrong_token_is_a_plain_404(
    client: FlaskClient, url: str
) -> None:
    reply = client.get(url)
    assert reply.status_code == 404
    assert "Shirt" not in reply.get_data(as_text=True)


@pytest.mark.parametrize(
    "url", [f"/{TOKEN}/", f"/{TOKEN}/day/2026-09-28", "/wrong/"]
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


def test_a_fresh_install_answers_and_writes_nothing(
    tmp_path: Path,
) -> None:
    absent = tmp_path / "absent" / "state.json"
    client = web.app(absent, TOKEN, fetch_weather=dict).test_client()
    assert "Shirt" in _get_text(client, f"/{TOKEN}/")
    assert not absent.parent.exists()


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
