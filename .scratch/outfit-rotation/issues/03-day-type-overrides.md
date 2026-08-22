# 03 — Day Type Overrides

**What to build:** The ability to record that a specific date is an Office Day or a Home Day regardless of the weekly pattern. Staying home on an office day, going in on a Saturday, a public holiday and a day of leave are all the same command and the same recorded fact — there is no separate holiday or absence concept.

The key behavior is that a Day Type Override redirects which Closet the date draws from without disturbing the other Rotation. Staying home on an Office Day leaves the office Position parked, so the Shirt that would have been worn simply reappears on the next Office Day rather than being lost.

Overrides apply to any date, past or future. A future-dated override changes what look-ahead reports for that date and every date after it.

This ticket introduces the append-only decision log, kept separate from the hand-authored Closet config so that recording an override can never corrupt it.

**Blocked by:** 01 — Rotation for any date

**Status:** done

- [x] A command records that a date is a Home Day; another records that it is an Office Day
- [x] Both default to today and accept an explicit date
- [x] Future dates are accepted and are reflected in look-ahead for that date and all later ones
- [x] Past dates are accepted and change what earlier dates resolve to
- [x] Overriding an Office Day to a Home Day leaves the office Position untouched, so the skipped Shirt appears on the next Office Day
- [x] Overriding a Home Day to an Office Day advances the office Rotation on that date
- [x] Recorded decisions are appended to a log the tool owns; the hand-authored Closet config is never touched
- [x] Holidays and leave are recorded through the same command as any other override, with no distinct handling
- [x] Tests pass recorded decisions in as part of the in-memory state rather than reading them from disk
