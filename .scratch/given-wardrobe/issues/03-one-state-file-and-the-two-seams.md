# 03 — One State file and the two seams

**What to build:** Everything the tool has been told moves into one file
the tool owns and no human authors. `stay-home`, `go-in` and `reset`
round-trip through it, and it survives a crash mid-write: a partial write
must never be observable, which is the guarantee the append-only log gave
for free and a whole-file rewrite gives only if it is written to a
temporary file beside the target and moved into place atomically.

A missing file is not an error and not a first run — it reads as the
given Anchors with no Overrides. The directory is created the first time
something is written, and never merely to look.

With one author for every fact, a Reset stops being a recorded offset and
becomes a move of its Rotation's Anchor to today and the Position asked
for. That deletes the offset term from the Position derivation and takes
the tie-break rule with it — the rule that a Reset dated before its
Closet's Anchor stops counting, which nobody could guess from the outside
and which existed only because two authorities disagreed.

The single entry point splits in two:

```
answer(state, on, weather) -> Response     # never changes anything
apply(state, command, today) -> State      # never renders anything
```

The shell composes them, so a command that records still shows its result.
This retires the "resolve as though the decision were already in force"
special case: every edit becomes a State-in, State-out function, which
makes "what did this command actually change" a single value comparison
in a test.

**Blocked by:** 02 — The CLI becomes subcommands

**Status:** ready-for-agent

- [ ] Recording a Day Type Override or a Reset persists it and a later invocation reflects it
- [ ] The State file is written to a temporary file in the same directory and moved into place atomically; a write that fails partway leaves the previous State intact
- [ ] A missing State file reads as the given Anchors with no Overrides, with no error and no first-run message
- [ ] The directory is created on first write only
- [ ] The file is legible to a person who opens it, though nobody is expected to
- [ ] Reading and writing the State file are the only impure functions added, alongside reading the clock and printing
- [ ] `answer` renders nothing and changes nothing; `apply` returns a State and renders nothing
- [ ] A Reset moves its Rotation's Anchor to today and the Position named; every later date follows and the Rotation stays continuous
- [ ] The Position derivation has no offset term and no Anchor cutoff
- [ ] Nothing in the State references a Garment by Label — Anchors store Positions and Overrides are keyed by date
- [ ] Day Type Overrides are keyed by date, so recording the opposite for a date replaces rather than stacks, and the "a later record wins" scan is gone
- [ ] The decisions module, its log, the `Decision` union, the `Reset` record, the Rotation enum and the Reset-offset accumulator are all deleted
- [ ] Staying home on an Office Day leaves the office Position parked so the skipped Shirt appears on the next Office Day; going in advances it
- [ ] A Reset naming a Label absent from the day's Closet is an error rather than a guess
- [ ] A mid-Week Reset changing what the Week's walk believes an earlier day spent, and therefore that Week's Fallback, is asserted directly — ADR-0001 accepts this knowingly and the test is what stops it being "fixed"
- [ ] A State written and read back is the same State
