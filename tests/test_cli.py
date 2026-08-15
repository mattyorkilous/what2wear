"""The shell. It reads a file, reads the clock and prints -- so that is all this covers."""

from datetime import date
from pathlib import Path

import pytest

from what2wear.cli import main, render
from what2wear.model import DayType, Outfit, Response

CONFIG = Path(__file__).parent.parent / "what2wear.yaml"


def test_a_date_argument_prints_that_dates_outfit(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--on", "2026-08-21", "--config", str(CONFIG)]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "Fri 21 Aug 2026 - office day",
        "  shirt  black",
        "  pants  tan",
    ]


def test_a_bare_invocation_prints_something_for_today(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["--config", str(CONFIG)]) == 0
    assert f"{date.today():%a %d %b %Y}" in capsys.readouterr().out


def test_a_bad_config_path_fails_with_a_clear_message(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["--config", "nowhere.yaml"]) == 2
    assert "no config file at nowhere.yaml" in capsys.readouterr().err


def test_the_default_config_can_be_pointed_somewhere_else(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("WHAT2WEAR_CONFIG", str(CONFIG))
    monkeypatch.chdir(tmp_path)
    assert main(["--on", "2026-08-21"]) == 0
    assert "shirt  black" in capsys.readouterr().out


def test_an_explicit_config_wins_over_the_environment(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("WHAT2WEAR_CONFIG", str(CONFIG))
    assert main(["--config", "nowhere.yaml"]) == 2
    assert "no config file at nowhere.yaml" in capsys.readouterr().err


def test_a_malformed_date_is_rejected() -> None:
    with pytest.raises(SystemExit):
        main(["--on", "the 21st"])


def test_home_days_render_as_home_days() -> None:
    response = Response(
        on=date(2026, 8, 22),
        day_type=DayType.HOME,
        outfit=Outfit(shirt="red", pants="blue"),
    )
    assert render(response).splitlines()[0] == "Sat 22 Aug 2026 - home day"
