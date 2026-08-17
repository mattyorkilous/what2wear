# Outfit Rotation

Status: ready-for-agent

## Problem Statement

Deciding what to wear every morning is a small, recurring, and entirely avoidable decision. The clothes are already known, and which combinations work together is already settled — what's missing is a rule for cycling through them so the same shirt doesn't come round too often, the same sweater doesn't appear twice in a week at the office, and the choice is different depending on whether the day involves going in.

Doing it by memory fails in specific ways: you can't remember what you wore three days ago, you can't tell what you'll be wearing next Tuesday, and you end up in the same thing every Monday. Going into the office some days and not others makes it worse, because the two settings draw on different clothes and drift out of step with each other.

## Solution

A tool that answers "what am I wearing today" in one command, and "what will I be wearing on any given date" in another.

It walks a fixed, hand-authored list of Shirts — one Closet for the office, one for home — advancing each Rotation only on days of its own kind. Pants come welded to the Shirt. Shoes and sweaters follow from the pants. At the office it guarantees no sweater and no pair of shoes repeats within a Monday-start Week, falling back to an alternate sweater when two Shirts in the same Week share pants. At home, jacket and sweater alternate across Home Days on their own Rotation, so every Home Day is a jacket day or a sweater day before the weather is consulted at all; the temperature decides only whether the Layer gets worn.

Because every Position is derived from the calendar rather than stored, looking ahead is the same operation as looking at today, and the Rotations stay correct whether or not the tool gets used on a given day. Overrides let a day switch sides (staying home on an office day, going in on a home day, a holiday), and a reset shifts the Rotation when the Shirt on offer isn't wanted.

## User Stories

### Daily use

1. As someone getting dressed, I want to run one command with no arguments and see today's Outfit, so that I don't have to think about it.
2. As someone getting dressed, I want the Outfit to tell me the Shirt, its pants, and its shoes, so that I have the complete answer and not just part of it.
3. As someone getting dressed, I want to be told whether today is an Office Day or a Home Day, so that I can sanity-check the answer against my own plans.
4. As someone getting dressed on a cold day, I want to be told which Layer to wear, so that I'm not deciding that separately.
5. As someone getting dressed on a warm day, I want no Layer suggested at all, so that the output stays uncluttered.
6. As someone who wore something different from what was suggested, I want the tool to carry on without complaint the next day, so that a deviation doesn't require correcting anything.

### Looking ahead

7. As someone planning a week, I want to ask what I'll be wearing on a specific future date, so that I can pack or plan around it.
8. As someone planning, I want look-ahead to use exactly the same rules as today, so that the answer I'm given is the answer I'll actually get on the day.
9. As someone planning past the weather forecast horizon, I want the Shirt, pants and shoes anyway, so that a distant date still gives me most of the answer.
10. As someone planning past the forecast horizon, I want to be told which Layer that date calls for with only the cold/warm condition left open, so that I can tell "no Layer" apart from "that jacket, if it turns out cold".
11. As someone planning, I want to ask about a past date, so that I can check what the rule says I wore.

### Office rules

12. As an office worker, I want a sweater never to repeat within a Monday-start Week, so that colleagues don't see me in the same sweater twice.
13. As an office worker, I want shoes never to repeat within a Week, so that the same rotation logic covers footwear.
14. As an office worker, I want the Fallback sweater chosen automatically when two Shirts in a Week share pants, so that I never have to notice the collision myself.
15. As an office worker, I want a Fallback to move the shoes along with the sweater, so that the pairing stays coherent.
16. As an office worker who adds a fourth office day to a Week, I want a deterministic answer even though a repeat is unavoidable, so that the tool never fails to answer.
17. As an office worker in that situation, I want to be told a repeat is happening, so that I can choose to wear something else knowingly.

### Home rules

18. As someone at home, I want each Home Day to be a jacket day or a sweater day by the calendar alone, so that the answer never depends on which past days happened to be cold.
19. As someone at home on a warm day, I want that day to spend its turn anyway, so that the alternation keeps running whether or not I open the tool. A mild Tuesday between two cold days will put me back in the same kind of Layer on the Wednesday, which I accept as the price of never storing anything.
20. As someone at home, I want office sweaters to have no effect on the home alternation, so that the two settings stay independent.
21. As someone at home, I don't want a no-repeat rule applied, so that the home Closet stays simple.

