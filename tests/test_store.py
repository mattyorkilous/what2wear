"""The State file: the tool's own, and the only thing it writes.

The shell's half of everything the tool is told. What a recorded
command does to a Rotation is `test_overrides.py` and
`test_resets.py`; that it survives being written down is this one's.
"""

from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from what2wear import store
from what2wear.core import answer
from what2wear.model import DayType, State, default_state
from what2wear.store import StateError, read_state, write_state
from what2wear.wardrobe import Anchor

TODAY = date(2026, 8, 22)
TOMORROW = date(2026, 8, 23)
WED26 = date(2026, 8, 26)

TOLD = State(
    office_anchor=Anchor(TODAY, 3),
    home_anchor=Anchor(WED26, 7),
    overrides={WED26: DayType.HOME, TOMORROW: DayType.OFFICE},
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
        write_state(_path(tmp_path), default_state(TODAY))
        assert read_state(_path(tmp_path), TODAY) == default_state(
            TODAY
        )

    def test_it_is_legible_to_a_person_who_opens_it(
        self, tmp_path: Path
    ) -> None:
        # Nobody is expected to, but nothing stops them: dates as
        # dates, Positions as numbers, and no back-references.
        write_state(_path(tmp_path), TOLD)
        text = _path(tmp_path).read_text()
        assert "position: 3" in text
        assert "2026-08-26" in text
        assert "*id" not in text


class TestAMissingFile:
    def test_it_reads_as_the_given_anchors_with_no_overrides(
        self, tmp_path: Path
    ) -> None:
        assert read_state(_path(tmp_path), TODAY) == default_state(
            TODAY
        )

    def test_reading_creates_nothing(self, tmp_path: Path) -> None:
        absent = tmp_path / "absent"
        read_state(absent / "state.yaml", TODAY)
        assert not absent.exists()

    def test_the_directory_arrives_with_the_first_write(
        self, tmp_path: Path
    ) -> None:
        absent = tmp_path / "absent"
        write_state(absent / "state.yaml", default_state(TODAY))
        assert (absent / "state.yaml").exists()


class TestTheFirstWritePinsTheAnchors:
    def test_until_then_they_move_with_today(
        self, tmp_path: Path
    ) -> None:
        assert read_state(_path(tmp_path), TOMORROW) == default_state(
            TOMORROW
        )

    def test_afterwards_they_stand_still(self, tmp_path: Path) -> None:
        write_state(_path(tmp_path), default_state(TODAY))
        assert read_state(_path(tmp_path), TOMORROW) == default_state(
            TODAY
        )

    def test_look_ahead_matches_the_date_it_looked_at(
        self, tmp_path: Path
    ) -> None:
        # Asked today about the Wednesday, and asked on the Wednesday
        # about the Wednesday, with nothing recorded in between.
        write_state(_path(tmp_path), default_state(TODAY))
        looked = answer(read_state(_path(tmp_path), TODAY), WED26)
        arrived = answer(read_state(_path(tmp_path), WED26), WED26)
        assert looked == arrived


class TestAFileFromAnEarlierVersion:
    @pytest.mark.parametrize(
        "document",
        [
            "",
            "overrides: {}\n",
            (
                "anchors:\n  office:\n"
                "    date: '2026-08-22'\n    position: 0\n"
            ),
        ],
    )
    def test_what_it_does_not_say_reads_as_given(
        self, tmp_path: Path, document: str
    ) -> None:
        _path(tmp_path).write_text(document)
        assert read_state(_path(tmp_path), TODAY) == default_state(
            TODAY
        )


class TestAFileThatDoesNotReadBack:
    @pytest.mark.parametrize(
        "document",
        [
            "anchors: [not, a, mapping]\n",
            "anchors:\n  office:\n    position: 0\n",
            "overrides:\n  2026-08-26: brunch\n",
            "overrides:\n  not-a-date: home\n",
            "overrides:\n  20260826: home\n",
            "]not yaml at all[\n",
        ],
    )
    def test_it_is_an_error_naming_the_file(
        self, tmp_path: Path, document: str
    ) -> None:
        _path(tmp_path).write_text(document)
        with pytest.raises(StateError, match=r"state\.yaml"):
            read_state(_path(tmp_path), TODAY)


class TestAWriteThatFailsPartway:
    def test_it_leaves_the_previous_state_intact(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The whole point of the temporary file: a crash between
        # opening the new State and finishing it must not be
        # observable, which is what the old append-only log gave free.
        write_state(_path(tmp_path), TOLD)
        monkeypatch.setattr(store, "_write_document", _half_written)
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
        write_state(_path(tmp_path), default_state(TODAY))
        assert _path(tmp_path).stat().st_ino != before


def _path(state_dir: Path) -> Path:
    return state_dir / "state.yaml"


def _half_written(path: Path, document: str) -> None:
    """Stand in for a machine that gave up halfway through a write."""
    path.write_text(document[: len(document) // 2])
    message = "the machine went away"
    raise RuntimeError(message)
