"""Fetching the forecast."""

import json
from collections.abc import Mapping
from datetime import date
from http.client import HTTPException
from types import MappingProxyType
from urllib.request import urlopen

from what2wear.wardrobe import LATITUDE, LONGITUDE

FORECAST_URL = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LATITUDE}&longitude={LONGITUDE}"
    "&daily=temperature_2m_max&temperature_unit=fahrenheit"
    "&timezone=auto&forecast_days=16"
)


def fetch_forecast(url: str = FORECAST_URL) -> Mapping[date, float]:
    """Fetch the high for each date the forecast reaches.

    A forecast that cannot be had is no forecast rather than an error,
    so every date answers as though it were past the horizon.

    Args:
        url: Where to fetch it from.

    Returns:
        Each date mapped to its high in degrees Fahrenheit, or nothing
        if the forecast could not be fetched or read.
    """
    try:
        with urlopen(url, timeout=5) as response:  # noqa: S310
            daily = json.load(response)["daily"]
        return MappingProxyType(
            {
                date.fromisoformat(on): float(high)
                for on, high in zip(
                    daily["time"],
                    daily["temperature_2m_max"],
                    strict=True,
                )
                if high is not None
            }
        )
    except HTTPException, OSError, KeyError, TypeError, ValueError:
        return MappingProxyType({})
