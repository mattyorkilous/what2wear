# Given Wardrobe

Status: ready-for-agent

Supersedes `.scratch/outfit-rotation/spec.md`, which is left intact as
the record of the design this replaces. Governed by ADR-0005, ADR-0006,
ADR-0007 and the amended ADR-0001 and ADR-0003.

## Problem Statement

The tool has two authors for the same facts and it shows. The Wardrobe
is a YAML file the wearer hand-writes; the recorded decisions are a
JSONL log the tool appends to; and where a Rotation stands is stated by
both — by the hand-authored Anchor and by tool-recorded Resets. Because
neither can be ignored, the code carries a tie-break rule nobody can
guess from the outside: a Reset dated before its Closet's Anchor stops
counting.

That confusion is the visible symptom. Underneath it is a boundary that
should never have existed. The tool is built as something a stranger
could configure for their own clothes, but the rules only mean anything
against this Wardrobe's shape — office sweaters one-to-one with office
shoes, a Fallback that is always another row's sweater, Closet sizes
coprime with the number of Office and Home Days in a week. A closet
that satisfied the schema and none of that would produce confident
nonsense, and no amount of validation would catch it. So the tool pays
for a config boundary, a schema, a first-run flow and an example file
to buy generality for a user who cannot exist.

Meanwhile the thing the wearer actually needs to change, it cannot
change: clothes get replaced. A worn-out sweater means editing YAML by
hand, and because every garment is keyed by its color, editing that
YAML risks moving a Rotation.

## Solution

The Wardrobe becomes given. Its shape lives in source: two Closets,
their sizes, the three pairs of Pants they share, which Pants each
Shirt is welded to, and which sweater, shoes and jacket follow from
each pair. None of it can be added to, removed or re-paired while the
tool runs.

Everything the tool is told lives in one State file the tool reads and
writes and no human authors — the Labels, the three Anchors, the Day
Type Overrides, and the two facts about the wearer that were never
about clothes: the Office Weekdays and the Cold Threshold. There is no
third place, and in particular no file a person edits.

Every fact then has exactly one author. A Reset stops being a recorded
offset and becomes a move of its Rotation's Anchor, which drops the
offset term out of the Position formula entirely and takes the
tie-break rule with it. Replacing a garment becomes a command, and
because nothing is keyed by a Label it cannot disturb a Rotation.

What the wearer gets is a tool that works on a fresh install with no
setup, answers in one command, and takes every correction as a command
rather than an edit.

## User Stories

### Daily use

1. As someone getting dressed, I want to run one command with no
   arguments and see today's Outfit, so that I don't have to think
   about it.
2. As someone getting dressed, I want the Outfit to name the Shirt, its
   Pants and its shoes, so that I have the complete answer and not just
   part of it.
3. As someone getting dressed, I want to be told whether today is an
   Office Day or a Home Day, so that I can sanity-check the answer
   against my own plans.
4. As someone getting dressed on a cold day, I want to be told which
   Outerwear to wear, so that I'm not deciding that separately.
5. As someone getting dressed on a warm day, I want no Outerwear
   suggested at all, so that the output stays uncluttered.
6. As someone who wore something different from what was suggested, I
   want the tool to carry on without complaint the next day, so that a
   deviation doesn't require correcting anything.
7. As a new installer, I want the tool to answer immediately with no
   setup, so that there is nothing to configure before it is useful.

### Looking ahead

8. As someone planning a week, I want to ask what I'll be wearing on a
   specific future date, so that I can pack or plan around it.
9. As someone planning, I want look-ahead to use exactly the same rules
   as today, so that the answer I'm given is the answer I'll actually
   get on the day.
10. As someone planning past the weather forecast horizon, I want the
    Shirt, Pants and shoes anyway, so that a distant date still gives
    me most of the answer.
11. As someone planning past the forecast horizon, I want to be told
    which Outerwear that date calls for with only the cold/warm
    condition left open, so that I can tell "no Outerwear" apart from
    "that jacket, if it turns out cold".
12. As someone asking about a past date, I want to be refused with a
    clear reason, so that I am not handed a confident answer about what
    I wore that a later Reset has already rewritten.

### Office rules

