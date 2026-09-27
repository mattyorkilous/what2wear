import re
from datetime import UTC, date, datetime, timedelta
from functools import partial
from pathlib import Path

import pytest

from what2wear import cli
from what2wear.core import HORIZON_DAYS
from what2wear.wardrobe import (
    DEFAULT_COLD_THRESHOLD,
    DEFAULT_OFFICE_WEEKDAYS,
    WEEKDAYS,
)

# No forecast, so no test here touches the network.
run = partial(cli.run, fetch_weather=dict)

MON, TUE, WED, FRI, SAT = 0, 1, 2, 4, 5
OUTERWEAR = ("  sweater", "  jacket")


def test_a_bare_invocation_prints_todays_day_and_outfit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run([], state_dir=tmp_path) == 0
    out = capsys.readouterr().out
    assert f"{_today():%a %d %b %Y}" in out
    assert " day" in out.splitlines()[0]
    shirt, pants, outerwear, shoes = (
        line.split()[0] for line in out.splitlines()[1:5]
    )
    assert (shirt, pants, shoes) == ("shirt", "pants", "shoes")
    assert outerwear in {"sweater", "jacket"}


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


class TestOuterwear:
    def test_a_cold_day_names_its_outerwear(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _run_in(DEFAULT_COLD_THRESHOLD - 10, tmp_path)
        assert "if it's cold" not in _get_outerwear_line(
            capsys.readouterr().out
        )

    def test_a_warm_day_prints_no_outerwear_line(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _run_in(DEFAULT_COLD_THRESHOLD, tmp_path)
        out = capsys.readouterr().out
        assert "  shoes" in out
        assert not any(kind in out for kind in OUTERWEAR)

    def test_an_unknown_day_names_it_if_its_cold(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run([], state_dir=tmp_path) == 0
        assert _get_outerwear_line(capsys.readouterr().out).endswith(
            "if it's cold"
        )

    def test_a_home_jacket_day_prints_a_jacket_line(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Of two Home Days in a row, one is a jacket day.
        saturday = _next(SAT)
        assert _ask(saturday, tmp_path) == 0
        assert _ask(saturday + timedelta(days=1), tmp_path) == 0
        assert "  jacket   " in capsys.readouterr().out

    def test_resolving_it_writes_nothing(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert _run("reset-outerwear", None, tmp_path) == 0
        written = _state(tmp_path).read_text()
        _run_in(DEFAULT_COLD_THRESHOLD - 10, tmp_path)
        capsys.readouterr()
        assert _state(tmp_path).read_text() == written
        assert [path.name for path in tmp_path.iterdir()] == [
            "state.json"
        ]


def test_a_malformed_date_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        run(["--on", "the 21st"], state_dir=tmp_path)


class TestNamingADateWithAWord:
    def test_tomorrow_resolves(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        tomorrow = _today() + timedelta(days=1)
        assert run(["--on", "tomorrow"], state_dir=tmp_path) == 0
        assert f"{tomorrow:%a %d %b %Y}" in capsys.readouterr().out

    def test_yesterday_resolves_and_keeps_the_past_date_note(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        yesterday = _today() - timedelta(days=1)
        assert run(["--on", "yesterday"], state_dir=tmp_path) == 0
        out = capsys.readouterr().out
        assert f"{yesterday:%a %d %b %Y}" in out
        assert "not what was worn" in out

    @pytest.mark.parametrize(
        "word", ["wed", "Wed", "wednesday", "WEDNESDAY"]
    )
    def test_a_weekday_is_spelled_however_it_comes_out(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        word: str,
    ) -> None:
        assert run(["--on", word], state_dir=tmp_path) == 0
        assert f"{_next(WED):%a %d %b %Y}" in capsys.readouterr().out

    @pytest.mark.parametrize("weekday", range(len(WEEKDAYS)))
    def test_a_weekday_lands_on_the_soonest_such_date(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        weekday: int,
    ) -> None:
        # Asserted as the property rather than against the same
        # arithmetic the parser does, which would agree with itself
        # however wrong it was.
        assert run(["--on", WEEKDAYS[weekday]], state_dir=tmp_path) == 0
        landed = _dated(capsys.readouterr().out)
        assert landed.weekday() == weekday
        assert timedelta() <= landed - _today() <= timedelta(days=6)

    def test_todays_own_weekday_is_today(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        today = _today()
        assert (
            run(["--on", WEEKDAYS[today.weekday()]], state_dir=tmp_path)
            == 0
        )
        out = capsys.readouterr().out
        assert f"{today:%a %d %b %Y}" in out
        assert "not what was worn" not in out

    def test_today_is_not_one_of_the_words(
        self, tmp_path: Path
    ) -> None:
        # A bare invocation already means today, so the word would be
        # a second spelling of the default. The asymmetry is the
        # decision, not a gap to be closed later.
        with pytest.raises(SystemExit) as refusal:
            run(["--on", "today"], state_dir=tmp_path)
        assert refusal.value.code == 2

    @pytest.mark.parametrize("word", ["wedding", "monkey", "satchel"])
    def test_a_word_merely_starting_with_one_is_refused(
        self, tmp_path: Path, word: str
    ) -> None:
        # Silently reading a typo as the weekday it starts with would
        # move a reset's anchor to the wrong day without saying so.
        with pytest.raises(SystemExit) as refusal:
            run(["--on", word], state_dir=tmp_path)
        assert refusal.value.code == 2

    def test_a_word_that_is_neither_says_what_is_accepted(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        with pytest.raises(SystemExit) as refusal:
            run(["--on", "nonesuch"], state_dir=tmp_path)
        assert refusal.value.code == 2
        assert "tomorrow" in capsys.readouterr().err

    def test_a_recording_command_takes_one(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        saturday = _next(SAT)
        assert run(["go-in", "--on", "sat"], state_dir=tmp_path) == 0
        assert f"{saturday} - office day" in capsys.readouterr().out

    def test_a_reset_takes_one(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        friday = _next(FRI)
        assert (
            run(
                ["reset", "Light Blue", "--on", "fri"],
                state_dir=tmp_path,
            )
            == 0
        )
        capsys.readouterr()
        assert _ask(friday, tmp_path) == 0
        assert _shirt(capsys.readouterr().out) == "Light Blue"

    def test_a_word_ahead_of_the_command_still_records_today(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # ADR-0008: a subcommand's own default overwrites an `--on`
        # given ahead of it, and a word is no exception.
        assert (
            run(["--on", "tomorrow", "go-in"], state_dir=tmp_path) == 0
        )
        assert f"{_today()} - office day" in capsys.readouterr().out


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
        assert _run(_contrary(), None, tmp_path) == 0
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
        assert _run(_contrary(), None, absent) == 0
        assert _state(absent).exists()

    def test_an_unreadable_state_fails_with_a_clear_message(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        _state(tmp_path).write_text('{"overrides": {"x": "gala"}}')
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


class TestRecordingAReset:
    def test_it_says_what_it_did(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run(["reset", "Light Blue"], state_dir=tmp_path) == 0
        out = capsys.readouterr().out
        assert "recorded" in out
        assert "shirt rotation reset to Light Blue" in out

    def test_naming_no_shirt_is_refused(self, tmp_path: Path) -> None:
        # Both closets hold an `Light Blue`, so the day never decides
        # whether the label is one; leaving it out is the only way
        # `reset` can be typed without one.
        with pytest.raises(SystemExit):
            run(["reset"], state_dir=tmp_path)

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
        assert run(["reset", "Light Blue"], state_dir=tmp_path) == 0
        assert _shirt(capsys.readouterr().out) != before

    def test_a_reset_outlives_the_invocation_that_made_it(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run(["reset", "Light Blue"], state_dir=tmp_path) == 0
        moved = _shirt(capsys.readouterr().out)
        assert run([], state_dir=tmp_path) == 0
        assert _shirt(capsys.readouterr().out) == moved

    def test_a_reset_can_name_the_date_it_moves(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # The Shirt lands on the date named rather than on today.
        monday = _next(MON) + timedelta(days=7)
        assert _reset("Light Blue", monday, tmp_path) == 0
        capsys.readouterr()
        assert _ask(monday, tmp_path) == 0
        assert _shirt(capsys.readouterr().out) == "Light Blue"

    def test_the_closet_comes_from_the_date_it_acts_on(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # `Striped` is an office Shirt and the home Closet has no
        # such Label, so the date alone decides which is searched.
        assert _reset("Striped", _next(MON), tmp_path) == 0
        capsys.readouterr()
        assert _reset("Striped", _next(SAT), tmp_path) == 2
        assert "no home shirt" in capsys.readouterr().err


class TestRecordingAnOuterwearReset:
    def test_it_says_what_it_did(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert _run("reset-outerwear", None, tmp_path) == 0
        out = capsys.readouterr().out
        assert "recorded" in out
        assert "outerwear rotation" in out

    @pytest.mark.parametrize(
        "extra", [["jacket"], ["--on", "2026-09-22"]]
    )
    def test_it_takes_no_argument_and_no_date(
        self, tmp_path: Path, extra: list[str]
    ) -> None:
        # Over two kinds, moving on by one and switching to the other
        # are the same, so there is nothing to name, and it always
        # moves on from today.
        with pytest.raises(SystemExit):
            run(["reset-outerwear", *extra], state_dir=tmp_path)

    def test_it_switches_the_next_home_day(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        saturday = _next(SAT) + timedelta(days=7)
        assert _ask(saturday, tmp_path) == 0
        before = _get_outerwear_line(capsys.readouterr().out)
        assert _run("reset-outerwear", None, tmp_path) == 0
        capsys.readouterr()
        assert _ask(saturday, tmp_path) == 0
        after = _get_outerwear_line(capsys.readouterr().out)
        assert before.split()[0] != after.split()[0]


class TestShowingTheCloset:
    def test_it_lists_both_closets_shirts_in_rotation_order(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run(["show-closet"], state_dir=tmp_path) == 0
        out = capsys.readouterr().out
        assert _shirts(out, "office") == [
            "White",
            "Black",
            "Light Blue",
            "Striped",
            "Dark Blue",
        ]
        assert _shirts(out, "home")[:3] == [
            "White",
            "Brown",
            "Dark Green",
        ]

    def test_it_shows_each_shirts_pants_in_its_own_column(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Which is what makes a legal Swap something to scan for:
        # `White` and `Striped` both wear blue.
        assert run(["show-closet"], state_dir=tmp_path) == 0
        out = capsys.readouterr().out
        assert _get_columns(out, "White")[2] == "Blue"
        assert _get_columns(out, "Striped")[2] == "Blue"
        assert _get_columns(out, "Black")[2] == "Tan"

    def test_it_prints_a_garment_that_can_be_replaced_by(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Copied rather than guessed at: whatever it printed is what
        # `replace` takes.
        assert run(["show-closet"], state_dir=tmp_path) == 0
        garment = _get_columns(capsys.readouterr().out, "Striped")[3]
        assert (
            run(["replace", garment, "check"], state_dir=tmp_path) == 0
        )
        capsys.readouterr()
        assert run(["show-closet"], state_dir=tmp_path) == 0
        assert "check" in _shirts(capsys.readouterr().out, "office")

    def test_it_marks_the_shirt_each_closet_is_due_to_give(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Today's closet marks today's shirt; the other marks the
        # one waiting on its next day, so a Reset can be typed
        # against either without working the date out.
        assert run([], state_dir=tmp_path) == 0
        due = _shirt(capsys.readouterr().out)
        assert run(["show-closet"], state_dir=tmp_path) == 0
        out = capsys.readouterr().out
        assert _marked(out, _todays_closet()) == [due]
        assert len(_marked(out, "office")) == 1
        assert len(_marked(out, "home")) == 1

    def test_the_mark_moves_with_the_rotation(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # `Dark Blue` hangs in both closets, so today's kind cannot
        # decide whether this passes.
        assert run(["show-closet"], state_dir=tmp_path) == 0
        before = _marked(capsys.readouterr().out, _todays_closet())
        assert run(["reset", "Dark Blue"], state_dir=tmp_path) == 0
        capsys.readouterr()
        assert run(["show-closet"], state_dir=tmp_path) == 0
        marked = _marked(capsys.readouterr().out, _todays_closet())
        assert marked == ["Dark Blue"]
        assert before != marked

    def test_it_lists_the_jackets_home_alone_has(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run(["show-closet"], state_dir=tmp_path) == 0
        out = capsys.readouterr().out
        assert "home.jacket.Brown" in out
        assert "office.jacket" not in out

    def test_it_lists_the_pants_both_closets_share_once(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run(["show-closet"], state_dir=tmp_path) == 0
        out = capsys.readouterr().out
        assert out.count("pants.Blue") == 1


class TestReplacingAGarment:
    def test_the_new_label_is_what_later_invocations_print(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert (
            run(["replace", "pants.Blue", "navy"], state_dir=tmp_path)
            == 0
        )
        assert "navy" in capsys.readouterr().out
        assert run(["show-closet"], state_dir=tmp_path) == 0
        assert "pants.navy" in capsys.readouterr().out

    def test_what_was_recorded_is_said_back(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert (
            run(
                ["replace", "home.shoes.Black", "oxblood"],
                state_dir=tmp_path,
            )
            == 0
        )
        assert "recorded" in capsys.readouterr().out

    def test_restating_the_label_a_garment_has_records_nothing(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # A no-op rather than a refusal, so it is not an error -- but
        # nothing was written, so nothing says it was.
        assert (
            run(["replace", "pants.Blue", "Blue"], state_dir=tmp_path)
            == 0
        )
        assert "recorded" not in capsys.readouterr().out
        assert not _state(tmp_path).exists()

    def test_a_refused_replace_records_nothing(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert (
            run(
                ["replace", "office.shoes.Brown", "Black"],
                state_dir=tmp_path,
            )
            == 2
        )
        assert "Black" in capsys.readouterr().err
        assert not _state(tmp_path).exists()


class TestSwappingTwoShirts:
    def test_the_labels_change_hands(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run(["show-closet"], state_dir=tmp_path) == 0
        columns = _get_columns(capsys.readouterr().out, "White")
        assert columns[2] == "Blue"
        assert (
            run(
                ["swap", "office", "White", "Striped"],
                state_dir=tmp_path,
            )
            == 0
        )
        capsys.readouterr()
        assert run(["show-closet"], state_dir=tmp_path) == 0
        assert _shirts(capsys.readouterr().out, "office")[:1] == [
            "Striped"
        ]

    def test_shirts_that_do_not_share_pants_are_refused(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert (
            run(
                ["swap", "office", "White", "Black"],
                state_dir=tmp_path,
            )
            == 2
        )
        assert "pants" in capsys.readouterr().err
        assert not _state(tmp_path).exists()

    def test_a_closet_that_is_not_one_is_refused(
        self, tmp_path: Path
    ) -> None:
        with pytest.raises(SystemExit):
            run(
                ["swap", "attic", "White", "Striped"],
                state_dir=tmp_path,
            )


class TestSettingTheOfficeWeekdays:
    def test_a_later_invocation_answers_from_the_new_pattern(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        tuesday = _next(TUE)
        assert _set_weekdays(["tue", "thu", "sat"], tmp_path) == 0
        capsys.readouterr()
        assert _ask(tuesday, tmp_path) == 0
        assert "office day" in capsys.readouterr().out

    def test_the_names_are_read_whatever_their_case(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert _set_weekdays(["Tue", "THU", "sat"], tmp_path) == 0
        capsys.readouterr()
        assert run(["office-weekdays"], state_dir=tmp_path) == 0
        assert "tue thu sat" in capsys.readouterr().out

    def test_it_says_every_rotation_was_re_anchored(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert _set_weekdays(["tue", "thu", "sat"], tmp_path) == 0
        out = capsys.readouterr().out
        assert "recorded" in out
        assert "re-anchored" in out

    @pytest.mark.parametrize(
        "weekdays",
        [
            ["mon"],
            ["mon", "wed"],
            ["mon", "tue", "wed", "thu"],
            ["mon", "mon", "wed"],
            ["mon", "mon", "wed", "fri"],
        ],
    )
    def test_anything_but_three_different_days_is_refused(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        weekdays: list[str],
    ) -> None:
        assert _set_weekdays(weekdays, tmp_path) == 2
        assert "source" in capsys.readouterr().err
        assert not _state(tmp_path).exists()

    def test_a_name_that_is_not_a_weekday_is_refused(
        self, tmp_path: Path
    ) -> None:
        with pytest.raises(SystemExit):
            _set_weekdays(["mon", "wed", "funday"], tmp_path)

    def test_a_weekday_is_spelled_out_or_shortened(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # The same vocabulary `--on` takes, so the two agree.
        assert _set_weekdays(["mon", "Wednesday", "FRI"], tmp_path) == 0
        assert "office weekdays mon wed fri" in capsys.readouterr().out

    def test_naming_none_at_all_is_refused(
        self, tmp_path: Path
    ) -> None:
        # Showing them is its own command, so there is no bare form
        # of this one to mean it.
        with pytest.raises(SystemExit):
            _set_weekdays([], tmp_path)


class TestSettingTheColdThreshold:
    def test_a_later_invocation_uses_it(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        mild = DEFAULT_COLD_THRESHOLD + 2
        assert (
            run(
                ["set-cold-threshold", f"{mild + 3}"],
                state_dir=tmp_path,
            )
            == 0
        )
        assert "recorded" in capsys.readouterr().out
        _run_in(mild, tmp_path)
        assert "if it's cold" not in _get_outerwear_line(
            capsys.readouterr().out
        )

    def test_naming_none_at_all_is_refused(
        self, tmp_path: Path
    ) -> None:
        with pytest.raises(SystemExit):
            run(["set-cold-threshold"], state_dir=tmp_path)

    def test_a_threshold_that_is_not_a_number_is_refused(
        self, tmp_path: Path
    ) -> None:
        with pytest.raises(SystemExit):
            run(["set-cold-threshold", "brisk"], state_dir=tmp_path)


class TestShowingWhatIsTold:
    def test_the_office_weekdays_are_printed_and_nothing_changes(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run(["office-weekdays"], state_dir=tmp_path) == 0
        assert (
            capsys.readouterr().out == "office weekdays mon wed fri\n"
        )
        assert not _state(tmp_path).exists()

    def test_the_cold_threshold_is_printed_and_nothing_changes(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run(["cold-threshold"], state_dir=tmp_path) == 0
        assert (
            capsys.readouterr().out
            == f"cold threshold {DEFAULT_COLD_THRESHOLD}°F\n"
        )
        assert not _state(tmp_path).exists()

    def test_neither_takes_a_value_to_set(self, tmp_path: Path) -> None:
        with pytest.raises(SystemExit):
            run(["cold-threshold", "55"], state_dir=tmp_path)


class TestAskingWhenAShirtIsNextDue:
    def test_it_prints_the_found_dates_whole_outfit(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert _when("office.shirt.White", tmp_path) == 0
        found = capsys.readouterr().out
        assert _ask(_dated(found), tmp_path) == 0
        assert capsys.readouterr().out == found

    def test_a_shirt_due_today_prints_today(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # A fresh installation anchors today at the top of its closet.
        closet = _todays_closet()
        assert _when(f"{closet}.shirt.White", tmp_path) == 0
        assert _dated(capsys.readouterr().out) == _today()

    def test_each_closets_white_is_a_different_shirt(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert _when("office.shirt.White", tmp_path) == 0
        at_the_office = _dated(capsys.readouterr().out)
        assert _when("home.shirt.White", tmp_path) == 0
        assert _dated(capsys.readouterr().out) != at_the_office

    @pytest.mark.parametrize(
        "garment",
        ["office.sweater.Beige", "home.shoes.Black", "pants.Blue"],
    )
    def test_anything_but_a_shirt_is_refused(
        self,
        garment: str,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        # Sweaters, shoes and jackets follow from pants during
        # Resolution rather than being picked by a Rotation.
        assert _when(garment, tmp_path) == 2
        assert "shirts" in capsys.readouterr().err

    def test_a_label_the_closet_does_not_have_is_refused(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert _when("office.shirt.ecru", tmp_path) == 2
        assert "ecru" in capsys.readouterr().err

    def test_a_shirt_the_year_ahead_never_wears_is_said_plainly(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Only a deliberate stretch of Overrides can exhaust the year.
        assert {
            _run(
                "stay-home", _today() + timedelta(days=offset), tmp_path
            )
            for offset in range(HORIZON_DAYS)
        } == {0}
        capsys.readouterr()
        assert _when("office.shirt.White", tmp_path) == 0
        assert (
            capsys.readouterr().out
            == "no office day in the next year wears White\n"
        )

    def test_it_takes_no_date(self, tmp_path: Path) -> None:
        with pytest.raises(SystemExit):
            run(
                [
                    "when",
                    "office.shirt.White",
                    "--on",
                    _today().isoformat(),
                ],
                state_dir=tmp_path,
            )

    def test_a_date_ahead_of_the_command_is_ignored(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # ADR-0008's ordering caveat, on a command that produces a date
        # rather than acting on one: the root parser's --on parses and
        # the search still runs from today.
        assert _when("office.shirt.White", tmp_path) == 0
        found = _dated(capsys.readouterr().out)
        assert (
            run(
                ["--on", "2027-01-05", "when", "office.shirt.White"],
                state_dir=tmp_path,
            )
            == 0
        )
        assert _dated(capsys.readouterr().out) == found

    def test_asking_records_nothing(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        absent = tmp_path / "absent"
        assert _when("office.shirt.White", absent) == 0
        assert "shirt" in capsys.readouterr().out
        assert not absent.exists()

    def test_the_found_dates_outerwear_hedges_until_forecast(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert _when("office.shirt.White", tmp_path) == 0
        out = capsys.readouterr().out
        assert _get_outerwear_line(out).endswith("if it's cold")
        assert (
            cli.run(
                ["when", "office.shirt.White"],
                state_dir=tmp_path,
                fetch_weather=lambda: {
                    _dated(out): DEFAULT_COLD_THRESHOLD - 10
                },
            )
            == 0
        )
        assert not _get_outerwear_line(
            capsys.readouterr().out
        ).endswith("if it's cold")


def _when(shirt: str, state_dir: Path) -> int:
    return run(["when", shirt], state_dir=state_dir)


def _set_weekdays(weekdays: list[str], state_dir: Path) -> int:
    return run(["set-office-weekdays", *weekdays], state_dir=state_dir)


def _run(command: str, on: date | None, state_dir: Path) -> int:
    return run(
        [command, *([] if on is None else ["--on", on.isoformat()])],
        state_dir=state_dir,
    )


def _reset(shirt: str, on: date, state_dir: Path) -> int:
    return run(
        ["reset", shirt, "--on", on.isoformat()], state_dir=state_dir
    )


def _ask(on: date, state_dir: Path) -> int:
    return run(["--on", on.isoformat()], state_dir=state_dir)


def _run_in(high: float, state_dir: Path) -> None:
    assert (
        cli.run(
            [],
            state_dir=state_dir,
            fetch_weather=lambda: {_today(): high},
        )
        == 0
    )


def _get_outerwear_line(out: str) -> str:
    return next(
        line for line in out.splitlines() if line.startswith(OUTERWEAR)
    )


def _state(state_dir: Path) -> Path:
    return state_dir / "state.json"


def _listed(out: str, closet: str) -> list[list[str]]:
    block = out.split(f"{closet}\n", maxsplit=1)[1]
    listed = block.split("\n\n", maxsplit=1)[0]
    return [
        re.split(r" {2,}", line.removeprefix("> ").strip())
        for line in listed.splitlines()
    ]


def _marked(out: str, closet: str) -> list[str]:
    block = out.split(f"{closet}\n", maxsplit=1)[1]
    listed = block.split("\n\n", maxsplit=1)[0]
    return [
        re.split(r" {2,}", line.removeprefix("> ").strip())[1]
        for line in listed.splitlines()
        if line.startswith("> ")
    ]


def _shirts(out: str, closet: str) -> list[str]:
    return [
        columns[1]
        for columns in _listed(out, closet)
        if columns[0] == "shirt"
    ]


def _get_columns(out: str, label: str) -> list[str]:
    return next(
        columns
        for closet in ("office", "home")
        for columns in _listed(out, closet)
        if columns[1] == label
    )


def _shirt(out: str) -> str:
    return next(
        line.split(maxsplit=1)[1]
        for line in out.splitlines()
        if line.startswith("  shirt")
    )


def _contrary() -> str:
    return "stay-home" if _todays_closet() == "office" else "go-in"


def _todays_closet() -> str:
    return (
        "office"
        if _today().weekday() in DEFAULT_OFFICE_WEEKDAYS
        else "home"
    )


def _next(weekday: int) -> date:
    today = _today()
    return today + timedelta(days=(weekday - today.weekday()) % 7)


def _today() -> date:
    return datetime.now(UTC).astimezone().date()


def _dated(out: str) -> date:
    """Return the date the first line of an answer prints."""
    return (
        datetime.strptime(
            out.splitlines()[0].split(" - ")[0], "%a %d %b %Y"
        )
        .replace(tzinfo=UTC)
        .date()
    )
