from datetime import date

import pytest

from what2wear.core import answer, replace_
from what2wear.errors import What2wearError
from what2wear.model import Garment, State
from what2wear.wardrobe import get_default_state

TODAY = date(2026, 8, 22)
SAT22, TUE25 = date(2026, 8, 22), date(2026, 8, 25)
MON24, WED26, FRI28 = (
    date(2026, 8, 24),
    date(2026, 8, 26),
    date(2026, 8, 28),
)
GIVEN = get_default_state(TODAY)


def _replaced(key: str, label: str) -> State:
    return replace_(GIVEN, key, label, "#123456")


def test_a_replaced_garment_is_named_by_its_new_label() -> None:
    told = _replaced("office.shirt.0", "cream")
    assert answer(told, MON24, {}).outfit.shirt.label == "cream"


def test_a_replace_moves_no_rotation() -> None:
    # The replaced Shirt is still Monday's and the other two are still
    # where they were, so nothing followed the Label.
    told = _replaced("office.shirt.0", "cream")
    assert [
        answer(told, on, {}).outfit.shirt.label
        for on in (MON24, WED26, FRI28)
    ] == ["cream", "Black", "Light Blue"]


def test_a_garment_is_replaced_again_where_it_hangs() -> None:
    # Where a Garment hangs stays put while its Label changes.
    once = _replaced("home.shirt.0", "cream")
    twice = replace_(once, "home.shirt.0", "ecru", "#123456")
    assert answer(twice, SAT22, {}).outfit.shirt.label == "ecru"


def test_home_shoes_two_pants_rows_call_for_change_once() -> None:
    # Saturday wears blue pants and Tuesday tan, and the black shoes
    # are one pair worn with either.
    told = _replaced("home.shoes.0", "oxblood")
    assert [
        answer(told, on, {}).outfit.shoes.label for on in (SAT22, TUE25)
    ] == [
        "oxblood",
        "oxblood",
    ]


def test_replacing_pants_changes_them_in_both_closets() -> None:
    # One set of trousers, both Closets wearing it.
    told = _replaced("pants.0", "navy")
    assert [
        answer(told, on, {}).outfit.pants.label for on in (SAT22, MON24)
    ] == [
        "navy",
        "navy",
    ]


def test_the_same_label_in_the_two_closets_stays_legal() -> None:
    # The home Closet already has a yellow sweater, and the office
    # one is a different garment.
    told = _replaced("office.sweater.0", "Yellow")
    assert (
        _get_label(answer(told, MON24, {}).outfit.sweater) == "Yellow"
    )


def test_the_same_label_in_another_kind_stays_legal() -> None:
    # The office already has brown shoes, and a sweater is not shoes.
    told = _replaced("office.sweater.0", "Brown")
    assert _get_label(answer(told, MON24, {}).outfit.sweater) == "Brown"


def test_a_replace_records_the_color_with_the_label() -> None:
    told = replace_(GIVEN, "office.shirt.0", "Plaid", "#aa0000")
    assert answer(told, MON24, {}).outfit.shirt == Garment(
        "Plaid", "#aa0000"
    )


def test_a_replace_records_a_stripe_color() -> None:
    told = replace_(
        GIVEN, "office.shirt.0", "Pinstripe", "#ffffff", "#000080"
    )
    assert answer(told, MON24, {}).outfit.shirt == Garment(
        "Pinstripe", "#ffffff", "#000080"
    )


def test_a_replace_without_a_stripe_color_drops_the_stripe() -> None:
    told = replace_(GIVEN, "office.shirt.3", "Plain", "#ffffff")
    assert told.colors["office.shirt.3"] == ("#ffffff", None)


def test_restating_a_label_with_a_new_color_records_it() -> None:
    told = replace_(GIVEN, "office.shirt.0", "White", "#fffff0")
    assert answer(told, MON24, {}).outfit.shirt.color == "#fffff0"


class TestARefusedReplace:
    def test_a_label_with_a_dot_is_refused(self) -> None:
        # The Garment would no longer be addressable, since its address
        # splits on the last dot.
        with pytest.raises(What2wearError, match=r"\."):
            _replaced("office.shirt.0", "St. Patrick")

    def test_a_label_another_garment_of_that_kind_has_is_refused(
        self,
    ) -> None:
        # The office already has black shoes, so a second pair called
        # black would leave the answer unactionable.
        with pytest.raises(What2wearError, match="Black"):
            _replaced("office.shoes.0", "Black")

    def test_restating_the_label_and_color_is_not(self) -> None:
        brown = GIVEN.colors["office.shoes.0"]
        assert (
            replace_(GIVEN, "office.shoes.0", "Brown", *brown) == GIVEN
        )

    def test_a_key_nothing_hangs_at_is_refused(self) -> None:
        # Recording it would write a made-up Garment into the State.
        with pytest.raises(
            What2wearError, match=r"nothing hangs at 'office\.shirt\.9'"
        ):
            _replaced("office.shirt.9", "cream")


def _get_label(garment: Garment | None) -> str | None:
    return None if garment is None else garment.label