13. As an office worker, I want a sweater never to repeat within a
    Monday-start Week, so that colleagues don't see me in the same
    sweater twice.
14. As an office worker, I want shoes never to repeat within a Week, so
    that the same rotation logic covers footwear.
15. As an office worker, I want the Fallback sweater chosen
    automatically when two Shirts in a Week share Pants, so that I
    never have to notice the collision myself.
16. As an office worker, I want a Fallback to move the shoes along with
    the sweater, so that the pairing stays coherent.
17. As an office worker who adds a fourth office day to a Week, I want
    a deterministic answer even though a repeat is unavoidable, so that
    the tool never fails to answer.
18. As an office worker in that situation, I want to be told a repeat
    is happening, so that I can choose to wear something else
    knowingly.

### Home rules

19. As someone at home, I want each Home Day to be a jacket day or a
    sweater day by the calendar alone, so that the answer never depends
    on which past days happened to be cold.
20. As someone at home on a warm day, I want that day to spend its turn
    anyway, so that the alternation keeps running whether or not I open
    the tool.
21. As someone at home, I want office sweaters to have no effect on the
    home alternation, so that the two settings stay independent.
22. As someone at home, I don't want a no-repeat rule applied, so that
    the home Closet stays simple.

### Changing what I own

23. As someone who replaced a sweater, I want one command to give that
    Garment a new Label, so that changing my clothes doesn't mean
    editing a file.
24. As someone replacing a Garment, I want the Rotations untouched, so
    that new clothes never change which Shirt I'm due.
25. As someone who mislabeled a Garment, I want the same command to
    correct it, so that there is no second concept to learn for what is
    the same event.
26. As someone replacing my black home shoes, which two pairs of Pants
    both call for, I want one command to change both, so that I cannot
    leave the two out of sync.
27. As someone replacing Pants, I want both Closets to follow, so that
    the one pair I own is named the same in both.
28. As someone naming a replacement, I want a Label that already names
    another Garment of the same kind in that Closet to be refused, so
    that the tool's output stays something I can act on.
29. As someone who wants two Shirts in a different order, I want to
    swap them, so that the Rotation presents them the way I prefer.
30. As someone swapping, I want Shirts that don't share Pants to be
    refused, so that a reorder can never quietly change which sweater
    or shoes a date calls for.
31. As someone who can't remember what's swappable, I want the Closet
    listing to show each Shirt's Pants, so that legal swaps are visible
    rather than discovered as an error.

### Seeing the Wardrobe

32. As someone whose Wardrobe is no longer a file I can open, I want a
    command that shows it, so that I can see what the tool thinks I
    own.
33. As someone reading that listing, I want the Shirts in Rotation
    order, so that I can see what's coming.
34. As someone about to replace a Garment, I want the listing to show
    how to address each one, so that I can copy a target rather than
    guess at it.

### Overrides and resets

35. As someone whose plans changed, I want to record that an Office Day
    is now a Home Day, so that the Outfit comes from the right Closet.
36. As someone whose plans changed, I want to record that a Home Day is
    now an Office Day, so that going in on a Saturday works.
37. As someone staying home, I want the office Rotation not to advance
    that day, so that the Shirt I skipped is simply deferred rather
    than lost.
38. As someone planning ahead, I want to record a Day Type Override for
    a future date, so that look-ahead reflects what I already know.
39. As someone with a holiday coming up, I want to record it as an
    ordinary Day Type Override, so that there's no separate concept to
    learn.
40. As someone who changed their mind about a date, I want recording
    the opposite to simply replace what I said, so that there is
    nothing to undo.
41. As someone whose Shirt is in the wash, I want a bare Reset to move
    to the next Shirt, so that the common case takes no arguments.
42. As someone with a specific Shirt in mind, I want to Reset directly
    to it by Label, so that I don't have to Reset repeatedly to reach
    it.
43. As someone resetting by Label, I want the Closet inferred from the
    day's type, so that I don't have to disambiguate.
44. As someone resetting by Label, I want an error if that Label isn't
    in the day's Closet, so that a typo doesn't silently do the wrong
    thing.
45. As someone who has Reset, I want every later date to follow, so
    that the Rotation stays continuous rather than snapping back.
