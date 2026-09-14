# The Wardrobe is source, the State is one file the tool owns

> Amended by [ADR-0009](./0009-the-recording-seam-is-four-functions-not-a-command-union.md).
> The two seams stand; the recording one is four functions rather than
> one `apply` over a `Command` union.

Everything given lives in source; everything the tool is told lives in
one YAML file the tool reads and writes and no human authors. The State
holds the Labels, the three Anchors and the Day Type Overrides, and
nothing structural can appear in it. Between them there is no third
place, and in particular there is no file a person edits.

The problem this solves is that there used to be two authors for one
fact. Where a Rotation stood was stated by a hand-authored Anchor Date
*and* by tool-recorded Resets, so the code carried a tie-break rule —
a Reset dated before its Closet's Anchor stopped counting — and ADR-0001
spent a consequence defending it. Splitting given from told means every
fact has exactly one author, and that rule becomes unnecessary rather
than merely documented.

## Consequences

- **Nothing may be keyed by a Label.** Labels move, so an Anchor stores
  a Position and a Pants Row points at a Garment, never at what it is
  currently called. A Label appears at the edges only: typed at a
  command, printed in an answer.
- **Two seams, not one.** The spec's single `handle` existed because
  every command was a question that might also record something. Now
  `answer(state, on) -> Response` never changes anything and the
  recording seam never renders anything; the shell composes them, so a
  command that records shows you its result for free. The shell writes
  only when the State it gets back differs from the State it had, so
  it makes the same call whether or not anything was typed. This
  retires `handle`'s "resolve as though the decision were already in
  force" special case, and makes every edit a State-in State-out
  function that is trivially table-tested. **ADR-0009 replaced the
  single `apply(state, command, today)` with the four functions it
  dispatched to.**
- **`read_state` and `write_state` are the only impure functions in the
  tool**, beside reading the clock, fetching the forecast and printing.
- **A whole-file rewrite can truncate; an append could not.** The
  append-only log's real guarantee was that recording something could
  never damage what was already recorded, and that is what a single
  mutable file gives up. Bought back by writing a temporary file in the
  same directory and `os.replace`-ing it onto the target. This is not
  optional: without it, "the one controlled side effect" is a hope.
- **`decisions.jsonl` and the `Decision` union are gone.** A Reset is no
  longer a record — it moves an Anchor — so the only thing left to
  record is Day Type Overrides, and they are a date-keyed map rather
  than a log. "A later record wins for the same date" becomes an
  overwrite, and the two kinds of thing stop needing a shared name.
- **The tool now creates its own directory and there is no first run.**
  A missing State file is a State with default Labels and the given
  Anchors, so a fresh install simply answers; the directory is created
  the first time something is written. The first-run message naming a
  path, `MissingWardrobeError`, and `.scratch/config-location/01`'s
  "nothing in the tool creates a directory" are all retired.
