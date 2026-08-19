"""Resets, driven through the pure `handle` seam.

A Reset is passed in as part of the in-memory State, the same way an
Override is -- nothing here reads the log off disk. The Wardrobe is the
example one, so the dates below line up with the worked calendar.
"""

from dataclasses import replace
from datetime import date

import pytest
from conftest import WARDROBE

from what2wear.core import UnknownShirtError, handle
from what2wear.model import (
    DayType,
    DayTypeOverride,
    Reset,
    ResetRequest,
    Rotation,
    State,
)

MON17, TUE18, WED19, THU20, FRI21 = (
    date(2026, 8, 17),
    date(2026, 8, 18),
    date(2026, 8, 19),
    date(2026, 8, 20),
    date(2026, 8, 21),
)
SAT22, MON24 = date(2026, 8, 22), date(2026, 8, 24)
MON10, SUN16 = date(2026, 8, 10), date(2026, 8, 16)


class TestABareReset:
    def test_it_moves_the_day_on_to_the_next_shirt(self) -> None:
        # Wednesday is poplin; the next office shirt is twill.
        response = handle(
            WED19, WARDROBE, today=WED19, record=ResetRequest()
        )
        assert response.outfit.shirt == "twill"

    def test_it_records_a_shift_of_one_against_the_shirts(self) -> None:
        response = handle(
            WED19, WARDROBE, today=WED19, record=ResetRequest()
        )
        assert response.decision == Reset(WED19, Rotation.SHIRT, 1)

    def test_it_moves_a_home_day_on_too(self) -> None:
        # Tuesday is henley; the next home shirt is jersey.
        response = handle(
            TUE18, WARDROBE, today=TUE18, record=ResetRequest()
        )
        assert response.outfit.shirt == "jersey"

    def test_it_defaults_to_today(self) -> None:
        response = handle(
            None, WARDROBE, today=WED19, record=ResetRequest()
        )
        assert response.decision == Reset(WED19, Rotation.SHIRT, 1)


class TestANamedReset:
    def test_it_jumps_straight_to_that_shirt(self) -> None:
        response = handle(
            WED19,
            WARDROBE,
            today=WED19,
            record=ResetRequest("gingham"),
        )
        assert response.outfit.shirt == "gingham"

    def test_it_records_the_distance_it_jumped(self) -> None:
        # Poplin sits at 0 and gingham at 3.
        response = handle(
            WED19,
            WARDROBE,
            today=WED19,
            record=ResetRequest("gingham"),
        )
        assert response.decision == Reset(WED19, Rotation.SHIRT, 3)

    def test_a_shirt_already_behind_is_reached_by_going_forward(
        self,
    ) -> None:
        # Monday's sateen sits at 4 and Wednesday's poplin at 0, so
        # asking for sateen again on the Wednesday means going round.
        response = handle(
            WED19, WARDROBE, today=WED19, record=ResetRequest("sateen")
        )
        assert response.outfit.shirt == "sateen"
        assert response.decision == Reset(WED19, Rotation.SHIRT, 4)

    def test_the_shirt_it_names_is_the_one_it_already_had(self) -> None:
        response = handle(
            WED19, WARDROBE, today=WED19, record=ResetRequest("poplin")
        )
        assert response.outfit.shirt == "poplin"
        assert response.decision == Reset(WED19, Rotation.SHIRT, 0)


class TestTheClosetIsInferredFromTheDay:
    def test_a_home_day_names_a_home_shirt(self) -> None:
        response = handle(
            TUE18, WARDROBE, today=TUE18, record=ResetRequest("rugby")
        )
        assert response.outfit.shirt == "rugby"

    @pytest.mark.parametrize(
        ("on", "shirt"),
        [(WED19, "henley"), (TUE18, "gingham")],
    )
    def test_a_shirt_the_days_closet_lacks_is_an_error(
        self, on: date, shirt: str
    ) -> None:
        with pytest.raises(UnknownShirtError, match=shirt):
            handle(on, WARDROBE, today=on, record=ResetRequest(shirt))

    def test_an_override_decides_which_closet_is_meant(self) -> None:
        # Wednesday spent at home, so a home shirt is now the one that
        # can be named on it and the office shirt is not.
        s = _with(overrides=(DayTypeOverride(WED19, DayType.HOME),))
        response = handle(
            WED19, s, today=WED19, record=ResetRequest("rugby")
        )
        assert response.outfit.shirt == "rugby"

    def test_naming_a_shirt_leaves_the_days_type_alone(self) -> None:
        response = handle(
            WED19,
            WARDROBE,
            today=WED19,
            record=ResetRequest("gingham"),
        )
        assert response.day_type is DayType.OFFICE
        assert isinstance(response.decision, Reset)