### Overrides and resets

22. As someone whose plans changed, I want to record that an Office Day is now a Home Day, so that the Outfit comes from the right Closet.
23. As someone whose plans changed, I want to record that a Home Day is now an Office Day, so that going in on a Saturday works.
24. As someone staying home, I want the office Rotation not to advance that day, so that the Shirt I skipped is simply deferred rather than lost.
25. As someone planning ahead, I want to record a Day Type Override for a future date, so that look-ahead reflects what I already know.
26. As someone with a holiday coming up, I want to record it as an ordinary Day Type Override, so that there's no separate concept to learn.
27. As someone whose Shirt is in the wash, I want a bare reset to move to the next Shirt, so that the common case takes no arguments.
28. As someone with a specific Shirt in mind, I want to reset directly to it by name, so that I don't have to reset repeatedly to reach it.
29. As someone resetting by name, I want the Closet inferred from the day's type, so that I don't have to disambiguate.
30. As someone resetting by name, I want an error if that Shirt isn't in the day's Closet, so that a typo doesn't silently do the wrong thing.
31. As someone who has reset, I want every later date to shift with it, so that the Rotation stays continuous rather than snapping back.
32. As someone whose home Layer has drifted from what I actually wore, I want to reset the Home Layer Rotation on its own, so that correcting it doesn't disturb the Shirt I'm due.

### Configuration

33. As the owner of the wardrobe, I want to author both Closets in a YAML file, so that changing my clothes doesn't mean changing code.
34. As the owner, I want to author sweater, jacket and shoe mappings keyed by pants rather than by Shirt, so that there are three rows to maintain instead of nine.
35. As the owner, I want to set which weekdays are Office Days, so that a schedule change is a config edit.
36. As the owner, I want to set the temperature threshold below which a Layer is recommended, so that I can tune it by season or preference.
37. As the owner, I want to set the Anchor Date for each Closet as a date plus the Shirt worn that day, so that re-anchoring reads the way I actually think about it.
38. As the owner, I want the home Anchor Date to name the Layer worn that day as well, so that the alternation starts where I say it does rather than at an arbitrary phase.
39. As the owner, I want my hand-written YAML never rewritten by the tool, so that comments and formatting survive.
40. As the owner, I want recorded decisions kept in append-only files separate from my config, so that a recorded override can never corrupt my Closet.

### Correctness over time

41. As an intermittent user, I want every Rotation to advance with the calendar even on days I don't run the tool, so that skipping a few days doesn't desynchronise anything.
42. As a user, I want weekends treated as ordinary Home Days, so that every date has exactly one answer.
43. As a user, I want the same Shirt always paired with the same pants, so that the authored combinations stay intact.

## Implementation Decisions

### Architecture

- **Functional core, imperative shell.** All domain logic lives in pure functions. The shell reads files, reads the clock, fetches the forecast, prints, and appends — nothing else.
- **One seam.** Every command routes through a single pure entry point:

  ```
  handle(command, state, today, weather) -> Response
  ```

  `state` is the parsed Closets plus all recorded decisions. `weather` is a mapping of date to daily high. `Response` carries what to display and, optionally, a decision to append. Confirmed with the developer as the intended test surface.

- **Uniform purity, per ADR-0001 and ADR-0004.** Shirt, pants, shoes, office sweaters and the kind of home Layer are all pure functions of the calendar and resolve for any date, past or future. Nothing is stored and nothing is consumed. Weather is the only input that can be missing, and it gates only whether a Layer is worn.

### Domain model

- A **Closet** is an ordered list of **Shirts**. Each Shirt carries its welded pants. The Office Closet has 5 Shirts; the Home Closet has 9.
- Sweaters, jackets and shoes are **keyed by pants, not by Shirt**. Each Closet has its own three-row mapping. This is why Fallbacks are needed at all: a sweater collision is exactly two office Shirts in the same Week sharing pants.
- The office sweater mapping additionally carries a Fallback sweater per pants colour, used when the primary is already taken that Week.
- Office shoes are a bijection with office sweaters, so resolving the sweater resolves the shoes and the no-repeat-shoes guarantee follows for free. Home shoes are not a bijection (two pants colours share a pair), which is acceptable because no home no-repeat rule exists.

