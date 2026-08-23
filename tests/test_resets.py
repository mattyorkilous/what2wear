"""Resets, driven through the pure `handle` seam.

A Reset is passed in as part of the in-memory State, the same way an
Override is -- nothing here reads the log off disk. The Wardrobe is the
given one and `today` is held at `TODAY`, which is also the Anchor with
nothing recorded, so the dates below line up with the worked calendar.
"""

from datetime import date

import pytest

from what2wear.core import UnknownShirtError, handle
from what2wear.model import (
    DayType,
    DayTypeOverride,
    Reset,
    ResetRequest,
    Rotation,
    State,
)

TODAY = date(2026, 8, 22)
SAT22 = date(2026, 8, 22)
MON24, TUE25, WED26 = (
    date(2026, 8, 24),
    date(2026, 8, 25),
    date(2026, 8, 26),
)
THU27, FRI28, SAT29 = (
    date(2026, 8, 27),
    date(2026, 8, 28),
    date(2026, 8, 29),
)
MON31 = date(2026, 8, 31)


class TestABareReset:
    def test_it_moves_the_day_on_to_the_next_shirt(self) -> None:
        # Wednesday is black; the next office shirt is lblue.
        response = handle(
            WED26, State(), today=TODAY, record=ResetRequest()
        )
        assert response.outfit.shirt == "lblue"

    def test_it_records_a_shift_of_one_against_the_shirts(self) -> None:
        response = handle(
            WED26, State(), today=TODAY, record=ResetRequest()
        )
        assert response.decision == Reset(WED26, Rotation.SHIRT, 1)

    def test_it_moves_a_home_day_on_too(self) -> None:
        # Tuesday is dgreen; the next home shirt is black.
        response = handle(
            TUE25, State(), today=TODAY, record=ResetRequest()
        )
        assert response.outfit.shirt == "black"

    def test_it_defaults_to_today(self) -> None:
        response = handle(
            None, State(), today=SAT22, record=ResetRequest()
        )
        assert response.decision == Reset(SAT22, Rotation.SHIRT, 1)


class TestANamedReset:
    def test_it_jumps_straight_to_that_shirt(self) -> None:
        response = handle(
            WED26,
            State(),
            today=TODAY,
            record=ResetRequest("dblue"),
        )
        assert response.outfit.shirt == "dblue"

    def test_it_records_the_distance_it_jumped(self) -> None:
        # Black sits at 1 and dblue at 4.
        response = handle(
            WED26,
            State(),
            today=TODAY,
            record=ResetRequest("dblue"),
        )
        assert response.decision == Reset(WED26, Rotation.SHIRT, 3)

    def test_a_shirt_already_behind_is_reached_by_going_forward(
        self,
    ) -> None:
        # Monday's white sits at 0 and Wednesday's black at 1, so
        # asking for white again on the Wednesday means going round.
        response = handle(
            WED26, State(), today=TODAY, record=ResetRequest("white")
        )
        assert response.outfit.shirt == "white"
        assert response.decision == Reset(WED26, Rotation.SHIRT, 4)

    def test_the_shirt_it_names_is_the_one_it_already_had(self) -> None:
        response = handle(
            WED26, State(), today=TODAY, record=ResetRequest("black")
        )
        assert response.outfit.shirt == "black"
        assert response.decision == Reset(WED26, Rotation.SHIRT, 0)


class TestTheClosetIsInferredFromTheDay:
    def test_a_home_day_names_a_home_shirt(self) -> None:
        response = handle(
            TUE25, State(), today=TODAY, record=ResetRequest("beige")
        )
        assert response.outfit.shirt == "beige"

    @pytest.mark.parametrize(
        ("on", "shirt"),
        [(WED26, "brown"), (TUE25, "striped")],
    )
    def test_a_shirt_the_days_closet_lacks_is_an_error(
        self, on: date, shirt: str
    ) -> None:
        with pytest.raises(UnknownShirtError, match=shirt):
            handle(on, State(), today=TODAY, record=ResetRequest(shirt))

    def test_an_override_decides_which_closet_is_meant(self) -> None:
        # Wednesday spent at home, so a home shirt is now the one that
        # can be named on it and the office shirt is not.
        s = _with(overrides=(DayTypeOverride(WED26, DayType.HOME),))
        response = handle(
            WED26, s, today=TODAY, record=ResetRequest("beige")
        )
        assert response.outfit.shirt == "beige"

    def test_naming_a_shirt_leaves_the_days_type_alone(self) -> None:
        response = handle(
            WED26,
            State(),
            today=TODAY,
            record=ResetRequest("dblue"),
        )
        assert response.day_type is DayType.OFFICE
        assert isinstance(response.decision, Reset)


