# The recording seam is four functions, not a Command union

The recording seam is four public functions on `core` — `record_override`,
`reset`, `replace_` and `swap` — each taking a State and the plain values
the wearer typed, and each returning a State. There is no `Command`
union, no `apply`, and the CLI matches on the subcommand once.

The problem this solves is that the same five-way shape was matched
three times over. `_get_command` turned parsed arguments into a Command
dataclass; `apply` matched that dataclass back to the function that did
the work; `_get_confirmation` matched it a third time to say what had
been recorded. Between the first match and the last, the Command object
travelled nine lines and was then discarded. Nothing stored it, wrote
it, queued it or replayed it.

Commands-as-values earn their keep when a command travels — a log to
append to, a queue to drain, an undo stack to unwind, a wire to cross.
[ADR-0006](./0006-the-wardrobe-is-source-the-state-is-one-file-the-tool-owns.md)
deleted `decisions.jsonl` and the `Decision` union it held, on the
grounds that a Reset is no longer a record but a moved Anchor. The
`Command` union outlived the only thing that gave it somewhere to
travel to.

## Consequences

- **Two matches, in the shell, on the string argparse already
  validated.** `_choose_update_function(args) -> UpdateFunction`
  picks the core function; `_get_message(args) -> str` returns the
  line describing what was typed, for the shell to confirm back. Neither does the other's job, and the
  message never needed a State to begin with — it describes what
  was typed, not what the state became, which is what lets `already` print for a
  command that changed nothing. Three matches become two, the
  `Command` union and its four subclasses go, and roughly seventy
  lines and ten imports with them.
- **A single `Command` class would not have worked.** The five
  commands carry different fields, so one class is either a
  god-object holding every field with most null on any given call, or
  a callable paired with a string — a tuple with a dataclass over it.
  The union was the honest shape for commands-as-values; the question
  was whether values were wanted at all, and they were not.
- **Exhaustiveness moves from the type checker to a `raise
  AssertionError`.** A closed union made `apply` provably total, so a
  fifth command that `apply` forgot was a type error. Matching on
  `args.action` gets no such check: a new subcommand would fall to the
  wildcard. Traded knowingly, because argparse's `choices` guards the
  input side and both wildcards now raise rather than silently doing
  nothing — `_get_message` included, so a forgotten arm there is as loud
  as a forgotten arm in `_choose_update_function` rather than a quietly
  missing line. **The parser, `_choose_update_function` and
  `_get_message` must be edited together**, and
  a new subcommand's CLI test is what catches it if they are not. The
  two matches carry identical arms, so they read as a pair.
- **Both seams still hold.** `answer` renders and changes nothing; each
  of the four records and renders nothing. The seam is four doors
  rather than one, which is what the shell wanted anyway — it never
  called `apply` without knowing which command it held.
- **The shell still writes only on a difference.** The chosen function
  hands back the State it was given when nothing was typed, so
  `state_updated != state` remains the single test that decides whether
  the file is written. `apply`'s "takes no command as well as one"
  property is now `_choose_update_function`'s `case None`, an identity
  function.
- **The CLI chooses a core function; core is the function.**
  `_choose_update_function` never updates a State itself — it returns
  one of the four core functions with the typed values already bound,
  and the shell calls it: `_choose_update_function(args)(state)`.
  The earlier `_update_state(state, args, on)` did the same work under
  a name that put the update in the shell, which is exactly backwards
  from where it happens. Swapping the CLI for another interface trades
  the parser, this chooser and the renderers; core does not move.
  `choose_` says a function comes back rather than a value, and
  `UpdateFunction` says it again in the annotation.
- **Tests name the thing they exercise.** `reset(GIVEN, "beige",
  WED26)` replaced `apply(GIVEN, ResetRequest("beige"), WED26)`, and
  `test_no_command.py` retired: the behaviour it guarded is the shell's
  now, already covered by
  `test_a_fresh_installation_answers_and_leaves_nothing_behind`.
- **The Replace function is `replace_`, with the trailing underscore
  PEP 8 keeps for a name already taken.** The core module imports
  `dataclasses.replace`, which every one of these functions uses to
  build the State it returns. The domain word wins the name and the
  collision is absorbed by the underscore, so the CLI subcommand,
  CONTEXT.md and the function all say Replace.
- **`show-closet` still short-circuits ahead of the update.** It prints
  the wardrobe and returns without an outfit at all, so it is neither
  a command that records nor one that answers, and neither match has
  anything to say about it.
