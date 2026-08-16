"""The shell.

It reads a file, reads the clock and prints -- so that is all this
covers. The config below is the shell's own, not the shipped wardrobe:
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

home:
  anchor: { date: 2026-08-15, shirt: tee }
  shirts:
    - { name: tee, pants: shorts }
"""


@pytest.fixture
def config(tmp_path: Path) -> Path:
    # Not in tmp_path itself, so a test can chdir there and still have
    # no config on the default relative path.
    directory = tmp_path / "closet"
    directory.mkdir()
    path = directory / "what2wear.yaml"
    path.write_text(CONFIG_TEXT)
    return path


@pytest.mark.parametrize(
    ("on", "expected"),
    [
        (
            "2026-08-21",
            [
                "Fri 21 Aug 2026 - office day",
                "  shirt  oxford",
                "  pants  tan",
            ],
        ),
        (
            "2026-08-22",
            [
                "Sat 22 Aug 2026 - home day",
                "  shirt  tee",
                "  pants  shorts",
            ],
        ),
    ],
)
def test_a_date_argument_prints_that_dates_day_and_outfit(
    on: str,
    expected: list[str],
    config: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["--on", on, "--config", str(config)]) == 0
    assert capsys.readouterr().out.splitlines() == expected


def test_a_bare_invocation_prints_something_for_today(
    config: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["--config", str(config)]) == 0
    assert f"{date.today():%a %d %b %Y}" in capsys.readouterr().out


def test_a_bad_config_path_fails_with_a_clear_message(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["--config", "nowhere.yaml"]) == 2
    assert "no config file at nowhere.yaml" in capsys.readouterr().err


def test_the_default_config_can_be_pointed_somewhere_else(
    config: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("WHAT2WEAR_CONFIG", str(config))
    monkeypatch.chdir(tmp_path)
    assert main(["--on", "2026-08-21"]) == 0
    assert "shirt  oxford" in capsys.readouterr().out


def test_an_explicit_config_wins_over_the_environment(
    config: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WHAT2WEAR_CONFIG", str(config))
    assert main(["--config", "nowhere.yaml"]) == 2
    assert "no config file at nowhere.yaml" in capsys.readouterr().err


def test_a_malformed_date_is_rejected() -> None:
    with pytest.raises(SystemExit):
        main(["--on", "the 21st"])
