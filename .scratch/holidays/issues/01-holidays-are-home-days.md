# 01 — Holidays are Home Days

**What to build:** US federal holidays, on their observed dates, and the
Friday after Thanksgiving are Home Days without the wearer saying so. A
Day Type Override still outranks them, so `go-in` on a Holiday makes it
an Office Day. Every reader agrees: `answer`, `get_due_shirt`,
`get_due_date`, the office sweater walk, and the Position count behind
all three Rotations. See `.scratch/holidays/spec.md`.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] `holidays` is a runtime dependency; the set is `US` with no
      subdivision and default observed dates, plus the day after each
      Thanksgiving found by name
- [ ] A date's kind is layered: Office Weekdays, then Holidays (Home),
      then Day Type Overrides
- [ ] The Position count keeps its whole-week shortcut and corrects over
      the Overrides and Holidays in range, each date counted once
- [ ] `record_override` prunes against weekday-plus-Holiday: `go-in` on
      a Holiday is kept, `stay-home` on one leaves nothing recorded
- [ ] Labor Day, Thanksgiving and the Friday after answer as Home Days;
      a Saturday July 4 makes Friday a Home Day, a Sunday holiday makes
      Monday one
- [ ] A Holiday does not advance the Office Shirt Rotation, does advance
      the Home Shirt Rotation, and takes a Home Outerwear turn
- [ ] The office sweater walk in a Holiday Week ignores the Holiday
- [ ] `get_due_date` never answers an office Shirt with a Holiday
- [ ] A Position years past many Holidays matches stepping through
      each date one at a time
- [ ] `tests/test_worked_calendar.py` and `tests/test_resolution.py`
      expectations on and after 2026-09-07 updated to the new truth,
      not overridden back
- [ ] `CONTEXT.md`: new **Holiday** term; Home Day, Office Day and Day
      Type Override updated; `holiday` off the Override _Avoid_ list
- [ ] ADR-0011 written, amending ADR-0001's "Overrides are the only
      thing the derivation reads"
- [ ] README: Holidays are Home Days by default, `go-in` overrides one,
      and an upgrade note to check today's Shirts and `reset` once
- [ ] State file schema unchanged