46. As someone whose home Outerwear has drifted from what I actually
    wore, I want to Reset the Home Outerwear Rotation on its own, so
    that correcting it doesn't disturb the Shirt I'm due.
47. As someone typing that on a Wednesday, I want it to land on the
    next Home Day, so that "flip my next home Outerwear" works whenever
    I think of it.

### Changing when I go in and how cold I feel it

56. As someone whose office days moved from Monday, Wednesday, Friday
    to Tuesday, Thursday, Friday, I want one command to say so, so that
    I'm not recording two Day Type Overrides every week for the rest of
    my life.
57. As someone changing my office days, I want every Rotation left
    exactly where it stood, so that saying when I go in never changes
    which Shirt I'm due.
58. As someone who tries to say I go in five days a week, I want to be
    refused with a reason, so that I don't silently flatten the variety
    the Closet sizes exist to produce.
59. As someone who keeps feeling cold at the temperature the tool
    thinks is warm, I want one command to move the Cold Threshold, so
    that it matches what I actually feel rather than what it shipped
    believing.
60. As someone about to change either, I want the same command with no
    argument to show me the current value, so that I can see what the
    tool believes before I overwrite it.

### The State file

48. As the wearer, I want the tool to own its file completely, so that
    there is nothing I am expected to edit and nothing I can break by
    editing.
49. As the wearer, I want a recording that fails partway through to
    leave the previous State intact, so that a crash mid-write cannot
    cost me everything the tool knows.
50. As the wearer, I want the file to be readable if I ever do open it,
    so that I can see what the tool has been told.
51. As a fresh installer, I want no State file until I first change
    something, so that an untouched installation has nothing to go
    wrong with.

### Correctness over time

52. As an intermittent user, I want every Rotation to advance with the
    calendar even on days I don't run the tool, so that skipping a few
    days doesn't desynchronise anything.
53. As a user, I want weekends treated as ordinary Home Days, so that
    every date has exactly one answer.
54. As a user, I want the same Shirt always paired with the same Pants,
    so that the given combinations stay intact.
55. As a user, I want the same inputs to always produce the same
    answer, so that the tool is worth trusting.

## Implementation Decisions

### Architecture

- **Two seams, not one.** The single `handle` entry point is replaced
  by two pure functions:

  ```
  answer(state, on, weather) -> Response     # never changes anything
  apply(state, command, today) -> State      # never renders anything
  ```

  The shell composes them, so a command that records shows its result
  for free. This retires `handle`'s "resolve as though the decision
  were already in force" special case and makes every edit a
  State-in-State-out function.
- **`read_state` and `write_state` are the only new impure functions**,
  alongside reading the clock, fetching the forecast and printing.
- **One source module holds everything given** — the Wardrobe's
  structure, which is Closet sizes, Shirt-to-Pants welds and Pants
  Rows; the forecast coordinates; and the starting values the State
  overlays when no State file exists, which are the Labels, the
  Anchors, the Office Weekdays and the Cold Threshold. It stays
  `wardrobe.py`, because nearly everything in it and nearly every
  reference to it is the Wardrobe; its docstring is what says it holds
  the starting values too. "Structure" here means those *values*, not
  the types that describe them: `Closet`, `Shirt`, `PantsRow` and
  `Anchor` are declared in `model.py` with every other type, and
  `wardrobe.py` imports them to state its values.
- **`show-closet` gets no core seam.** The listing is a walk over the
  Wardrobe and the Labels, so it renders in the shell like every other
  output.

### What is deleted

- The config module in full: YAML schema, validation and all its error
  types. Duplicate Shirt Labels, unmapped Pants, a Fallback that is no
  other row's sweater, office sweaters not one-to-one with shoes, and
  an Anchor on the wrong kind of day all become properties of source
  that a test asserts once.
- The decisions module and its append-only log.
- The `Decision` union, the `Reset` record, the Rotation enum naming
  which Rotation a Reset shifts, the Reset-offset accumulator on
  `State`, and the anchor-supersedes-Resets cutoff.
- The missing-Wardrobe error and the first-run message.
- The example Wardrobe file and the test pinning the in-memory fixture
  to it.
