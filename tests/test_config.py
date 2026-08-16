"""The config boundary: hand-authored YAML in, validated State out,
nothing written back.
"""

from datetime import date
from pathlib import Path

import pytest

from wardrobe import WARDROBE
from what2wear.config import ConfigError, load_state
from what2wear.model import PantsRow, Shirt

VALID = """
# A comment, which must survive being read.
office_weekdays: [mon, wed, fri]

office:
  anchor: { date: 2026-08-17, shirt: o2 }
  shirts:
    - { name: o1, pants: tan }
    - { name: o2, pants: navy }
  pants:
    tan: { sweater: beige, shoes: brown, fallback: grey }
    navy: { sweater: grey, shoes: white }

home:
  anchor: { date: 2026-08-15, shirt: h1 }
  shirts:
    - { name: h1, pants: blue }
  pants:
    blue: { sweater: yellow, jacket: brown, shoes: black }
"""


class TestLoading:
    def test_closets_shirts_and_pants_are_parsed(
        self, tmp_path: Path
    ) -> None:
        state = load_state(_write(tmp_path, VALID))
        assert state.office.shirts == (
            Shirt("o1", "tan"),
            Shirt("o2", "navy"),
        )
        assert state.home.shirts == (Shirt("h1", "blue"),)

    def test_anchors_are_a_date_plus_the_shirt_worn_that_day(
        self, tmp_path: Path
    ) -> None:
        state = load_state(_write(tmp_path, VALID))
        assert (
            state.office.anchor_date,
            state.office.anchor_shirt,
        ) == (date(2026, 8, 17), "o2")
        assert (state.home.anchor_date, state.home.anchor_shirt) == (
            date(2026, 8, 15),
            "h1",
        )

    def test_the_weekday_pattern_is_parsed_into_weekday_numbers(
        self, tmp_path: Path
    ) -> None:
        state = load_state(_write(tmp_path, VALID))
        assert state.office_weekdays == frozenset({0, 2, 4})

    def test_office_pants_rows_carry_a_sweater_shoes_and_fallback(
        self, tmp_path: Path
    ) -> None:
        # Looked up rather than compared as a sequence: the rows are a
        # mapping keyed by pants, so their order carries no meaning.
        state = load_state(_write(tmp_path, VALID))
        assert state.office.row_for("tan") == PantsRow(
            "tan", sweater="beige", shoes="brown", fallback="grey"
        )
        assert state.office.row_for("navy") == PantsRow(
            "navy", sweater="grey", shoes="white"
        )

    def test_home_pants_rows_carry_a_jacket_instead(
        self, tmp_path: Path
    ) -> None:
        state = load_state(_write(tmp_path, VALID))
        assert state.home.row_for("blue") == PantsRow(
            "blue", sweater="yellow", shoes="black", jacket="brown"
        )

    def test_the_yaml_is_never_rewritten(self, tmp_path: Path) -> None:
        path = _write(tmp_path, VALID)
        before = path.read_bytes()
        load_state(path)
        assert path.read_bytes() == before


