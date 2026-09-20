from datetime import date

import pytest

from what2wear.core import answer, replace_, set_cold_threshold
from what2wear.errors import What2wearError
from what2wear.model import Response
from what2wear.wardrobe import DEFAULT_COLD_THRESHOLD, get_default_state

TODAY = date(2026, 8, 22)
MON = date(2026, 8, 24)
# The Week whose Friday wears blue pants again after Monday took beige.
FALLBACK_MON = date(2026, 8, 31)
FALLBACK_FRI = date(2026, 9, 4)
# Home Days either side of the Office Days of one Week.
TUE, WED, THU, FRI, SAT = (date(2026, 9, day) for day in range(1, 6))
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
    def test_consecutive_cold_home_days_alternate(self) -> None:
        # Wednesday and Friday are Office Days and do not move it.
        assert [
            _get_home_outerwear(on, {on: COLD})
            for on in (TUE, THU, SAT)
        ] == [(None, "brown"), ("beige", None), (None, "black")]

    def test_a_warm_day_spends_its_turn(self) -> None:
        # ADR-0004's price, asserted rather than worked around: the
        # mild Thursday took the sweater turn, so both sides wear a
        # jacket.
        weather: dict[date, float] = {TUE: COLD, THU: WARM, SAT: COLD}
        assert [
            _get_home_outerwear(on, weather) for on in (TUE, THU, SAT)
        ] == [(None, "brown"), (None, None), (None, "black")]

    def test_office_sweaters_between_them_change_nothing(self) -> None:
        cold_office = dict.fromkeys((WED, FRI), COLD)
        warm_office = dict.fromkeys((WED, FRI), WARM)
        assert all(
            _response(on, {on: COLD, **cold_office})
            == _response(on, {on: COLD, **warm_office})
            for on in (TUE, THU, SAT)
        )
        assert all(
            _response(on, {on: COLD}).outfit.sweater
            for on in (WED, FRI)
        )

    def test_beyond_the_horizon_names_the_garment_and_hedges(
        self,
    ) -> None:
        response = _response(TUE, {})
        assert (response.outfit.sweater, response.outfit.jacket) == (
            None,
            "brown",
        )
        assert response.cold is None

    def test_a_date_years_out_still_names_its_kind(self) -> None:
        far = date(2031, 3, 1)
        assert _get_home_outerwear(far, {}) != (None, None)

    def test_a_jacket_can_come_twice_in_a_week(self) -> None:
        # Tuesday's tan pants and Saturday's black both call for the
        # one black jacket, and home has no no-repeat rule to stop it.
        tue, sat = date(2026, 8, 25), date(2026, 8, 29)
        responses = [_response(on, {on: COLD}) for on in (tue, sat)]
        assert [r.outfit.jacket for r in responses] == ["black"] * 2
        assert not any(r.unavoidable_repeat for r in responses)

    def test_a_jacket_is_named_by_its_label(self) -> None:
        state = replace_(
            get_default_state(TODAY), "home.jacket.black", "navy"
        )
        assert answer(state, SAT, {SAT: COLD}).outfit.jacket == "navy"


class TestTheColdThreshold:
    def test_a_new_threshold_decides_whether_outerwear_is_worn(
        self,
    ) -> None:
        mild = DEFAULT_COLD_THRESHOLD + 2
        state = set_cold_threshold(
            get_default_state(TODAY), DEFAULT_COLD_THRESHOLD + 5
        )
        assert _response(MON, {MON: mild}).cold is False
        assert answer(state, MON, {MON: mild}).outfit.sweater == "beige"

    def test_a_day_it_makes_warm_still_spends_its_turn(self) -> None:
        # Lowering it turns Thursday warm, and Saturday still wears
        # the jacket its turn gave it: the threshold moves no
        # Position.
        weather: dict[date, float] = {
            TUE: COLD,
            THU: COLD + 5,
            SAT: COLD,
        }
        state = set_cold_threshold(get_default_state(TODAY), COLD + 1)
        assert [
            _get_home_outerwear(on, weather) for on in (TUE, THU, SAT)
        ] == [(None, "brown"), ("beige", None), (None, "black")]
        assert [
            (outfit.sweater, outfit.jacket)
            for outfit in (
                answer(state, on, weather).outfit
                for on in (TUE, THU, SAT)
            )
        ] == [(None, "brown"), (None, None), (None, "black")]

    @pytest.mark.parametrize("threshold", [float("nan"), float("inf")])
    def test_a_threshold_that_is_no_temperature_is_refused(
        self, threshold: float
    ) -> None:
        with pytest.raises(What2wearError):
            set_cold_threshold(get_default_state(TODAY), threshold)


def _get_home_outerwear(
    on: date, weather: dict[date, float]
) -> tuple[str | None, str | None]:
    outfit = _response(on, weather).outfit
    return outfit.sweater, outfit.jacket


def _response(on: date, weather: dict[date, float]) -> Response:
    return answer(get_default_state(TODAY), on, weather)