- `pydantic` as a dependency. `pyyaml` stays, for the State file.

### The State file

- One YAML file in the platform user config directory, beside nothing.
  Written by a temporary file in the same directory followed by an
  atomic replace — a partial write must never be observable, which is
  the guarantee the append-only log used to provide for free.
- Holds five things: a Label per Garment, three Anchors, the Day Type
  Overrides, the Office Weekdays and the Cold Threshold. The last two
  arrive in 07 per ADR-0007; they are told facts about the wearer
  rather than about the Wardrobe, and they are five named facts in a
  flat file rather than two groups.
- **Nothing in it may reference a Garment by Label.** Labels move, so
  Anchors store Positions and the Overrides are keyed by date. A Label
  appears only at the edges: typed at a command, printed in an answer.
- A missing file is not an error and not a first run — it reads as the
  starting values with no Overrides, and so does a file written before
  a later ticket added a field. The directory is created
  the first time something is written.
- Day Type Overrides are a date-keyed mapping rather than a list, so
  recording the opposite for a date is an overwrite. The
  "a later record wins for the same date" scan is gone.

### Garment identity

- Within one Closet, one Label names exactly one Garment: home shoes
  called for by two Pants Rows are one pair, and a jacket called for by
  two Pants Rows is one jacket. Replacing either is one command.
- Across the two Closets, the same Label names two different Garments —
  the office and home Closets hold different shirts, sweaters and shoes
  that happen to share color names.
- **Pants are the exception that crosses.** There is one set of
  trousers and both Closets wear it. What they are worn *with* differs
  by Closet, which is the Pants Row.
- A Fallback points at a Garment, not at a Label, which is what stops a
  replacement from breaking the wiring.

### Position derivation

- Every Rotation derives its Position the same way:

  ```
  position(date) = (anchor.position + days_of_that_type_between(anchor.date, date)) mod len(rotation)
  ```

  The Shirt Rotations use their Closet's size; the Home Outerwear
  Rotation uses 2. There is no offset term: a Reset moves the Anchor.
- **Three Anchors, one per Rotation** — office Shirt, home Shirt, home
  Outerwear — each moved independently. This is what lets a Home
  Outerwear Reset issued on an Office Day land cleanly without
  disturbing a Shirt Anchor that has to sit on a day of its own kind.
- Each Anchor stores a **Position**, never a Label, so a Replace or a
  Swap cannot move it.
- Counting backwards from an Anchor is still required internally: the
  office Week walk resolves Monday and Wednesday to answer Friday, and
  a mid-Week Reset puts the Anchor after them. It must not be
  simplified away on the grounds that past dates are refused.

### Resolution

- Office sweater resolution walks the Week's Office Days in date order
  from Monday, taking each Shirt's Pants-mapped sweater unless already
  used that Week, in which case the Fallback. If both are taken — only
  reachable when a Week has four or more Office Days — take the primary
  anyway and mark the Response as having a repeat.
- Home Outerwear resolution: the Home Outerwear Rotation's Position
  says whether the date is a sweater day or a jacket day, and the Pants
  Row supplies the garment. At or above the threshold no Outerwear is
  worn and the day still spends its turn. Office sweaters are never
  consulted.
- Office Outerwear has no alternation — below the threshold you wear
  the Pants-mapped sweater.
- The Response distinguishes three Outerwear states: worn, not worn,
  and named-but-conditional for dates whose temperature is unknown.

### Commands

- Subcommands, with a bare invocation meaning today and `--on` staying
  a root flag because it modifies the default question rather than
  being its own verb:

  ```
  what2wear                            today
  what2wear --on <date>                a future date
  what2wear stay-home [date]
  what2wear go-in [date]
  what2wear reset [label]
  what2wear reset-outerwear
  what2wear replace <target> <label>
  what2wear swap <closet> <label> <label>
  what2wear show-closet
  what2wear office-weekdays [mon wed fri]
  what2wear cold-threshold [55]
  ```

- **A Garment is addressed by a dotted target** — `office.shirt.white`,
  `home.shoes.black`, `pants.grey` — because a Label alone is unique
  only within a Closet and a kind. One positional, no irregular arity
  for the Pants case, and `show-closet` prints the targets so one can
  be copied. Recorded as the least-bad option on a surface that is
  deliberately disposable, not as a good one.
