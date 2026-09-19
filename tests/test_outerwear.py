from datetime import date

import pytest

from what2wear.core import answer, replace_
from what2wear.model import Response
from what2wear.wardrobe import DEFAULT_COLD_THRESHOLD, get_default_state

TODAY = date(2026, 8, 22)
MON = date(2026, 8, 24)
# The Week whose Friday wears blue pants again after Monday took beige.
FALLBACK_MON = date(2026, 8, 31)
FALLBACK_FRI = date(2026, 9, 4)
HOME_DAY = date(2026, 9, 1)
COLD = DEFAULT_COLD_THRESHOLD - 10
WARM = DEFAULT_COLD_THRESHOLD + 25


class TestOfficeOuterwear:
    def test_a_cold_day_wears_the_sweater_its_pants_map_to(
        self,
    ) -> None:
        response = _response(MON, {MON: COLD})
        assert response.outfit.sweater == "beige"
        assert response.cold is True

    def test_a_cold_day_after_a_taken_sweater_wears_the_fallback(
        self,
    ) -> None:
        assert (
            _response(FALLBACK_FRI, {FALLBACK_FRI: COLD}).outfit.sweater
            == "grey"
        )

    @pytest.mark.parametrize(
        "high",
        [DEFAULT_COLD_THRESHOLD, DEFAULT_COLD_THRESHOLD + 0.1, WARM],
    )
    def test_at_or_above_the_threshold_no_outerwear_is_named(
        self, high: float
    ) -> None:
        response = _response(MON, {MON: high})
        assert response.outfit.sweater is None
        assert response.cold is False

    def test_just_below_the_threshold_is_cold(self) -> None:
        assert _response(MON, {MON: DEFAULT_COLD_THRESHOLD - 0.1}).cold

    def test_a_warm_day_keeps_its_shirt_pants_and_shoes(self) -> None:
        warm_outfit = _response(
            FALLBACK_FRI, {FALLBACK_FRI: WARM}
        ).outfit
        cold_outfit = _response(
            FALLBACK_FRI, {FALLBACK_FRI: COLD}
        ).outfit
        assert (
            warm_outfit.shirt,
            warm_outfit.pants,
            warm_outfit.shoes,
        ) == (
            cold_outfit.shirt,
            cold_outfit.pants,
            cold_outfit.shoes,
        )

    def test_a_warm_monday_does_not_free_its_sweater_for_the_week(
        self,
    ) -> None:
        # Which sweater a day calls for is knowable without any
        # weather, so no day's weather can change another's garment.
        assert (
            _response(
                FALLBACK_FRI, {FALLBACK_MON: WARM, FALLBACK_FRI: COLD}
            ).outfit.sweater
            == "grey"
        )

    def test_a_cold_day_names_the_sweater_by_its_label(self) -> None:
        state = replace_(
            get_default_state(TODAY), "office.sweater.beige", "oatmeal"
        )
        assert (
            answer(state, MON, {MON: COLD}).outfit.sweater == "oatmeal"
        )


class TestUnknownWeather:
    def test_beyond_the_horizon_names_the_garment_and_hedges(
        self,
    ) -> None:
        response = _response(MON, {TODAY: COLD})
        assert response.outfit.sweater == "beige"
        assert response.cold is None

    def test_beyond_the_horizon_keeps_everything_else(self) -> None:
        unknown_outfit = _response(FALLBACK_FRI, {}).outfit
        cold_outfit = _response(
            FALLBACK_FRI, {FALLBACK_FRI: COLD}
        ).outfit
        assert unknown_outfit == cold_outfit

    def test_a_failed_lookup_answers_as_beyond_the_horizon(
        self,
    ) -> None:
        # A failed fetch reaches the core as no weather at all.
        assert _response(MON, {}) == _response(MON, {TODAY: COLD})

    def test_the_three_states_are_distinct(self) -> None:
        assert (
            len(
                {
                    _response(MON, {MON: COLD}),
                    _response(MON, {MON: WARM}),
                    _response(MON, {}),
                }
            )
            == 3
        )


class TestHomeOuterwear:
    def test_a_cold_home_day_names_a_sweater(self) -> None:
        assert _response(HOME_DAY, {HOME_DAY: COLD}).outfit.sweater

    def test_a_warm_home_day_names_none(self) -> None:
        assert (
            _response(HOME_DAY, {HOME_DAY: WARM}).outfit.sweater is None
        )

    def test_an_unknown_home_day_names_it_and_hedges(self) -> None:
        response = _response(HOME_DAY, {})
        assert response.outfit.sweater
        assert response.cold is None


def _response(on: date, weather: dict[date, float]) -> Response:
    return answer(get_default_state(TODAY), on, weather)