### Position derivation

- **Position** is derived, never stored, for every Rotation:

  ```
  position(date) = (days_of_that_type_between(anchor, date) + reset_offsets_before(date)) mod len(rotation)
  ```

  The Shirt Rotations use `len(closet)`; the Home Layer Rotation uses `2`. Both home Rotations count the same Home Days but carry their own Reset offsets, so shifting one leaves the other alone.

- Each Closet has its own **Anchor Date**, expressed as a date and the Shirt worn on it. The office anchor is a date that is an Office Day; the home anchor a date that is a Home Day, and it additionally names the Layer worn — `sweater` or `jacket` — which fixes Position 0 of the Home Layer Rotation. The field is required rather than defaulted: a defaulted phase is an arbitrary one nobody can see.
- **Day Type Overrides** are `(date, office|home)` records. They take precedence over the weekly weekday pattern, apply to any date past or future, and are the single mechanism covering staying home, going in, holidays and leave. An override moves both home Rotations, because both count Home Days.
- **Resets** are recorded as `(date, rotation, offset)` — a signed offset effective from that date forward, permanently, against one named Rotation. A bare Shirt reset records `+1`. A reset naming a Shirt records the delta from the derived Shirt to the named one, resolved within the Closet implied by that date's type; naming a Shirt absent from that Closet is an error. A Layer reset records `+1` against the Home Layer Rotation and takes no argument: over two items, "advance by one" and "flip to the other" are the same operation, so a named form could only ever be a redundant no-op. It is legal on an Office Day — that day doesn't consult the Home Layer Rotation, but the offset lands cleanly on the next Home Day, and "flip my next home Layer" is a reasonable thing to type on a Wednesday.

### Resolution

- Office sweater resolution walks the Week's Office Days in date order from Monday, taking each Shirt's pants-mapped sweater unless already used that Week, in which case the Fallback. If both are taken — only reachable when a Week has four or more Office Days — take the primary anyway and mark the Response as having a repeat.
- Home Layer resolution: the Home Layer Rotation's Position says whether the date is a sweater day or a jacket day, and the pants row supplies the garment. If the daily high is at or above the threshold, no Layer is worn — the day still spends its turn. Office sweaters are never consulted.
- Office Layer resolution has no alternation — below the threshold, the pants-mapped sweater is worn.
- One threshold covers both kinds. Per-kind thresholds are now *possible*, since the kind is known before the temperature is, but they aren't wanted yet and splitting the value later is a config change the model doesn't resist.

### Persistence

- Two files, both under the platform's user config directory.
- Hand-authored Closet config in YAML, parsed and validated with pydantic at the boundary. Never written by the tool.
- Recorded decisions (Day Type Overrides and Resets) in an append-only log. There is no second log: per ADR-0004 nothing about a Layer needs recording.

### Weather

- Open-Meteo, no API key. Fixed coordinates for the Washington DC area. Threshold defaults to 50°F, configurable.
- Only the forecast endpoint is used; no historical archive. Dates beyond the forecast horizon resolve Shirt, pants, shoes *and the Layer garment* normally — all of them derive from the calendar — and hedge only the cold/warm condition.
- A failed or unavailable forecast degrades the same way as being past the horizon rather than failing the command.

### CLI

- Flags take a `--` prefix. Bare invocation shows today.
- `--on <date>`, `--stay-home [date]`, `--go-in [date]`, `--reset [shirt]`, `--reset-layer`. Date arguments default to today.
- The CLI is deliberately disposable — a thin renderer over `handle`, expected to be replaced by a phone-friendly UI later.

### Tooling

- uv, ruff, pytest, pydantic. Python 3.14. No polars and no pandas — the data is a few dozen records, and a dataframe engine would earn nothing here.

## Testing Decisions

### What makes a good test here

Tests drive the single `handle` seam with in-memory `state`, an explicit `today`, and an explicit weather mapping. Nothing is mocked, no files are touched, no network is used, and the clock is never read — every input the core needs is passed to it. Tests assert on the returned `Response`: the resolved Outfit and any decision to append. They must not reach into how a Position was computed or how a Week was walked, so that the internals can be restructured freely.

### Coverage

Everything is tested through `handle`. The dense cases:

