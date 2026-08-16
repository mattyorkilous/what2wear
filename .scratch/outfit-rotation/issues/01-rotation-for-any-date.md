# 01 — Rotation for any date

**What to build:** Running the tool with no arguments prints the Shirt and its pants for today, along with whether today is an Office Day or a Home Day. Running it with a date prints the same for that date — past or future, arbitrarily far out. Both Closets are read from a hand-authored YAML file the tool never writes back to.

This is the walking skeleton for the whole feature. It stands up the single pure seam every later ticket routes through, the config parsing at the boundary, and the CLI shell. Most importantly it proves ADR-0001 in practice: because Position is derived from the calendar rather than stored, looking at a future date is the same call as looking at today, not a separate simulation.

Scope is deliberately narrow — Shirt and pants only. No sweaters, no shoes, no overrides, no resets, no weather.

**Blocked by:** None — can start immediately.

**Status:** done

- [x] Bare invocation prints today's Shirt, its pants, and the day's type
- [x] A date argument prints the same for any date, including dates years out
- [x] Office Days follow a configurable weekday pattern; every other date is a Home Day, weekends included
- [x] Each Closet has its own Anchor Date, authored as a date plus the Shirt worn that day
- [x] The Office Rotation advances only on Office Days and the Home Rotation only on Home Days; each wraps at the end of its Closet
- [x] Closets, the weekday pattern and the Anchor Dates are loaded from YAML and validated at the boundary; malformed config fails with a clear message
- [x] The YAML is never rewritten by the tool
- [x] All domain logic sits behind one pure entry point taking the parsed state and the date as arguments — the shell reads files, reads the clock and prints, and does nothing else
- [x] Tests drive that entry point with in-memory state and an explicit date; no files, no network, no clock, no mocks
- [x] The agreed Aug 15–24 2026 sequence is asserted for Shirt and pants, covering the home wrap from lgreen back to white
