# what2wear

Tells you what to wear today, and what you'll wear on any other day.

It walks a fixed list of shirts — one closet for the office, one for home — advancing each rotation only on days of its own kind. Pants come welded to the shirt; shoes and sweaters follow from the pants. At the office it guarantees no sweater and no pair of shoes repeats within a Monday-start week. When it's cold you wear the outerwear your pants call for — at the office their sweater, at home their sweater or their jacket, whichever kind the day's turn says.

> **Status: the given wardrobe.** There is nothing to install and nothing to configure — the wardrobe lives in source, so a fresh checkout answers straight away. `what2wear` and `what2wear --on <date>` give you the shirt, its pants, its shoes, whether it's an office day, and whether today's forecast calls for its sweater or jacket; a past date answers too, with a note that it says where the rotation stands now rather than what was worn. `stay-home` and `go-in` switch a date's side, `reset` moves the shirt rotation to a shirt you name, and `reset-outerwear` moves the home outerwear rotation on to the other kind. `replace` gives a garment a new label, `swap` reorders two shirts that share pants, and `show-closet` lists everything with the name to copy into either. Every command that acts on a date takes today unless `--on` says otherwise. Everything it's been told lives in one state file it owns.

## How it works

**Rotation picks the shirt. Resolution decides everything else.** Those are deliberately separate steps, and the glossary keeps them apart.

The rotation position for any date is *derived* from the calendar rather than stored as a cursor:

```
position(date) = (anchor.position + days_of_that_type_since_anchor) mod len(closet)
```

There is no offset term: a reset moves the anchor, so the whole rotation comes with it. That one choice shapes the whole design. Looking ahead to a future date is the same function call as looking at today, not a separate simulation that can drift. The rotation also stays correct whether or not you run the tool on a given day — you wore clothes either way. See [ADR-0001](docs/adr/0001-positions-derived-from-the-calendar.md).

Resolution keys off **pants, not shirts** — there is one set of pants and both closets wear it, each carrying its own row per pair, holding the sweater, shoes and jacket that follow from it. This is also why fallbacks exist at all: an office sweater collision is precisely two shirts in the same week sharing pants. See [ADR-0003](docs/adr/0003-garments-are-keyed-by-pants-not-by-shirt.md).

Home outerwear alternates on the calendar too. Every home day is a jacket day or a sweater day by its own rotation, and the weather decides only whether the outerwear gets worn — so a mild day in the middle of a cold stretch spends its turn wearing nothing, and you can land on the same kind of outerwear either side of it. That trade buys a system with nothing stored anywhere. See [ADR-0004](docs/adr/0004-home-outerwear-alternates-on-the-calendar.md), which supersedes ADR-0002.

## Outerwear and the weather

Below 50°F you wear outerwear; at or above it, none, and no outerwear line is printed. The forecast decides only *whether*: which garment a date calls for is worked out without it, so a date too far out for the forecast still names one:

```
  sweater  beige                  # cold: wear it
                                  # warm: no outerwear line
  sweater  beige, if it's cold    # no forecast for that date yet
```

The last is also what you get when the forecast can't be fetched at all. A network problem never stops the tool answering — it just can't say yet whether you'll want it.

At the office it is always a sweater — the one your pants call for, or the week's fallback when that one is taken. A warm Monday still spends its sweater for the week.

At home each day is a jacket day or a sweater day, taking turns across home days, and the pants row supplies the garment: the blue pants' jacket is brown, the tan and black pants share one black jacket. The turn is spent whatever the weather, so cold, mild, cold gives jacket, nothing, jacket — the mild day took the sweater's turn. Office days don't take a turn, and home has no rule against wearing the same thing twice in a week. When the turn has fallen out of step with what you actually wore, `reset-outerwear` moves it on by one from today; typed on an office day it lands on the next home day. It takes no `--on`: the turn is only ever put right from where you stand.

