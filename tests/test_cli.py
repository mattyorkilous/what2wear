"""The shell.

It reads a file, reads the clock and prints -- so that is all this
covers. The Wardrobe below is the shell's own, not the example one:
what a real closet holds is `test_config.py`'s business, and editing
it must not break these.
"""

from datetime import date
from pathlib import Path

import pytest

from what2wear.cli import main

CONFIG_TEXT = """
office_weekdays: [mon, wed, fri]

office:
  anchor: { date: 2026-08-17, shirt: oxford }
  shirts:
    - { name: oxford, pants: tan }
    - { name: chambray, pants: navy }
    - { name: denim, pants: olive }
  pants:
    tan: { sweater: cream, shoes: brogues, fallback: charcoal }
    navy: { sweater: charcoal, shoes: loafers }
    olive: { sweater: rust, shoes: boots }

home:
  anchor: { date: 2026-08-15, shirt: tee }
  shirts:
    - { name: tee, pants: shorts }
  pants:
    shorts: { sweater: hoodie, jacket: anorak, shoes: sandals }
"""

# Two office shirts and three office days, so the week runs out of
# sweaters on the Friday however it is walked.
REPEATING_CONFIG = CONFIG_TEXT.replace(
    "    - { name: denim, pants: olive }\n", ""
).replace("    olive: { sweater: rust, shoes: boots }\n", "")


@pytest.fixture
def config_dir(tmp_path: Path) -> Path:
    """A configured installation: a Wardrobe where the tool looks for
    one, and the decision log that will land beside it."""
    (tmp_path / "config.yaml").write_text(CONFIG_TEXT)
    return tmp_path


@pytest.mark.parametrize(
    ("on", "expected"),
    [
        (
            "2026-08-21",
            [
                "Fri 21 Aug 2026 - office day",
                "  shirt    denim",
                "  pants    olive",
                "  sweater  rust",
                "  shoes    boots",
            ],
        ),
        (
            "2026-08-22",
            [
                "Sat 22 Aug 2026 - home day",
                "  shirt    tee",
                "  pants    shorts",
                "  sweater  hoodie",
                "  shoes    sandals",
            ],
        ),
    ],
)
def test_a_date_argument_prints_that_dates_day_and_outfit(
    on: str,
    expected: list[str],
    config_dir: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["--on", on], config_dir=config_dir) == 0
    assert capsys.readouterr().out.splitlines() == expected


def test_a_bare_invocation_prints_something_for_today(
    config_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main([], config_dir=config_dir) == 0
    assert f"{date.today():%a %d %b %Y}" in capsys.readouterr().out


def test_an_unavoidable_repeat_is_called_out(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "config.yaml").write_text(REPEATING_CONFIG)
    assert main(["--on", "2026-08-21"], config_dir=tmp_path) == 0
    assert "already worn this week" in capsys.readouterr().out


def test_a_malformed_date_is_rejected(config_dir: Path) -> None:
    with pytest.raises(SystemExit):
        main(["--on", "the 21st"], config_dir=config_dir)


class TestTheFirstRun:
    def test_no_wardrobe_names_the_path_and_the_example(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert main([], config_dir=tmp_path) == 2
        err = capsys.readouterr().err
        assert str(tmp_path / "config.yaml") in err
        assert "example.yaml" in err

    def test_a_malformed_wardrobe_reports_its_parse_error(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        (tmp_path / "config.yaml").write_text("office: [unclosed")
        assert main([], config_dir=tmp_path) == 2
        err = capsys.readouterr().err
        assert "is not valid YAML" in err
        assert "example.yaml" not in err

    def test_nothing_creates_the_directory(
        self, tmp_path: Path
    ) -> None:
        absent = tmp_path / "absent"
        assert main([], config_dir=absent) == 2
        assert not absent.exists()

    def test_a_recording_run_writes_no_log_either(
        self, tmp_path: Path
    ) -> None:
        # The Wardrobe is read before anything is appended, so an
        # unconfigured installation leaves nothing behind.
        assert main(["--stay-home"], config_dir=tmp_path) == 2
        assert list(tmp_path.iterdir()) == []


class TestRecordingADayTypeOverride:
    def test_staying_home_answers_from_the_home_closet(
        self, config_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert _run("--stay-home", "2026-08-19", config_dir) == 0
        out = capsys.readouterr().out
        assert "Wed 19 Aug 2026 - home day" in out
        assert "shirt    tee" in out

    def test_going_in_answers_from_the_office_closet(
        self, config_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert _run("--go-in", "2026-08-22", config_dir) == 0
        out = capsys.readouterr().out
        assert "Sat 22 Aug 2026 - office day" in out
        assert "shirt    oxford" in out

    def test_the_date_defaults_to_today(
        self, config_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert _run("--stay-home", None, config_dir) == 0
        assert f"{date.today():%a %d %b %Y}" in capsys.readouterr().out
        assert date.today().isoformat() in _log(config_dir).read_text()

    def test_what_was_recorded_is_said_back(
        self, config_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert _run("--go-in", "2026-08-22", config_dir) == 0
        assert "recorded" in capsys.readouterr().out

    def test_a_recorded_override_changes_a_later_invocation(
        self, config_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Friday would be denim; with Wednesday spent at home the
        # office rotation is parked, so Friday wears Wednesday's.
        assert _run("--on", "2026-08-21", config_dir) == 0
        assert "shirt    denim" in capsys.readouterr().out
        assert _run("--stay-home", "2026-08-19", config_dir) == 0
        capsys.readouterr()
        assert _run("--on", "2026-08-21", config_dir) == 0
        assert "shirt    chambray" in capsys.readouterr().out

    def test_the_log_is_appended_to_and_the_wardrobe_untouched(
        self, config_dir: Path
    ) -> None:
        config = config_dir / "config.yaml"
        before = config.read_text()
        _run("--stay-home", "2026-08-19", config_dir)
        _run("--go-in", "2026-08-22", config_dir)
        assert len(_log(config_dir).read_text().splitlines()) == 2
        assert config.read_text() == before

    def test_an_unreadable_log_fails_with_a_clear_message(
        self, config_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _log(config_dir).write_text("not a decision log\n")
        assert _run("--on", "2026-08-21", config_dir) == 2
        assert "decision log" in capsys.readouterr().err

    def test_asking_and_recording_are_not_combined(
        self, config_dir: Path
    ) -> None:
        with pytest.raises(SystemExit):
            main(
                ["--on", "2026-08-21", "--stay-home"],
                config_dir=config_dir,
            )


def _run(flag: str, on: str | None, config_dir: Path) -> int:
    return main(
        [flag, *([] if on is None else [on])], config_dir=config_dir
    )


def _log(config_dir: Path) -> Path:
    return config_dir / "decisions.jsonl"