class TestEveryLaterDateMovesWithIt:
    def test_later_dates_of_that_kind_are_shifted(self) -> None:
        s = _with(resets=(Reset(WED26, Rotation.SHIRT, 1),))
        worn = [
            handle(day, s, today=TODAY).outfit.shirt
            for day in (WED26, FRI28, MON31)
        ]
        assert worn == ["lblue", "striped", "dblue"]

    def test_resets_accumulate_rather_than_replace(self) -> None:
        s = _with(
            resets=(
                Reset(WED26, Rotation.SHIRT, 1),
                Reset(FRI28, Rotation.SHIRT, 1),
            )
        )
        assert handle(MON31, s, today=TODAY).outfit.shirt == "white"

    def test_only_the_closet_it_was_recorded_in_moves(self) -> None:
        # Reset on an office day, so the home rotation stays where it
        # was and Thursday is still black.
        s = _with(resets=(Reset(WED26, Rotation.SHIRT, 1),))
        assert handle(THU27, s, today=TODAY).outfit.shirt == "black"

    def test_a_home_reset_leaves_the_office_closet_alone(self) -> None:
        s = _with(resets=(Reset(TUE25, Rotation.SHIRT, 1),))
        assert handle(WED26, s, today=TODAY).outfit.shirt == "black"
        assert handle(SAT29, s, today=TODAY).outfit.shirt == "dblue"

    def test_the_other_days_of_the_week_still_resolve_around_it(
        self,
    ) -> None:
        # Wednesday's Reset is what Friday's Week walk sees when it
        # resolves the Monday and Wednesday behind it, so the Friday
        # sweater moves with the Reset rather than ignoring it.
        s = _with(resets=(Reset(WED26, Rotation.SHIRT, 1),))
        outfit = handle(FRI28, s, today=TODAY).outfit
        assert (outfit.shirt, outfit.sweater) == ("striped", "beige")

    def test_look_ahead_differs_by_exactly_the_recorded_shift(
        self,
    ) -> None:
        # Monday was going to be striped. Four shirts on from there
        # is round the end of the closet and back to lblue.
        assert handle(MON31, State(), today=TODAY).outfit.shirt == (
            "striped"
        )
        decision = handle(
            WED26, State(), today=TODAY, record=ResetRequest("white")
        ).decision
        assert decision == Reset(WED26, Rotation.SHIRT, 4)
        s = _with(resets=(decision,))
        assert handle(MON31, s, today=TODAY).outfit.shirt == "lblue"


class TestInterleavedWithOverrides:
    def test_both_kinds_apply_by_their_own_date(self) -> None:
        # Wednesday spent at home moves the home rotation on and parks
        # the office one, and the reset recorded that day moves the
        # home rotation again -- Thursday takes both.
        s = _with(
            overrides=(DayTypeOverride(WED26, DayType.HOME),),
            resets=(Reset(WED26, Rotation.SHIRT, 1),),
        )
        assert handle(WED26, s, today=TODAY).outfit.shirt == "purple"
        assert handle(THU27, s, today=TODAY).outfit.shirt == "dblue"
        assert handle(FRI28, s, today=TODAY).outfit.shirt == "black"

    def test_an_override_after_a_reset_still_parks_the_shirt(
        self,
    ) -> None:
        s = _with(
            overrides=(DayTypeOverride(FRI28, DayType.HOME),),
            resets=(Reset(WED26, Rotation.SHIRT, 1),),
        )
        assert handle(MON31, s, today=TODAY).outfit.shirt == "striped"


def _with(
    *,
    overrides: tuple[DayTypeOverride, ...] = (),
    resets: tuple[Reset, ...] = (),
) -> State:
    return State(overrides=overrides, resets=resets)
