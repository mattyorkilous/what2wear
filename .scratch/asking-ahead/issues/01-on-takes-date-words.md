# 01 — `--on` takes date words

**What to build:** The wearer can name a date with a word instead of
digits. `--on tomorrow` and `--on yesterday` work, and so does any
weekday name — `wed`, `Wed`, `wednesday`, `WEDNESDAY` all land on the
soonest date with that weekday, today included, so on a Wednesday
`--on wed` means today. ISO dates keep working exactly as they do now.

Because `--on` is declared once on the shared parent parser, every
command that takes it gains the words at the same time: `go-in --on
sat`, `stay-home --on tomorrow`, and ADR-0008's own motivating case,
`reset lblue --on fri`, which sets a Rotation right for the next time
you go in from a day you are not going in.

There is deliberately no `today`: a bare invocation already means
today, so the word would be a second spelling of the default. `--on
today` is an error, and that asymmetry is a decision rather than a gap.

Weekday matching reuses the vocabulary `set-office-weekdays` already
has, matched on the first three letters and lowercased, rather than
introducing a second table. `calendar.day_name` is deliberately not
consulted — it is locale-dependent.

Shell only. Nothing in core, nothing in the State file, no domain term:
a word for a date is a spelling, not a concept.

**Blocked by:** None — can start immediately.

**Status:** done

- [x] `--on tomorrow` and `--on yesterday` resolve, and `yesterday`
      still carries the past-date note
- [x] `wed`, `Wed`, `wednesday` and `WEDNESDAY` all resolve to the same
      date
- [x] A weekday word resolves to the soonest date with that weekday, at
      most six days out, from whichever day it is asked
- [x] Asking for today's own weekday returns today, not seven days on
- [x] `--on today` is refused, with a test pinning the asymmetry so it
      is not "fixed" later
- [x] A word that is neither a date nor a weekday is refused at exit 2
      with a message naming what `--on` accepts
- [x] ISO dates keep working, including the existing malformed-date
      refusal
- [x] The words work on a recording command: `go-in --on sat` records
      that Saturday, and the confirmation line names that date
- [x] `reset <label> --on fri` moves the Anchor to the coming Friday
- [x] `--on`'s metavar is `DATE` and its help text names the accepted
      words
- [x] ADR-0008's ordering caveat still holds: `what2wear --on tomorrow
      go-in` still records today
- [x] Tests go through `cli.run`, the existing shell seam; `_parse_date`
      is not tested directly
- [x] The README's Interface section shows the words

## Comments

Weekday matching came out stricter than this ticket specified. "Matched
on the first three letters" was implemented literally at first, which
made `--on wedding` mean Wednesday and `--on monkey` mean Monday —
silently, so a mistyped `reset` would move an Anchor to the wrong day
without refusing. Both reviews flagged it. It now matches the full name
or its first three letters and nothing else.

That needed the seven names spelled out, which this ticket had hoped to
avoid ("rather than introducing a second table"). They are local to
`_get_weekday` in the shell, and every abbreviation elsewhere is one of
their first three letters, so the two cannot drift unnoticed: mistyping
one fails ten tests through `cli.run`.

`set-office-weekdays` shares that lookup, so it takes the spelled-out
names too — a change to a command this ticket did not name, made so the
two cannot disagree about what a weekday is called.