class TestEveryLaterDateMovesWithIt:
    def test_later_dates_of_that_kind_are_shifted(self) -> None:
        s = _with(resets=(Reset(WED19, Rotation.SHIRT, 1),))
        worn = [
            handle(day, s, today=WED19).outfit.shirt
            for day in (WED19, FRI21, MON24)
        ]
        assert worn == ["twill", "flannel", "gingham"]

    def test_earlier_dates_are_untouched(self) -> None:
        s = _with(resets=(Reset(WED19, Rotation.SHIRT, 1),))
        assert handle(MON17, s, today=WED19) == handle(
            MON17, WARDROBE, today=WED19
        )

    def test_resets_accumulate_rather_than_replace(self) -> None:
        s = _with(
            resets=(
                Reset(WED19, Rotation.SHIRT, 1),
                Reset(FRI21, Rotation.SHIRT, 1),
            )
        )
        assert handle(MON24, s, today=WED19).outfit.shirt == "sateen"

    def test_only_the_closet_it_was_recorded_in_moves(self) -> None:
        # Reset on an office day, so the home rotation stays where it
        # was and Thursday is still jersey.
        s = _with(resets=(Reset(WED19, Rotation.SHIRT, 1),))
        assert handle(THU20, s, today=WED19).outfit.shirt == "jersey"

    def test_a_home_reset_leaves_the_office_closet_alone(self) -> None:
        s = _with(resets=(Reset(TUE18, Rotation.SHIRT, 1),))
        assert handle(WED19, s, today=TUE18).outfit.shirt == "poplin"
        assert handle(SAT22, s, today=TUE18).outfit.shirt == "waffle"

    def test_look_ahead_differs_by_exactly_the_recorded_shift(
        self,
    ) -> None:
        # Monday was going to be flannel. Four shirts on from there is
        # round the end of the closet and back to twill.
        assert handle(MON24, WARDROBE, today=WED19).outfit.shirt == (
            "flannel"
        )
        decision = handle(
            WED19, WARDROBE, today=WED19, record=ResetRequest("sateen")
        ).decision
        assert decision == Reset(WED19, Rotation.SHIRT, 4)
        s = _with(resets=(decision,))
        assert handle(MON24, s, today=WED19).outfit.shirt == "twill"


class TestTheAnchorIsTheLastWord:
    def test_a_reset_before_the_anchor_no_longer_counts(self) -> None:
        # Re-authoring the anchor says where the rotation stands, so
        # what was reset before it is not stacked back on top.
        s = _with(resets=(Reset(MON10, Rotation.SHIRT, 1),))
        assert handle(MON17, s, today=MON17) == handle(
            MON17, WARDROBE, today=MON17
        )

    def test_a_reset_on_the_anchor_date_still_counts(self) -> None:
        s = _with(resets=(Reset(MON17, Rotation.SHIRT, 1),))
        assert handle(MON17, s, today=MON17).outfit.shirt == "poplin"

    def test_each_closet_is_cut_off_at_its_own_anchor(self) -> None:
        # Sunday falls after the home anchor but before the office
        # one, so a home reset there still counts.
        s = _with(resets=(Reset(SUN16, Rotation.SHIRT, 1),))
        assert handle(TUE18, s, today=SUN16).outfit.shirt == "jersey"


class TestInterleavedWithOverrides:
    def test_both_kinds_apply_by_their_own_date(self) -> None:
        # Wednesday spent at home moves the home rotation on and parks
        # the office one, and the reset recorded that day moves the
        # home rotation again -- Thursday takes both.
        s = _with(
            overrides=(DayTypeOverride(WED19, DayType.HOME),),
            resets=(Reset(WED19, Rotation.SHIRT, 1),),
        )
        assert handle(WED19, s, today=WED19).outfit.shirt == "twill"
        assert handle(THU20, s, today=WED19).outfit.shirt == "waffle"
        assert handle(FRI21, s, today=WED19).outfit.shirt == "poplin"

    def test_an_override_after_a_reset_still_parks_the_shirt(
        self,
    ) -> None:
        s = _with(
            overrides=(DayTypeOverride(FRI21, DayType.HOME),),
            resets=(Reset(WED19, Rotation.SHIRT, 1),),
        )
        assert handle(MON24, s, today=WED19).outfit.shirt == "flannel"


def _with(
    *,
    overrides: tuple[DayTypeOverride, ...] = (),
    resets: tuple[Reset, ...] = (),
) -> State:
    return replace(WARDROBE, overrides=overrides, resets=resets)
