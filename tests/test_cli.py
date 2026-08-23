"""The shell.

It reads the State, reads the clock and prints -- so that is all this
covers. The Wardrobe is given, so there is nothing to set up and no
fixture closet here: which Shirt a date calls for is the core's
business, and these assert on what gets rendered and what gets
recorded.

Dates are taken relative to the real today, because the shell reads
the real clock and `--on` is measured against it.
"""

from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest

from what2wear.cli import run

MON, SAT = 0, 5
LINES = ("shirt", "pants", "sweater", "shoes")


def test_a_bare_invocation_prints_todays_day_and_outfit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run([], state_dir=tmp_path) == 0
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
    assert run([], state_dir=absent) == 0
    assert "shirt" in capsys.readouterr().out
    assert not absent.exists()


def test_a_future_date_prints_that_date(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    day = _today() + timedelta(days=400)
    assert run(["--on", day.isoformat()], state_dir=tmp_path) == 0
    assert f"{day:%a %d %b %Y}" in capsys.readouterr().out


def test_a_past_date_answers_and_says_what_the_answer_is(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Derivable and offered, but a Reset rewrites where a Rotation
    # stood, so the note is what stops it reading as wear history.
    day = _today() - timedelta(days=1)
    assert run(["--on", day.isoformat()], state_dir=tmp_path) == 0
    out = capsys.readouterr().out
    assert f"{day:%a %d %b %Y}" in out
    assert "not what was worn" in out


def test_today_itself_is_not_the_past(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(["--on", _today().isoformat()], state_dir=tmp_path) == 0
    out = capsys.readouterr().out
    assert f"{_today():%a %d %b %Y}" in out
    assert "not what was worn" not in out


def test_an_unavoidable_repeat_is_called_out(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # A fourth Office Day in the Week, which the three office sweaters
    # and their Fallbacks cannot cover however the Week is walked.
    assert _run("go-in", _next(SAT), tmp_path) == 0
    assert "already worn this week" in capsys.readouterr().out


def test_a_malformed_date_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        run(["--on", "the 21st"], state_dir=tmp_path)


class TestRecordingADayTypeOverride:
    def test_staying_home_answers_from_the_home_closet(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monday = _next(MON)
        assert _run("stay-home", monday, tmp_path) == 0
        out = capsys.readouterr().out
        assert f"{monday:%a %d %b %Y} - home day" in out

    def test_going_in_answers_from_the_office_closet(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        saturday = _next(SAT)
        assert _run("go-in", saturday, tmp_path) == 0
        out = capsys.readouterr().out
        assert f"{saturday:%a %d %b %Y} - office day" in out

    def test_the_date_defaults_to_today(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert _run("stay-home", None, tmp_path) == 0
        assert f"{_today():%a %d %b %Y}" in capsys.readouterr().out
        assert _today().isoformat() in _state(tmp_path).read_text()

    def test_what_was_recorded_is_said_back(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert _run("go-in", _next(SAT), tmp_path) == 0
        assert "recorded" in capsys.readouterr().out

    def test_a_recorded_override_changes_a_later_invocation(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monday = _next(MON)
        assert _ask(monday, tmp_path) == 0
        assert "office day" in capsys.readouterr().out
        assert _run("stay-home", monday, tmp_path) == 0
        capsys.readouterr()
        assert _ask(monday, tmp_path) == 0
        assert "home day" in capsys.readouterr().out

    def test_an_earlier_record_survives_a_later_one(
        self, tmp_path: Path
    ) -> None:
        monday, saturday = _next(MON), _next(SAT)
        _run("stay-home", monday, tmp_path)
        _run("go-in", saturday, tmp_path)
        recorded = _state(tmp_path).read_text()
        assert monday.isoformat() in recorded
        assert saturday.isoformat() in recorded

    def test_recording_the_opposite_replaces_what_was_said(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monday = _next(MON)
        _run("stay-home", monday, tmp_path)
        assert _run("go-in", monday, tmp_path) == 0
        capsys.readouterr()
        assert _ask(monday, tmp_path) == 0
        assert "office day" in capsys.readouterr().out

    def test_the_directory_arrives_with_the_first_record(
        self, tmp_path: Path
    ) -> None:
        absent = tmp_path / "absent"
        assert _run("stay-home", None, absent) == 0
        assert _state(absent).exists()

    def test_an_unreadable_state_fails_with_a_clear_message(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _state(tmp_path).write_text("overrides:\n  2026-08-26: gala\n")
        assert _ask(_next(MON), tmp_path) == 2
        assert "state file" in capsys.readouterr().err

    def test_a_past_date_can_still_be_recorded_against(
        self, tmp_path: Path
    ) -> None:
        # Correcting what last Monday was is what parks the
        # rotation into this week.
        monday = _next(MON) - timedelta(days=7)
        assert _run("stay-home", monday, tmp_path) == 0
        assert monday.isoformat() in _state(tmp_path).read_text()

    def test_either_side_of_the_command_names_the_same_date(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # The subcommand's own default must not overwrite an `--on`
        # given ahead of it, which would silently record today.
        saturday = _next(SAT)
        for argv in (
            ["--on", saturday.isoformat(), "go-in"],
            ["go-in", "--on", saturday.isoformat()],
        ):
            assert run(argv, state_dir=tmp_path) == 0
            assert f"recorded {saturday}" in capsys.readouterr().out


class TestRecordingAReset:
    def test_a_bare_reset_says_what_it_did(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run(["reset"], state_dir=tmp_path) == 0
        out = capsys.readouterr().out
        assert "recorded" in out
        assert "shirt rotation reset" in out

    def test_a_shirt_the_day_does_not_have_is_refused(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Neither Closet holds it, so today's kind cannot matter.
        assert run(["reset", "nonesuch"], state_dir=tmp_path) == 2
        assert "nonesuch" in capsys.readouterr().err
        assert not _state(tmp_path).exists()

    def test_a_recorded_reset_moves_the_shirt_on(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run([], state_dir=tmp_path) == 0
        before = _shirt(capsys.readouterr().out)
        assert run(["reset"], state_dir=tmp_path) == 0
        assert _shirt(capsys.readouterr().out) != before

    def test_a_reset_outlives_the_invocation_that_made_it(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run(["reset"], state_dir=tmp_path) == 0
        moved = _shirt(capsys.readouterr().out)
        assert run([], state_dir=tmp_path) == 0
        assert _shirt(capsys.readouterr().out) == moved

    def test_a_reset_can_name_the_date_it_moves(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # A bare Reset moves the named date on by one, and the
        # Rotation comes with it rather than snapping back.
        monday = _next(MON) + timedelta(days=7)
        assert _ask(monday, tmp_path) == 0
        before = _shirt(capsys.readouterr().out)
        assert _reset(None, monday, tmp_path) == 0
        capsys.readouterr()
        assert _ask(monday, tmp_path) == 0
        assert _shirt(capsys.readouterr().out) != before

    def test_the_closet_comes_from_the_date_it_acts_on(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # `striped` is an office Shirt and the home Closet has no
        # such Label, so the date alone decides which is searched.
        assert _reset("striped", _next(MON), tmp_path) == 0
        capsys.readouterr()
        assert _reset("striped", _next(SAT), tmp_path) == 2
        assert "no home shirt" in capsys.readouterr().err


def _run(command: str, on: date | None, state_dir: Path) -> int:
    return run(
        [command, *([] if on is None else ["--on", on.isoformat()])],
        state_dir=state_dir,
    )


def _reset(shirt: str | None, on: date, state_dir: Path) -> int:
    named = [] if shirt is None else [shirt]
    return run(
        ["reset", *named, "--on", on.isoformat()], state_dir=state_dir
    )


def _ask(on: date, state_dir: Path) -> int:
    return run(["--on", on.isoformat()], state_dir=state_dir)


def _state(state_dir: Path) -> Path:
    return state_dir / "state.yaml"


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
