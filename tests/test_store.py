from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from what2wear import store
from what2wear.core import answer, replace_
from what2wear.errors import What2wearError
from what2wear.model import Anchor, DayType, Rotation, State
from what2wear.store import read_state, write_state
from what2wear.wardrobe import (
    DEFAULT_COLD_THRESHOLD,
    DEFAULT_OFFICE_WEEKDAYS,
    build_default_colors,
    build_default_labels,
    get_default_state,
)

TODAY = date(2026, 8, 22)
TOMORROW = date(2026, 8, 23)
WED26 = date(2026, 8, 26)

TOLD = State(
    labels=build_default_labels(),
    colors=build_default_colors(),
    anchors={
        Rotation.OFFICE: Anchor(TODAY, 3),
        Rotation.HOME: Anchor(WED26, 7),
        Rotation.OUTERWEAR: Anchor(TOMORROW, 1),
    },
    office_weekdays=frozenset({1, 3, 5}),
    cold_threshold=55.5,
    overrides={WED26: DayType.HOME, TOMORROW: DayType.OFFICE},
)


def _document(overrides: str) -> str:
    return (
        '{"anchors": {'
        '"office": {"date": "2026-08-22", "position": 0}, '
        '"home": {"date": "2026-08-22", "position": 0}}, '
        f'"overrides": {overrides}}}'
    )


class TestRoundTrip:
    def test_a_state_written_and_read_back_is_the_same_state(
        self, tmp_path: Path
    ) -> None:
        write_state(_path(tmp_path), TOLD)
        assert read_state(_path(tmp_path), TODAY) == TOLD

    def test_a_later_write_replaces_the_one_before_it(
        self, tmp_path: Path
    ) -> None:
        write_state(_path(tmp_path), TOLD)
        write_state(_path(tmp_path), get_default_state(TODAY))
        assert read_state(_path(tmp_path), TODAY) == get_default_state(
            TODAY
        )

    def test_it_is_legible_to_a_person_who_opens_it(
        self, tmp_path: Path
    ) -> None:
        # Nobody is expected to, but nothing stops them: dates as
        # dates, Positions as numbers, one fact per line.
        write_state(_path(tmp_path), TOLD)
        text = _path(tmp_path).read_text()
        assert '"position": 3' in text
        assert "2026-08-26" in text


class TestTheLabels:
    def test_what_a_garment_was_replaced_with_outlives_the_file(
        self, tmp_path: Path
    ) -> None:
        told = replace_(
            get_default_state(TODAY),
            "office.shirt.White",
            "cream",
            "#fffdd0",
        )
        write_state(_path(tmp_path), told)
        assert read_state(_path(tmp_path), TODAY) == told

    def test_only_what_was_replaced_is_written_down(
        self, tmp_path: Path
    ) -> None:
        # The given Labels go back underneath on the way in, so
        # writing them out again would only be the file repeating
        # itself.
        told = replace_(
            get_default_state(TODAY), "pants.Blue", "navy", "#1f2a44"
        )
        write_state(_path(tmp_path), told)
        text = _path(tmp_path).read_text()
        assert '"pants.0": "navy"' in text
        assert '"pants.1"' not in text

    def test_a_file_with_no_told_labels_answers_with_full_names(
        self, tmp_path: Path
    ) -> None:
        # The live file, which is why the given Labels could become
        # full names without converting it.
        _path(tmp_path).write_text(
            _document("{}").replace(
                '"overrides": {}', '"overrides": {}, "labels": {}'
            )
        )
        outfit = answer(
            read_state(_path(tmp_path), TODAY), TODAY, {}
        ).outfit
        assert (outfit.shirt.label, outfit.pants.label) == (
            "White",
            "Blue",
        )

    def test_a_garment_a_file_says_nothing_about_reads_as_given(
        self, tmp_path: Path
    ) -> None:
        # Which is what lets a file written before a Garment existed
        # go on reading.
        _path(tmp_path).write_text(_document("{}"))
        assert (
            read_state(_path(tmp_path), TODAY).labels
            == build_default_labels()
        )


class TestTheColors:
    TOLD = replace(
        get_default_state(TODAY),
        colors={
            **build_default_colors(),
            "office.shirt.0": ("#fffdd0", None),
            "home.shirt.0": ("#ffffff", "#ff0000"),
        },
    )

    def test_a_told_color_outlives_the_file(
        self, tmp_path: Path
    ) -> None:
        write_state(_path(tmp_path), self.TOLD)
        assert read_state(_path(tmp_path), TODAY) == self.TOLD

    def test_only_what_was_told_is_written_down(
        self, tmp_path: Path
    ) -> None:
        write_state(_path(tmp_path), self.TOLD)
        text = _path(tmp_path).read_text()
        assert '"office.shirt.0"' in text
        assert '"home.shirt.0"' in text
        assert '"pants.0"' not in text

    def test_a_file_without_colors_reads_the_given_ones(
        self, tmp_path: Path
    ) -> None:
        _path(tmp_path).write_text(_document("{}"))
        assert (
            read_state(_path(tmp_path), TODAY).colors
            == build_default_colors()
        )


