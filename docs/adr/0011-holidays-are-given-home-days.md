# Holidays are given Home Days, between the Office Weekdays and the Overrides

A date's kind is decided in three layers, each overriding the one
below: the Office Weekdays, then the Holidays, which are Home Days
whatever the weekday, then the Day Type Overrides. The Holidays are the
`holidays` library's `US` calendar with its default observed dates,
plus the day after each Thanksgiving, found by name in the same
calendar.

The set is given, per ADR-0005: it is a fact about the one wearer the
tool dresses, the same for every year they keep their job, and a change
to it is a commit. There is no command to add or remove a Holiday and
nothing about them is written to the State. An employer that skips a
federal holiday, or a wearer who works one, is a `go-in` Override —
one mechanism for every exception.

This amends ADR-0001's consequence that Overrides are "the only thing
left that the derivation reads out of the State." That is still true
of the State, but the derivation now also reads a given calendar. The
alternative was the status quo: the wearer remembers to `stay-home`
each Holiday every year, and every one forgotten leaves both Shirt
Rotations off by one until a Reset.

## Consequences

- **Holidays enter the derivation in one place.** The default kind of
  a date — weekday then Holiday — is what the day-type function falls
  through to, what `record_override` prunes against, and what the
  Position count corrects toward. `answer`, `when` and the office
  sweater walk all agree because they all ask it.
- **The Position count keeps its whole-week shortcut.** It counts by
  the weekday pattern, then corrects over the Overrides and Holidays in
  range, each date once. A Holiday already a Home Day by weekday
  corrects nothing, so the library's duplicate entry for a weekend
  Holiday is harmless. Asking every date its kind would be simpler but
  make each Position a walk from the Anchor, and `when` asks for up to
  a year of them.
- **`stay-home` on a Holiday records nothing; `go-in` on one is kept.**
  Existing `stay-home` records on past Holidays become redundant, change
  no answer, and are pruned the next time anything is recorded.
- **Observed dates are the federal rule, not the wearer's.** A Saturday
  Holiday observes on Friday even under Office Weekdays that make
  Friday a Home Day already — harmless, since it is one anyway.
- **Today's Positions move once, and nothing re-anchors them.**
  Introducing Holidays reclassifies every past Holiday between the
  Anchors and today. ADR-0007 re-anchors inside the command that changes
  the calendar, but this change arrives as code, so there is no command
  to do it in. Accepted: there is one wearer, it happens once, and a
  Reset per Closet puts it right. The README's upgrade note says so. No
  migration was written, and the State file's schema is unchanged.
- **`holidays` is a runtime dependency.** It carries the rule code for
  moving and observed holidays that would otherwise live here.
