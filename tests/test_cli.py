"""The shell.

It reads the log, reads the clock and prints -- so that is all this
covers. The Wardrobe is given, so there is nothing to set up and no
fixture closet here: which Shirt a date calls for is the core's
business, and these assert on what gets rendered and what gets
recorded.

Dates are taken relative to the real today, because the shell reads
the real clock and the past is not answerable.
"""

from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest

from what2wear.cli import main

MON, SAT = 0, 5
LINES = ("shirt", "pants", "sweater", "shoes")


def test_a_bare_invocation_prints_todays_day_and_outfit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main([], state_dir=tmp_path) == 0
    out = capsys.readouterr().out
    assert f"{_today():%a %d %b %Y}" in out
    assert " day" in out.splitlines()[0]
    assert [line.split()[0] for line in out.splitlines()[1:5]] == list(
        LINES
    )


def test_a_fresh_installation_answers_and_leaves_nothing_behind(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Nothing to configure, so nothing to look for and no directory to
    # make until something is recorded.
    absent = tmp_path / "absent"
    assert main([], state_dir=absent) == 0
    assert "shirt" in capsys.readouterr().out
    assert not absent.exists()


def test_a_future_date_prints_that_date(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    day = _today() + timedelta(days=400)
    assert main(["--on", day.isoformat()], state_dir=tmp_path) == 0
    assert f"{day:%a %d %b %Y}" in capsys.readouterr().out


def test_a_past_date_is_refused_with_a_reason(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    day = _today() - timedelta(days=1)
    assert main(["--on", day.isoformat()], state_dir=tmp_path) == 2
    err = capsys.readouterr().err
    assert day.isoformat() in err
    assert "past is not answerable" in err


def test_an_unavoidable_repeat_is_called_out(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # A fourth Office Day in the Week, which the three office sweaters
    # and their Fallbacks cannot cover however the Week is walked.
    assert _run("--go-in", _next(SAT), tmp_path) == 0
    assert "already worn this week" in capsys.readouterr().out


def test_a_malformed_date_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        main(["--on", "the 21st"], state_dir=tmp_path)


class TestRecordingADayTypeOverride:
    def test_staying_home_answers_from_the_home_closet(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monday = _next(MON)
        assert _run("--stay-home", monday, tmp_path) == 0
        out = capsys.readouterr().out
        assert f"{monday:%a %d %b %Y} - home day" in out

    def test_going_in_answers_from_the_office_closet(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        saturday = _next(SAT)
        assert _run("--go-in", saturday, tmp_path) == 0
        out = capsys.readouterr().out
        assert f"{saturday:%a %d %b %Y} - office day" in out

    def test_the_date_defaults_to_today(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert _run("--stay-home", None, tmp_path) == 0
        assert f"{_today():%a %d %b %Y}" in capsys.readouterr().out
        assert _today().isoformat() in _log(tmp_path).read_text()

    def test_what_was_recorded_is_said_back(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert _run("--go-in", _next(SAT), tmp_path) == 0
        assert "recorded" in capsys.readouterr().out

    def test_a_recorded_override_changes_a_later_invocation(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monday = _next(MON)
        assert _run("--on", monday, tmp_path) == 0
        assert "office day" in capsys.readouterr().out
        assert _run("--stay-home", monday, tmp_path) == 0
        capsys.readouterr()
        assert _run("--on", monday, tmp_path) == 0
        assert "home day" in capsys.readouterr().out

    def test_the_log_is_appended_to_rather_than_rewritten(
        self, tmp_path: Path
    ) -> None:
        _run("--stay-home", _next(MON), tmp_path)
        _run("--go-in", _next(SAT), tmp_path)
        assert len(_log(tmp_path).read_text().splitlines()) == 2

    def test_the_directory_arrives_with_the_first_record(
        self, tmp_path: Path
    ) -> None:
        absent = tmp_path / "absent"
        assert _run("--stay-home", None, absent) == 0
        assert _log(absent).exists()

    def test_an_unreadable_log_fails_with_a_clear_message(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _log(tmp_path).write_text("not a decision log\n")
        assert _run("--on", _next(MON), tmp_path) == 2
        assert "decision log" in capsys.readouterr().err

    def test_a_past_date_can_still_be_recorded_against(
        self, tmp_path: Path
    ) -> None:
        # Only the question is refused. Correcting what last Monday
        # was is what parks the rotation into this week.
        monday = _next(MON) - timedelta(days=7)
        assert _run("--stay-home", monday, tmp_path) == 0
        assert monday.isoformat() in _log(tmp_path).read_text()

    def test_asking_and_recording_are_not_combined(
        self, tmp_path: Path
    ) -> None:
        with pytest.raises(SystemExit):
            main(
                ["--on", _next(MON).isoformat(), "--stay-home"],
                state_dir=tmp_path,
            )


class TestRecordingAReset:
    def test_a_bare_reset_records_a_shift_of_one(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert main(["--reset"], state_dir=tmp_path) == 0
        assert "recorded" in capsys.readouterr().out
        assert '"rotation": "shirt"' in _log(tmp_path).read_text()
        assert '"offset": 1' in _log(tmp_path).read_text()

    def test_a_shirt_the_day_does_not_have_is_refused(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Neither Closet holds it, so today's kind cannot matter.
        assert main(["--reset", "nonesuch"], state_dir=tmp_path) == 2
        assert "nonesuch" in capsys.readouterr().err
        assert not _log(tmp_path).exists()

    def test_a_recorded_reset_moves_the_shirt_on(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert main([], state_dir=tmp_path) == 0
        before = _shirt(capsys.readouterr().out)
        assert main(["--reset"], state_dir=tmp_path) == 0
        assert _shirt(capsys.readouterr().out) != before

    def test_asking_and_resetting_are_not_combined(
        self, tmp_path: Path
    ) -> None:
        with pytest.raises(SystemExit):
            main(
                ["--on", _next(MON).isoformat(), "--reset"],
                state_dir=tmp_path,
            )


def _run(flag: str, on: date | None, state_dir: Path) -> int:
    return main(
        [flag, *([] if on is None else [on.isoformat()])],
        state_dir=state_dir,
    )


def _log(state_dir: Path) -> Path:
    return state_dir / "decisions.jsonl"


def _shirt(out: str) -> str:
    return next(
        line.split()[1]
        for line in out.splitlines()
        if line.startswith("  shirt")
    )


def _next(weekday: int) -> date:
    """Give the next date of that weekday, today included."""
    today = _today()
    return today + timedelta(days=(weekday - today.weekday()) % 7)


def _today() -> date:
    """Read the wearer's own today, the way the shell does."""
    return datetime.now(UTC).astimezone().date()