- **A worked calendar.** The agreed Aug 15–24 2026 sequence is the primary integration test: it exercises the home wrap from lgreen back to white, the Friday Aug 21 sweater Fallback where tan pants want black but Monday already took it, the shoes moving from black to white alongside that Fallback, and the Week resetting on Monday Aug 24 so lblue takes grey cleanly.
- **All five office Week shapes.** Because 5 Shirts and 3 Office Days are coprime, the Week shapes cycle over five weeks. Two of them require a Fallback and three don't; all five are asserted.
- **Four-office-day Weeks.** A `--go-in` producing an unavoidable repeat returns a deterministic Outfit and flags the repeat.
- **Layer alternation.** Jacket, sweater, jacket across consecutive Home Days; a warm day in the middle spending its turn silently, so the days either side of it land on the *same* kind — the consequence ADR-0004 accepts, asserted rather than avoided; office sweaters interleaved and shown to have no effect.
- **Layer resets.** `--reset-layer` flips every subsequent Home Day and leaves the Shirt Rotation untouched; a Shirt reset leaves the Layer Rotation untouched; one issued on an Office Day lands on the next Home Day.
- **Overrides.** Staying home leaves the office Position untouched so the skipped Shirt appears on the next Office Day; going in advances it; a future-dated override changes look-ahead; a holiday behaves identically to any other override.
- **Resets.** Bare reset advances by one; a named reset computes the right delta; every later date shifts; a name from the wrong Closet errors.
- **Horizon.** A date past the forecast window returns Shirt, pants, shoes and the named Layer garment, with only the cold/warm condition hedged; an unavailable forecast degrades identically. Covered for both Closets.
- **Determinism.** The same inputs always produce the same Response, and look-ahead to a date matches what that date returns when it arrives, absent intervening decisions.

### Prior art

None — this is the first code in the repo. These tests set the pattern: table-driven parametrised cases against one pure function, fixtures built in memory.

## Out of Scope

- **Any UI beyond the CLI.** The phone-usable interface is the eventual goal and the core is being shaped for it, but nothing web, hosted, or authenticated is built here.
- **Editing the Closet through a UI.** Config is hand-authored YAML for now. When UI editing arrives the tool will start writing that file and comments will be lost; that trade is deliberately deferred.
- **Wear history.** The tool says what to wear; it does not record what was actually worn. This is why ADR-0001 accepts that editing a Closet rewrites the past.
- **Closet versioning.** Adding a Shirt reshuffles every derived Position. Accepted, not mitigated.
- **Historical weather.** No archive endpoint. Nothing needs one now: past weather no longer affects any Position, only whether a Layer you already know the name of was worn.
- **Garment-level availability.** No "these shoes are at the cobbler, route around them". Would require garment identity, which the pants-keyed model deliberately avoids.
- **Multiple users, sync, auth, deployment.**
- **Generating combinations.** Shirts and their pants are authored by hand, never assembled from separate lists.
- **Laundry, packing, travel, occasion-specific dressing.**

## Further Notes

- The glossary in `CONTEXT.md` is authoritative for naming. In particular Rotation (choosing the Shirt, or the kind of Layer) and Resolution (deciding everything else about the day) are distinct steps and shouldn't be conflated in code or tests. Bare "Rotation" means the Shirt Rotation where no Layer is in scope; qualify it wherever both are live.
- Two ADRs govern this area and should be read before changing the core: ADR-0001 on Positions being derived from the calendar, and ADR-0004 on the home Layer alternation riding that same derivation. ADR-0002 recorded the opposite and is superseded; a reader who finds the stored-cursor design described anywhere is looking at retired reasoning.
- The 9-Shirt home and 5-Shirt office Closets are coprime with 4 home days and 3 office days per Week respectively, so the same Shirt takes 9 and 5 Weeks to return to the same weekday. This is a desirable property of the current sizes rather than something the code enforces — a 6-Shirt office Closet would put the same Shirt on alternate Mondays.
- The Home Layer Rotation's 2 is likewise coprime with the home Closet's 9, so a given Shirt takes 18 Home Days to meet the same kind of Layer again. Also unenforced: an even-sized home Closet would weld every Shirt to one kind of Layer forever.
- Build order: pure core first, then config loading and the event log, then the CLI, then weather and Layers last. The core is testable in full before any I/O exists.