Forecasts are daily highs from [Open-Meteo](https://open-meteo.com), which needs no API key, for the coordinates in `wardrobe.py`. It covers the next sixteen days. Only the forecast endpoint is ever called — no historical archive — so a past date hedges the same way.

## Interface

A deliberately disposable CLI, to be replaced later by something usable from a phone.

```
what2wear                            # today's outfit
what2wear --on 2026-08-24            # any other date, past or future
what2wear stay-home                  # this office day is now a home day
what2wear go-in                      # this home day is now an office day
what2wear reset lblue                # move the rotation to that shirt, today
what2wear reset lblue --on 2026-09-07  # --on goes after the command, and defaults to today
what2wear reset-outerwear            # home jacket days become sweater days, and back
what2wear show-closet                # every garment, how to name it, and what's due
what2wear replace office.sweater.beige oatmeal   # this one is called that now
what2wear swap office white striped  # two shirts sharing pants trade labels
```

Holidays and leave aren't separate concepts — they're just `stay-home` on the relevant date.

A garment is named by a dotted string — `office.shirt.white`, `home.shoes.black`, `pants.blue` — because a label alone is unique only within a closet and a kind. Pants are named without a closet: there is one set of trousers and both closets wear it, so replacing them changes both. `show-closet` prints those names so one can be copied rather than guessed at, and shows each shirt's pants in its own column so the legal swaps are the ones sharing that column. It marks with `>` the shirt each rotation is due to give you — today's in the closet today draws from, and in the other the one waiting on its next day — so the label to type into `reset` is read off rather than counted out.

`replace` covers a worn-out garment and a mislabeled one alike — no garment's history is kept, so they are the same event. Nothing is keyed by a label, so neither a replace nor a swap can move a rotation.

## The wardrobe is given

There is no configuration. Both closets, the pants they share, the office weekday pattern, the cold threshold, the forecast coordinates, and the labels and anchors a fresh install starts from all live in [`src/what2wear/wardrobe.py`](src/what2wear/wardrobe.py), because the rules only mean anything against this wardrobe's shape — office sweaters one-to-one with office shoes, a fallback that is always another row's sweater, closet sizes coprime with the office and home days in a week. A stranger's closet satisfying a schema and none of that would produce confident nonsense, and no amount of validation would catch it. See [ADR-0005](docs/adr/0005-what2wear-dresses-one-person-from-a-given-wardrobe.md).

So there is nothing to write, nothing to copy and no first run. The properties the rules lean on — those pairings, those sizes — are asserted once by `tests/test_wardrobe.py`.

An anchor is a date and the position a rotation stood at on it — a position rather than a shirt name, so that renaming a garment can never move a rotation. With nothing yet recorded the anchor is *today* at position 0, so a fresh install opens on `white` in whichever closet the day calls for; the first thing you record pins it, and from then on it stands still.

A pants row's `fallback` is the sweater to take when the row's own is already worn that week. It is always another row's own, which is what lets the fallback bring that row's shoes along with it.

Every string in `wardrobe.py` names a garment rather than stating what it is called: it is the label that garment shipped with. The state says what each is called now, keyed by where the garment hangs — `office.shirt.0`, `pants.1` — so no key is spelled with a label and a `replace` changes a value only.

## The state is one file the tool owns

Everything it's been told — what every garment is called, the three anchors (one per shirt rotation, one for home outerwear) and the day type overrides — lives in `state.json` in your platform's user config directory (`~/Library/Application Support/what2wear` on macOS, `~/.config/what2wear` on Linux). Nobody authors it and there is nothing in it to edit; it is readable if you open it, but you are not expected to. There is no flag, environment variable or working-directory fallback to point it elsewhere: where it lives is a property of the installation, not of an invocation. The directory arrives with the first record; until then an installation has no files at all.

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

The architecture is a functional core with an imperative shell, and the core has two pure seams. One answers and never changes anything — `answer` for a whole outfit, `get_due_shirt` for where one rotation stands:

```
answer(state, on, weather)         -> Response
get_due_shirt(state, day_type, on) -> str
```

`weather` maps each date the forecast reaches to its high, so the core never touches the network: the shell fetches and the core decides.

The other records and never renders anything — one function per thing that can be recorded:

```
record_override(state, on, day_type) -> State
reset(state, shirt, on)              -> State
reset_outerwear(state, today)        -> State
replace_(state, garment, label)      -> State
swap(state, closet, first, second)   -> State
```

That is five functions rather than a single `apply` over a union of command objects, because nothing here queues, logs or replays a command — there was nothing for a command object to be. The shell picks one of them for what was typed and calls it (`_choose_update_function(args)(state)`), so trading the CLI for another interface trades the parser, the chooser and the renderers, and moves nothing in core. See [ADR-0009](docs/adr/0009-the-recording-seam-is-four-functions-not-a-command-union.md).

The shell composes the two seams, so a command that records shows its result for free. It only reads and writes the state file, reads the clock, fetches the forecast and prints. Those two seams are the whole test surface — no mocks, no files touched, no clock reads outside the shell's own tests. The wardrobe under test is the given one, so there is no fixture that can drift from what ships.

Read [`CONTEXT.md`](CONTEXT.md) before touching anything, then the ADRs for the area you're working in.

Built with uv, ruff, ty and pytest. No dataframe library — the data is a few dozen records.
