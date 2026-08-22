# 01 — The Wardrobe becomes given source

**What to build:** The tool answers on a fresh install with nothing to set
up. There is no file to write, no example to copy and no first-run
message, because the Wardrobe is no longer something the wearer states —
its whole shape lives in source. Running with no arguments prints today's
Shirt, its Pants and whether today is an Office Day or a Home Day;
`--on` with a future date prints the same for that date, arbitrarily far
out. A date in the past is refused with a reason rather than answered,
because a Reset rewrites what a past Position was and the tool keeps no
record of what was actually worn.

This is the slice that deletes the config boundary. Everything that
boundary validated becomes a property of source instead: duplicate Shirt
Labels, Pants with no row, a Fallback that is no other row's sweater,
office sweaters not one-to-one with office shoes, and an Anchor sitting
on a day of the wrong kind are all now impossible to author by accident
and are asserted once rather than checked on every run. Anchors stop
naming a Shirt and start stating a Position, so that later tickets can
change a Label without moving a Rotation.

Day Type Overrides and Resets are untouched here and keep working off
the existing decision log. They move in 03.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] `what2wear` on a machine with no files anywhere prints today's Shirt, its Pants and the day's type
- [ ] `--on` with a future date answers identically, including dates years out
- [ ] `--on` with a date before today is an error that names why the past is not answerable
- [ ] The office Week walk still resolves earlier Office Days of the current Week internally — counting backwards from an Anchor survives, and is covered by a test that would fail if it were removed as dead
- [ ] Nothing reads a Wardrobe from disk, and nothing creates a directory to look for one
- [ ] The config module, its schema, its validation and all its error types are gone, along with the missing-Wardrobe error and the first-run flow
- [ ] The example Wardrobe file is gone, as is the test pinning the in-memory fixture to it
- [ ] `pydantic` is no longer a dependency; `pyyaml` stays
- [ ] Every property the config boundary used to enforce is asserted once against the given Wardrobe: no duplicate Shirt Label within a Closet, every Shirt's Pants has a row, every Fallback is another row's sweater, office sweaters pair one-to-one with office shoes, and each Anchor sits on a day of its own kind
- [ ] Each Anchor is a date and a Position; no Anchor names a Label
- [ ] Pants are shared across both Closets, with a Pants Row per Closet, per ADR-0003 as amended
- [ ] The wearer's real Labels and Anchors are moved by hand into source and the old platform config file is deleted
- [ ] Day Type Overrides and Resets behave exactly as before
- [ ] The README no longer describes a config file, an example file or a first run
