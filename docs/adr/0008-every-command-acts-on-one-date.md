# Every command acts on one date, and the past is answerable

`--on` becomes the single way any invocation names the date it is
about, on every command, defaulting to today. The positional dates on
`stay-home` and `go-in` go, `reset` gains a date it never had, and
dates before today stop being refused.

This amends ADR-0001, which held that "dates before today are
refused". That refusal was never protecting a computation — the
derivation is total and signed, and answers a past date as readily as
a future one. It was protecting a reading: the answer describes where
the Rotation stands now, and a bare date at the top of the output
invites it to be read as what was actually worn. A note says the
difference instead, which is the smaller instrument for the problem
that was actually there.

## Consequences

- **A past answer is offered with a caveat rather than withheld.** The
  output carries a note saying it is where the Rotation stands now,
  not what was worn. Refusal and note answer the same worry; the note
  costs the wearer nothing when they want the date anyway.
- **A Reset names the date it moves the Anchor to.** ADR-0001's
  formula has no offset term, so an Anchor at any date is as valid as
  an Anchor at today. `reset white --on <next office day>` is the case
  this exists for: setting a Rotation right for the next time you go
  in, from a day you are not going in.
- **A Reset dated ahead of today moves today as well.** The whole
  Rotation comes with the Anchor, and today is counted backwards from
  it, so today's Shirt shifts by one. Accepted for the same reason
  ADR-0001 accepts a mid-Week Reset changing that Week's Fallback: it
  is the honest consequence of a Rotation with no offset term, and the
  alternative is a date-scoped Reset, which is the stored history this
  design exists without.
- **Which Closet a Reset searches comes from its date, not from
  today.** `ResetRequest` always said the Closet comes from the date
  and never from the Label; while a Reset was pinned to today the two
  could not be told apart. They can now, and the date wins.
- **The shell loses three things.** `PastDateError`, the check that
  refused it, and the check that refused `--on` beside a command all
  go, because one date idiom leaves nothing to arbitrate. The rule
  count goes down rather than moving.
- **`--on` is declared once, on a shared parent parser, and defaults
  to today.** The top-level parser and every dated subcommand take it,
  so both `what2wear --on <date>` and `go-in --on <date>` work.
  `replace`, `swap` and `show-closet` do not: a Label is not dated, so
  a date they would ignore is better refused than accepted. The two
  positions are not interchangeable: a subcommand's own default
  overwrites an `--on` given ahead of it, so `what2wear --on <date>
  go-in` records today. Accepted, because the flag belongs after the
  command it modifies, and the confirmation line names the date it
  recorded either way. An earlier version suppressed the subcommands'
  copy so that both orders meant the same thing. It cost a second
  parser, a parameter carrying either a date or a sentinel, and a
  paragraph explaining the asymmetry, to support a form nobody types.