class TestValidation:
    def test_a_missing_file_says_so(self, tmp_path: Path) -> None:
        with pytest.raises(ConfigError, match="no config file at"):
            load_state(tmp_path / "absent.yaml")

    def test_malformed_yaml_says_so(self, tmp_path: Path) -> None:
        with pytest.raises(ConfigError, match="is not valid YAML"):
            load_state(_write(tmp_path, "office: [unclosed"))

    def test_a_missing_field_names_it(self, tmp_path: Path) -> None:
        text = VALID.replace(
            "    - { name: o1, pants: tan }\n", "    - { name: o1 }\n"
        )
        with pytest.raises(
            ConfigError, match=r"office\.shirts\.0\.pants"
        ):
            load_state(_write(tmp_path, text))

    def test_an_unknown_weekday_name_lists_the_valid_ones(
        self, tmp_path: Path
    ) -> None:
        text = VALID.replace("[mon, wed, fri]", "[mon, wodensday]")
        with pytest.raises(ConfigError, match="wodensday"):
            load_state(_write(tmp_path, text))

    def test_an_empty_closet_is_rejected(self, tmp_path: Path) -> None:
        text = VALID.replace("    - { name: h1, pants: blue }\n", "")
        with pytest.raises(ConfigError, match="home.shirts"):
            load_state(_write(tmp_path, text))

    def test_duplicate_shirt_names_within_a_closet_are_rejected(
        self, tmp_path: Path
    ) -> None:
        text = VALID.replace(
            "{ name: o2, pants: navy }", "{ name: o1, pants: navy }"
        )
        with pytest.raises(
            ConfigError, match="duplicate shirt name 'o1'"
        ):
            load_state(_write(tmp_path, text))

    def test_an_anchor_shirt_absent_from_its_closet_is_rejected(
        self, tmp_path: Path
    ) -> None:
        text = VALID.replace("shirt: o2 }", "shirt: o9 }")
        with pytest.raises(
            ConfigError,
            match="anchor shirt 'o9' is not in the office closet",
        ):
            load_state(_write(tmp_path, text))

    def test_an_office_anchor_that_is_not_an_office_day_is_rejected(
        self, tmp_path: Path
    ) -> None:
        text = VALID.replace(
            "{ date: 2026-08-17, shirt: o2 }",
            "{ date: 2026-08-18, shirt: o2 }",
        )
        with pytest.raises(
            ConfigError, match="2026-08-18 is not an office day"
        ):
            load_state(_write(tmp_path, text))

    def test_a_home_anchor_that_is_not_a_home_day_is_rejected(
        self, tmp_path: Path
    ) -> None:
        text = VALID.replace(
            "{ date: 2026-08-15, shirt: h1 }",
            "{ date: 2026-08-17, shirt: h1 }",
        )
        with pytest.raises(
            ConfigError, match="2026-08-17 is not a home day"
        ):
            load_state(_write(tmp_path, text))

    def test_a_week_with_no_home_days_is_rejected(
        self, tmp_path: Path
    ) -> None:
        text = VALID.replace(
            "[mon, wed, fri]", "[mon, tue, wed, thu, fri, sat, sun]"
        )
        with pytest.raises(ConfigError, match="leaving no home days"):
            load_state(_write(tmp_path, text))

    def test_a_repeated_weekday_is_not_mistaken_for_a_longer_week(
        self, tmp_path: Path
    ) -> None:
        text = VALID.replace(
            "[mon, wed, fri]", "[mon, mon, wed, wed, fri, fri, mon]"
        )
        assert load_state(
            _write(tmp_path, text)
        ).office_weekdays == frozenset({0, 2, 4})

    def test_a_file_that_is_not_text_says_so(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "what2wear.yaml"
        path.write_bytes(b"\xff\xfe\x00\x01not utf-8 at all")
        with pytest.raises(ConfigError, match="is not UTF-8 text"):
            load_state(path)

    def test_a_pants_colour_with_no_row_is_rejected(
        self, tmp_path: Path
    ) -> None:
        text = VALID.replace(
            "    - { name: o2, pants: navy }\n",
            "    - { name: o2, pants: navy }\n"
            "    - { name: o3, pants: khaki }\n",
        )
        with pytest.raises(
            ConfigError,
            match="office closet: no pants row for 'khaki'",
        ):
            load_state(_write(tmp_path, text))

    def test_a_fallback_that_is_no_other_rows_sweater_is_rejected(
        self, tmp_path: Path
    ) -> None:
        text = VALID.replace("fallback: grey", "fallback: purple")
        with pytest.raises(
            ConfigError,
            match="fallback 'purple' for tan pants is no other row's",
        ):
            load_state(_write(tmp_path, text))

    def test_a_fallback_naming_its_own_rows_sweater_is_rejected(
        self, tmp_path: Path
    ) -> None:
        text = VALID.replace("fallback: grey", "fallback: beige")
        with pytest.raises(ConfigError, match="fallback 'beige'"):
            load_state(_write(tmp_path, text))

    def test_two_office_rows_sharing_a_sweater_are_rejected(
        self, tmp_path: Path
    ) -> None:
        text = VALID.replace(
            "navy: { sweater: grey, shoes: white }",
            "navy: { sweater: beige, shoes: white }",
        )
        with pytest.raises(
            ConfigError, match="more than one row wears sweater 'beige'"
        ):
            load_state(_write(tmp_path, text))

    def test_an_office_row_may_not_name_a_jacket(
        self, tmp_path: Path
    ) -> None:
        text = VALID.replace(
            "navy: { sweater: grey, shoes: white }",
            "navy: { sweater: grey, shoes: white, jacket: brown }",
        )
        with pytest.raises(ConfigError, match="office.pants.navy"):
            load_state(_write(tmp_path, text))

    def test_a_home_row_may_not_name_a_fallback(
        self, tmp_path: Path
    ) -> None:
        text = VALID.replace(
            "blue: { sweater: yellow, jacket: brown, shoes: black }",
            "blue: { sweater: yellow, jacket: brown, shoes: black,"
            " fallback: grey }",
        )
        with pytest.raises(ConfigError, match="home.pants.blue"):
            load_state(_write(tmp_path, text))

    def test_an_unknown_top_level_key_is_rejected(
        self, tmp_path: Path
    ) -> None:
        with pytest.raises(ConfigError, match="sweaters"):
            load_state(_write(tmp_path, VALID + "\nsweaters: {}\n"))


def test_the_shipped_config_matches_the_tested_wardrobe() -> None:
    assert (
        load_state(Path(__file__).parent.parent / "what2wear.yaml")
        == WARDROBE
    )


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "what2wear.yaml"
    path.write_text(text)
    return path
