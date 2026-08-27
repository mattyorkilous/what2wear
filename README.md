# what2wear

Tells you what to wear today, and what you'll wear on any other day.

It walks a fixed list of shirts — one closet for the office, one for home — advancing each rotation only on days of its own kind. Pants come welded to the shirt; shoes and sweaters follow from the pants. At the office it guarantees no sweater and no pair of shoes repeats within a Monday-start week. At home, when it's cold, it alternates jacket and sweater so the same kind of outerwear never comes twice running.

> **Status: the given wardrobe.** There is nothing to install and nothing to configure — the wardrobe lives in source, so a fresh checkout answers straight away. `what2wear` and `what2wear --on <date>` give you the shirt, its pants, its sweater, its shoes and whether it's an office day; a past date answers too, with a note that it says where the rotation stands now rather than what was worn. `stay-home` and `go-in` switch a date's side, and `reset` moves the shirt rotation on for good. Every command acts on one date, which is today unless `--on` says otherwise. Everything it's been told lives in one state file it owns. Replace and swap, outerwear and weather are still ahead.

## How it works

**Rotation picks the shirt. Resolution decides everything else.** Those are deliberately separate steps, and the glossary keeps them apart.

The rotation position for any date is *derived* from the calendar rather than stored as a cursor:

```
position(date) = (anchor.position + days_of_that_type_since_anchor) mod len(closet)
```

There is no offset term: a reset moves the anchor, so the whole rotation comes with it. That one choice shapes the whole design. Looking ahead to a future date is the same function call as looking at today, not a separate simulation that can drift. The rotation also stays correct whether or not you run the tool on a given day — you wore clothes either way. See [ADR-0001](docs/adr/0001-positions-derived-from-the-calendar.md).

Resolution keys off **pants, not shirts** — there is one set of pants and both closets wear it, each carrying its own row per pair, holding the sweater, shoes and jacket that follow from it. This is also why fallbacks exist at all: an office sweater collision is precisely two shirts in the same week sharing pants. See [ADR-0003](docs/adr/0003-garments-are-keyed-by-pants-not-by-shirt.md).

Home outerwear alternates on the calendar too. Every home day is a jacket day or a sweater day by its own rotation, and the weather decides only whether the outerwear gets worn — so a mild day in the middle of a cold stretch spends its turn wearing nothing, and you can land on the same kind of outerwear either side of it. That trade buys a system with nothing stored anywhere. See [ADR-0004](docs/adr/0004-home-outerwear-alternates-on-the-calendar.md), which supersedes ADR-0002.

## Interface

A deliberately disposable CLI, to be replaced later by something usable from a phone.

```
what2wear                            # today's outfit
what2wear --on 2026-08-24            # any other date, past or future
what2wear stay-home                  # this office day is now a home day
what2wear go-in                      # this home day is now an office day
what2wear reset [shirt]              # move on to the next shirt, or jump to a named one
what2wear reset lblue --on 2026-09-07  # every command takes --on, defaulting to today
```

Holidays and leave aren't separate concepts — they're just `stay-home` on the relevant date.

## The wardrobe is given

There is no configuration. Both closets, the pants they share, the office weekday pattern and the anchors a fresh install starts from all live in [`src/what2wear/wardrobe.py`](src/what2wear/wardrobe.py), because the rules only mean anything against this wardrobe's shape — office sweaters one-to-one with office shoes, a fallback that is always another row's sweater, closet sizes coprime with the office and home days in a week. A stranger's closet satisfying a schema and none of that would produce confident nonsense, and no amount of validation would catch it. See [ADR-0005](docs/adr/0005-what2wear-dresses-one-person-from-a-given-wardrobe.md).

So there is nothing to write, nothing to copy and no first run. The properties the rules lean on — those pairings, those sizes — are asserted once by `tests/test_wardrobe.py`.

An anchor is a date and the position a rotation stood at on it — a position rather than a shirt name, so that renaming a garment can never move a rotation. With nothing yet recorded the anchor is *today* at position 0, so a fresh install opens on `white` in whichever closet the day calls for; the first thing you record pins it, and from then on it stands still.

A pants row's `fallback` is the sweater to take when the row's own is already worn that week. It is always another row's own, which is what lets the fallback bring that row's shoes along with it.

## The state is one file the tool owns

Everything it's been told — the two anchors and the day type overrides — lives in `state.json` in your platform's user config directory (`~/Library/Application Support/what2wear` on macOS, `~/.config/what2wear` on Linux). Nobody authors it and there is nothing in it to edit; it is readable if you open it, but you are not expected to. There is no flag, environment variable or working-directory fallback to point it elsewhere: where it lives is a property of the installation, not of an invocation. The directory arrives with the first record; until then an installation has no files at all.

It is rewritten whole rather than appended to, so it is written to a temporary file beside it and moved into place atomically — a recording that fails partway leaves the previous state intact. See [ADR-0006](docs/adr/0006-the-wardrobe-is-source-the-state-is-one-file-the-tool-owns.md).

## Layout

```
CONTEXT.md                  glossary — authoritative for naming
docs/adr/                   architecture decisions
docs/agents/                conventions for agent workflows
.scratch/given-wardrobe/    spec and implementation tickets
src/what2wear/              the package
src/what2wear/wardrobe.py   the given wardrobe
```

## Design

The architecture is a functional core with an imperative shell, and the core has two pure seams:

```
answer(state, on) -> Response      # never changes anything
apply(state, command, today) -> State   # never renders anything
```

The shell composes them, so a command that records shows its result for free. It only reads and writes the state file, reads the clock, fetches the forecast and prints. Those two seams are the whole test surface — no mocks, no files touched, no clock reads outside the shell's own tests. The wardrobe under test is the given one, so there is no fixture that can drift from what ships.

Read [`CONTEXT.md`](CONTEXT.md) before touching anything, then the ADRs for the area you're working in.

Built with uv, ruff and pytest. No dataframe library — the data is a few dozen records.
