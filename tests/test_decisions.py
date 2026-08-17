"""The decision log: append-only, tool-owned, read back as State.

The shell's half of Day Type Overrides. The core's half -- what an
Override does to a Rotation -- is `test_overrides.py`.
"""

from datetime import date
from pathlib import Path

import pytest

from what2wear.decisions import (
    DecisionsError,
    append_decision,
    load_decisions,
)
from what2wear.model import DayType, DayTypeOverride

STAY_HOME = DayTypeOverride(date(2026, 8, 19), DayType.HOME)
GO_IN = DayTypeOverride(date(2026, 8, 22), DayType.OFFICE)


class TestLoading:
    def test_a_log_that_does_not_exist_yet_is_an_empty_one(
        self, tmp_path: Path
    ) -> None:
        assert load_decisions(tmp_path / "nothing.jsonl") == ()

    def test_what_was_appended_comes_back(self, tmp_path: Path) -> None:
        path = tmp_path / "decisions.jsonl"
        append_decision(path, STAY_HOME)
        append_decision(path, GO_IN)
        assert load_decisions(path) == (STAY_HOME, GO_IN)

    def test_appending_never_rewrites_what_is_already_there(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "decisions.jsonl"
        append_decision(path, STAY_HOME)
        before = path.read_text()
        append_decision(path, GO_IN)
        assert path.read_text().startswith(before)

    def test_one_record_per_line(self, tmp_path: Path) -> None:
        path = tmp_path / "decisions.jsonl"
        append_decision(path, STAY_HOME)
        append_decision(path, GO_IN)
        assert len(path.read_text().splitlines()) == 2


class TestABadLog:
    @pytest.mark.parametrize(
        "text",
        [
            "not json at all\n",
            '{"on": "2026-08-19"}\n',
            '{"on": "the 19th", "day_type": "home"}\n',
            '{"on": "2026-08-19", "day_type": "beach"}\n',
        ],
    )
    def test_an_unreadable_log_fails_with_a_clear_message(
        self, text: str, tmp_path: Path
    ) -> None:
        path = tmp_path / "decisions.jsonl"
        path.write_text(text)
        with pytest.raises(DecisionsError, match=str(path)):
            load_decisions(path)

    def test_a_log_that_cannot_be_written_fails_the_same_way(
        self, tmp_path: Path
    ) -> None:
        # A missing parent directory, rather than a permission bit, so
        # the test behaves the same when run as root.
        path = tmp_path / "nowhere" / "decisions.jsonl"
        with pytest.raises(DecisionsError, match=str(path)):
            append_decision(path, STAY_HOME)
