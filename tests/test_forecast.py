import json
from datetime import date
from pathlib import Path

import pytest

from what2wear.forecast import FORECAST_URL, fetch_forecast


def test_each_forecast_date_maps_to_its_high(tmp_path: Path) -> None:
    assert fetch_forecast(
        _serve(
            tmp_path,
            {
                "daily": {
                    "time": ["2026-09-19", "2026-09-20"],
                    "temperature_2m_max": [48.2, 71],
                }
            },
        )
    ) == {date(2026, 9, 19): 48.2, date(2026, 9, 20): 71.0}


def test_a_date_with_no_high_is_left_out(tmp_path: Path) -> None:
    assert fetch_forecast(
        _serve(
            tmp_path,
            {
                "daily": {
                    "time": ["2026-09-19", "2026-09-20"],
                    "temperature_2m_max": [48.2, None],
                }
            },
        )
    ) == {date(2026, 9, 19): 48.2}


@pytest.mark.parametrize(
    "document",
    [
        "not json",
        json.dumps({"error": True, "reason": "out of range"}),
        json.dumps(
            {"daily": {"time": ["tomorrow"], "temperature_2m_max": [1]}}
        ),
        json.dumps(
            {
                "daily": {
                    "time": ["2026-09-19"],
                    "temperature_2m_max": ["hot"],
                }
            }
        ),
        json.dumps([]),
    ],
)
def test_a_forecast_that_does_not_read_is_no_forecast(
    tmp_path: Path, document: str
) -> None:
    path = tmp_path / "forecast.json"
    path.write_text(document)
    assert fetch_forecast(path.as_uri()) == {}


def test_a_forecast_that_cannot_be_reached_is_no_forecast(
    tmp_path: Path,
) -> None:
    assert fetch_forecast((tmp_path / "absent.json").as_uri()) == {}


def test_only_the_forecast_endpoint_is_asked() -> None:
    assert FORECAST_URL.startswith(
        "https://api.open-meteo.com/v1/forecast?"
    )


def _serve(tmp_path: Path, document: object) -> str:
    path = tmp_path / "forecast.json"
    path.write_text(json.dumps(document))
    return path.as_uri()