- `swap` needs no dotted target: it only ever applies to Shirts, so the
  Closet and two Labels are unambiguous.
- `--on` with a past date is an error naming why.
- `show-closet` prints both Closets, Shirts in Rotation order, with
  each Shirt's Pants in its own column so that legal swaps are
  visible by scanning one column.
- The CLI remains deliberately disposable — a thin renderer over the
  two seams, expected to be replaced by a phone-friendly UI later.

### Weather

- Open-Meteo, no API key, fixed coordinates, Cold Threshold starting
  in source at 50°F. Forecast endpoint only; no historical archive.
- Dates beyond the forecast horizon resolve the Shirt, Pants, shoes
  *and the named Outerwear garment*, hedging only the cold/warm
  condition.
- A failed or unavailable forecast degrades identically to being past
  the horizon, never to an error.

### Migration

- The existing hand-authored Wardrobe at the platform config path is
  read once by hand: its Labels and Anchors move into source, and the
  file is deleted. No migration code — it is a one-time move of thirty
  strings and two dates for a single user.
- The real Labels ship in source. ADR-0005 records that the earlier
  anonymization is deliberately undone; the repository is private.

## Testing Decisions

### What makes a good test here

Tests drive the two seams with an in-memory State, an explicit `today`
and an explicit weather mapping. Nothing is mocked, no files are
touched, no network is used and the clock is never read. `answer` tests
assert on the returned Response; `apply` tests assert on the returned
State. Neither may reach into how a Position was computed or how a Week
was walked, so the internals stay free to be restructured.

`apply` is the cheaper surface and should carry the weight of every
mutation case: it takes a State and a command and returns a State, so
"what did this command actually change" is a single value comparison.

### Coverage

- **A worked calendar.** The Aug 15–24 2026 sequence stays the primary
  integration test, re-cut so that `today` sweeps forward across the
  range rather than one `today` asking about the whole of it — past
  dates are no longer answerable. It exercises the home wrap, the
  Friday Aug 21 sweater Fallback, the shoes moving with that Fallback,
  and the Week resetting cleanly on Monday Aug 24.
- **All five office Week shapes.** Five Shirts and three Office Days
  are coprime, so the shapes cycle over five weeks; two require a
  Fallback and three don't, and all five are asserted.
- **Four-office-day Weeks.** A `go-in` producing an unavoidable repeat
  returns a deterministic Outfit and flags the repeat.
- **Outerwear alternation.** Jacket, sweater, jacket across consecutive
  Home Days; a warm day in the middle spending its turn silently so the
  days either side land on the same kind; office sweaters interleaved
  and shown to have no effect.
- **Resets as Anchor moves.** A bare Reset advances by one; a Reset to
  a named Label computes the right Position; every later date follows;
  a Label from the wrong Closet errors. A Shirt Reset leaves the
  Outerwear Anchor untouched and an Outerwear Reset leaves the Shirt
  Anchor untouched. An Outerwear Reset on an Office Day lands on the
  next Home Day.
- **The mid-Week Reset consequence.** A Wednesday Reset changing what
  the Week's walk believes Monday spent, and therefore Friday's
  Fallback, is asserted directly rather than avoided — ADR-0001 accepts
  it knowingly and a test is what stops it being "fixed" later.
- **Overrides.** Staying home leaves the office Position untouched so
  the skipped Shirt appears on the next Office Day; going in advances
  it; a future-dated Override changes look-ahead; recording the
  opposite for a date replaces rather than stacks.
- **Replace.** A replacement changes the Label and no Position; a
  shared home shoe or jacket changes for both Pants Rows at once; Pants
  change in both Closets; a Label duplicating another Garment of the
  same kind in the same Closet is refused.
- **Swap.** Two Shirts sharing Pants exchange Labels and nothing else
  in the resolved Outfit changes for any date; two Shirts with
  different Pants are refused; a Label absent from that Closet is
  refused.
- **Past dates.** `--on` with a date before today errors, while the
  office Week walk still resolves earlier days of the current Week
  internally.
