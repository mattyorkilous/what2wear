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

**Status:** ready-for-agent

- [ ] `--on tomorrow` and `--on yesterday` resolve, and `yesterday`
      still carries the past-date note
- [ ] `wed`, `Wed`, `wednesday` and `WEDNESDAY` all resolve to the same
      date
- [ ] A weekday word resolves to the soonest date with that weekday, at
      most six days out, from whichever day it is asked
- [ ] Asking for today's own weekday returns today, not seven days on
- [ ] `--on today` is refused, with a test pinning the asymmetry so it
      is not "fixed" later
- [ ] A word that is neither a date nor a weekday is refused at exit 2
      with a message naming what `--on` accepts
- [ ] ISO dates keep working, including the existing malformed-date
      refusal
- [ ] The words work on a recording command: `go-in --on sat` records
      that Saturday, and the confirmation line names that date
- [ ] `reset <label> --on fri` moves the Anchor to the coming Friday
- [ ] `--on`'s metavar is `DATE` and its help text names the accepted
      words
- [ ] ADR-0008's ordering caveat still holds: `what2wear --on tomorrow
      go-in` still records today
- [ ] Tests go through `cli.run`, the existing shell seam; `_parse_date`
      is not tested directly
- [ ] The README's Interface section shows the words
