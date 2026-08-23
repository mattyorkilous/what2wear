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

**Status:** done

- [x] Recording a Day Type Override or a Reset persists it and a later invocation reflects it
- [x] The State file is written to a temporary file in the same directory and moved into place atomically; a write that fails partway leaves the previous State intact
- [x] A missing State file reads as the given Anchors with no Overrides, with no error and no first-run message
- [x] The directory is created on first write only
- [x] The file is legible to a person who opens it, though nobody is expected to
- [x] Reading and writing the State file are the only impure functions added, alongside reading the clock and printing
- [x] `answer` renders nothing and changes nothing; `apply` returns a State and renders nothing
- [x] A Reset moves its Rotation's Anchor to today and the Position named; every later date follows and the Rotation stays continuous
- [x] The Position derivation has no offset term (the Anchor cutoff was already deleted in 01)
- [x] Nothing in the State references a Garment by Label — Anchors store Positions and Overrides are keyed by date
- [x] Day Type Overrides are keyed by date, so recording the opposite for a date replaces rather than stacks, and the "a later record wins" scan is gone
- [x] The decisions module, its log, the `Decision` union, the `Reset` record, the Rotation enum and the Reset-offset accumulator are all deleted
- [x] Staying home on an Office Day leaves the office Position parked so the skipped Shirt appears on the next Office Day; going in advances it
- [x] A Reset naming a Label absent from the day's Closet is an error rather than a guess
- [x] A mid-Week Reset changing what the Week's walk believes an earlier day spent, and therefore that Week's Fallback, is asserted directly — ADR-0001 accepts this knowingly and the test is what stops it being "fixed"
- [x] A State written and read back is the same State
- [x] The first write pins the default Anchor, so a Rotation stops moving with today — carried over from 01, where the Anchor became today at Position 0 with nowhere to record it
- [x] Look-ahead to a date matches what that date returns when it arrives, absent intervening commands — false while the Anchor moves, and restored by pinning it

## Comments

**The past is refused in the shell, not the core.** `answer(state, on)`
takes no `today` -- with the Anchor in the State there is nothing left
for it to read a clock for -- so it cannot tell a past date from a
future one. The refusal, and `PastDateError` with it, moved to
`cli.py`. This is also what keeps `stay-home <a past date>` printing
the outfit it records against, which it did before: only the bare
question is refused.

**Dates are written as strings rather than as YAML dates.** Both
Anchors normally sit on the same date, and PyYAML abbreviates a
repeated value to an alias (`date: &id001 2026-08-22` / `date:
*id001`). Legible is an acceptance criterion, so `_document` writes
`anchor.on.isoformat()` and `_state` reads it back with
`date.fromisoformat`.

**`answer` takes no `weather` yet.** The ticket writes
`answer(state, on, weather)`; weather arrives in 05, so the seam ships
as `answer(state, on)`. It also takes no `today`, per the note above.

**Look-ahead is only pinned once something has been recorded.** The
last criterion is ticked as written -- "restored by pinning it" -- but
the residual is worth stating: an installation that has never recorded
anything has no State file, so `read_state` still hands back the given
Anchors at *today*, and a `--on <future date>` answer from it will
differ by the time that date arrives. Nothing writes on the read path,
because story 51 asks for no State file until the wearer first changes
something. From the first `stay-home`, `go-in` or `reset` onward the
Anchors stand still. `tests/test_store.py` asserts both halves.

**`StateError` is kept, and is not the deleted validation.** 01
deleted a schema that checked a *human-authored* Wardrobe against
domain rules. This is the tool's own file failing to deserialize at
all, which `decisions.py` handled the same way with `DecisionsError`
and which the shell already had an exit path for. A corrupt State file
reports rather than tracebacks; nothing about its contents is checked
beyond being readable.

**A machine crash is covered as well as a process crash.** The move is
atomic either way, but a rename can land ahead of the bytes, so
`_write_document` flushes and `os.fsync`s the temporary file before
`replace`. The test drives a write that dies halfway and asserts the
previous State reads back whole.