class TestTheOuterwearAnchor:
    def test_it_is_written_beside_the_shirt_anchors(
        self, tmp_path: Path
    ) -> None:
        write_state(_path(tmp_path), TOLD)
        assert '"outerwear"' in _path(tmp_path).read_text()

    def test_a_file_written_before_it_reads_as_the_given_one(
        self, tmp_path: Path
    ) -> None:
        # So nothing has to be migrated: Position 0 on the home
        # Anchor's date, which the file has already pinned -- today
        # would move it with every read.
        _path(tmp_path).write_text(_document("{}"))
        assert [
            read_state(_path(tmp_path), today).anchors[
                Rotation.OUTERWEAR
            ]
            for today in (TODAY, WED26)
        ] == [Anchor(TODAY, 0)] * 2


class TestTheOfficeWeekdaysAndTheColdThreshold:
    def test_they_are_written_as_two_named_facts(
        self, tmp_path: Path
    ) -> None:
        write_state(_path(tmp_path), TOLD)
        text = _path(tmp_path).read_text()
        assert (
            '"office_weekdays": [\n    "tue",\n    "thu",\n    "sat"'
            in (text)
        )
        assert '"cold_threshold": 55.5' in text

    def test_a_file_written_before_them_reads_as_the_given_ones(
        self, tmp_path: Path
    ) -> None:
        _path(tmp_path).write_text(_document("{}"))
        state = read_state(_path(tmp_path), TODAY)
        assert state.office_weekdays == DEFAULT_OFFICE_WEEKDAYS
        assert state.cold_threshold == DEFAULT_COLD_THRESHOLD


class TestAMissingFile:
    def test_it_reads_as_the_given_anchors_with_no_overrides(
        self, tmp_path: Path
    ) -> None:
        assert read_state(_path(tmp_path), TODAY) == get_default_state(
            TODAY
        )

    def test_reading_creates_nothing(self, tmp_path: Path) -> None:
        absent = tmp_path / "absent"
        read_state(absent / "state.json", TODAY)
        assert not absent.exists()

    def test_the_directory_arrives_with_the_first_write(
        self, tmp_path: Path
    ) -> None:
        absent = tmp_path / "absent"
        write_state(absent / "state.json", get_default_state(TODAY))
        assert (absent / "state.json").exists()


class TestTheFirstWritePinsTheAnchors:
    def test_until_then_they_move_with_today(
        self, tmp_path: Path
    ) -> None:
        given = get_default_state(TOMORROW)
        assert read_state(_path(tmp_path), TOMORROW) == given

    def test_afterwards_they_stand_still(self, tmp_path: Path) -> None:
        write_state(_path(tmp_path), get_default_state(TODAY))
        pinned = get_default_state(TODAY)
        assert read_state(_path(tmp_path), TOMORROW) == pinned

    def test_look_ahead_matches_the_date_it_looked_at(
        self, tmp_path: Path
    ) -> None:
        # Asked today about the Wednesday, and asked on the Wednesday
        # about the Wednesday, with nothing recorded in between.
        write_state(_path(tmp_path), get_default_state(TODAY))
        looked = answer(read_state(_path(tmp_path), TODAY), WED26, {})
        arrived = answer(read_state(_path(tmp_path), WED26), WED26, {})
        assert looked == arrived


class TestAFileThatDoesNotReadBack:
    @pytest.mark.parametrize(
        "document",
        [
            "",
            "{}",
            '{"anchors": [], "overrides": {}}',
            '{"anchors": {"office": {"position": 0}}, "overrides": {}}',
            _document('{"2026-08-26": "brunch"}'),
            _document('{"not-a-date": "home"}'),
            _document("{}").replace(
                "}}, ", '}}, "office_weekdays": ["someday"], ', 1
            ),
            _document("{}").replace(
                "}}, ", '}}, "cold_threshold": "brisk", ', 1
            ),
            "]not json at all[",
        ],
    )
    def test_it_is_an_error_naming_the_file(
        self, tmp_path: Path, document: str
    ) -> None:
        _path(tmp_path).write_text(document)
        with pytest.raises(What2wearError, match=r"state\.json"):
            read_state(_path(tmp_path), TODAY)


class TestAWriteThatFailsPartway:
    def test_it_leaves_the_previous_state_intact(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The whole point of the temporary file: a machine that goes
        # away between opening the new State and getting it onto the
        # disk must not be observable, which is what the old
        # append-only log gave free.
        write_state(_path(tmp_path), TOLD)
        monkeypatch.setattr(store.os, "fsync", _went_away)
        with pytest.raises(RuntimeError):
            write_state(_path(tmp_path), replace(TOLD, overrides={}))
        assert read_state(_path(tmp_path), TODAY) == TOLD

    def test_the_target_is_only_ever_moved_onto(
        self, tmp_path: Path
    ) -> None:
        # Nothing is written to the State file itself, so there is no
        # window in which it holds half a document.
        write_state(_path(tmp_path), TOLD)
        before = _path(tmp_path).stat().st_ino
        write_state(_path(tmp_path), get_default_state(TODAY))
        assert _path(tmp_path).stat().st_ino != before


def _path(state_dir: Path) -> Path:
    return state_dir / "state.json"


def _went_away(descriptor: int) -> None:
    del descriptor
    message = "the machine went away"
    raise RuntimeError(message)