- **Horizon.** A date past the forecast window returns Shirt, Pants,
  shoes and the named Outerwear garment with only the condition
  hedged; an unavailable forecast degrades identically. Both Closets.
- **Office Weekdays and the Cold Threshold.** Exactly three weekdays
  are accepted and every other count refused; setting them changes no
  date's Outfit by itself, because all three Anchors move with the
  change; restating the current three changes nothing; a mid-Week
  change moving that Week's Fallback is asserted rather than avoided;
  and a new Cold Threshold changes whether Outerwear is worn and no
  Position.
- **The State file round-trips.** A State written and read back is the
  same State, and a missing file reads as the given Labels and Anchors
  with no Overrides.
- **Determinism.** The same inputs always produce the same Response,
  and look-ahead to a date matches what that date returns when it
  arrives, absent intervening commands.

### Prior art

The existing suite is the pattern to follow: table-driven parametrised
cases against pure functions, fixtures built in memory, no mocks. What
changes is that there is no longer a file to pin fixtures against —
the Wardrobe under test *is* the given one, so the fixture-versus-file
test is deleted rather than re-pointed.

## Out of Scope

- **Adding or removing a Garment.** Closet sizes are fixed in source
  per ADR-0005. A sixth office Shirt is a source change and a commit.
- **Re-pairing.** Which sweater follows which Pants is structure. A
  Swap looks like a re-pairing and deliberately is not.
- **Changing how many days a week are Office Days.** Which three
  weekdays they are became told in 07; that there are three is
  structure, for the reasons ADR-0007 records, and stays a source
  change with the same standing as a sixth office Shirt.
- **Changing the forecast coordinates at runtime.** Coordinates change
  when the wearer moves house, which is rarer than most source changes
  this repo makes, and a wrong one fails loudly rather than quietly.
- **Any UI beyond the CLI.** The phone-usable interface is the eventual
  goal and the seams are being shaped for it, but nothing web, hosted
  or authenticated is built here.
- **Undo.** Every mutation is idempotent by restatement — recording the
  opposite Day Type, resetting to the Shirt actually wanted, replacing
  a Label again. An undo stack would put back the history the State
  file exists to not have.
- **Wear history.** The tool says what to wear; it does not record what
  was actually worn. This is why past dates are refused rather than
  answered.
- **Historical weather.** No archive endpoint. Past weather affects no
  Position and no Outerwear identity.
- **Garment-level availability.** No "these shoes are at the cobbler,
  route around them".
- **Multiple users, sync, auth, deployment.**
- **Generating combinations.** Shirts and their Pants are given, never
  assembled from separate lists.
- **Migration code** for the superseded config file. A one-time hand
  move.

## Further Notes

- `CONTEXT.md` is authoritative for naming. Rotation (choosing the
  Shirt, or the kind of Outerwear) and Resolution (deciding everything
  else about the day) are distinct steps and shouldn't be conflated in
  code or tests.
- Six ADRs govern this area. ADR-0005 and ADR-0006 are new and record
  the decisions this spec implements; ADR-0007 amends ADR-0006's "and
  nothing else" to let the State hold told facts that are not about
  clothes. ADR-0001 and ADR-0003 are amended
  — read the amendment notes at the top of each. ADR-0002 is superseded
  by ADR-0004 and describes a stored cursor that no longer exists.
- The nine-Shirt home and five-Shirt office Closets are coprime with
  four Home Days and three Office Days per Week, so the same Shirt
  takes nine and five Weeks to return to the same weekday. The Home
  Outerwear Rotation's 2 is likewise coprime with 9. Under ADR-0005
  these are now guaranteed by source rather than merely true of the
  current configuration, but nothing enforces them if the source
  changes — a six-Shirt office Closet would put the same Shirt on
  alternate Mondays. This is also why 07 lets the wearer say *which*
  three weekdays they go in and never *how many*: at five Office Days
  a week the same office Shirt would land on every Monday forever.
- Build order: the given Wardrobe and the State file first, then the
  two seams over them, then the commands, then Outerwear and weather
  last, and the two told facts that are not about clothes last of all.
  The old tickets 05 and 06 are re-cut under this spec rather than
  ported.
