# what2wear

Tells you what to wear today, and what you'll wear on any future day.

It walks a fixed, hand-authored list of shirts — one closet for the office, one for home — advancing each rotation only on days of its own kind. Pants come welded to the shirt; shoes and sweaters follow from the pants. At the office it guarantees no sweater and no pair of shoes repeats within a Monday-start week. At home, when it's cold, it alternates jacket and sweater so the same kind of layer never comes twice running.

> **Status: complete outfits.** Tickets 01 and 02 are in: rotation for any date, config parsing, the CLI, and resolution — sweaters and shoes keyed by pants, with the office week fallback. `what2wear` and `what2wear --on <date>` give you the shirt, its pants, its sweater, its shoes and whether it's an office day. Overrides, resets, layers and weather are still ahead.

## How it works

**Rotation picks the shirt. Resolution decides everything else.** Those are deliberately separate steps, and the glossary keeps them apart.

The rotation position for any date is *derived* from the calendar rather than stored as a cursor:

```
position(date) = (days_of_that_type_since_anchor + reset_offsets_before(date)) mod len(closet)
```

That one choice shapes the whole design. Looking ahead to a future date is the same function call as looking at today, not a separate simulation that can drift. The rotation also stays correct whether or not you run the tool on a given day — you wore clothes either way. See [ADR-0001](docs/adr/0001-positions-derived-from-the-calendar.md).

Resolution keys off **pants, not shirts** — each closet carries one pants row per colour, holding the sweater, shoes and jacket that follow from it. This is also why fallbacks exist at all: an office sweater collision is precisely two shirts in the same week sharing pants. See [ADR-0003](docs/adr/0003-garments-are-keyed-by-pants-not-by-shirt.md).

The one exception to deriving everything is the home layer alternation, which needs a stored cursor because past weather isn't reconstructable the way the calendar is. That's deliberate and documented in [ADR-0002](docs/adr/0002-home-layer-alternation-is-a-stored-cursor.md) — it is not an inconsistency waiting to be cleaned up.

## Planned interface

A deliberately disposable CLI, to be replaced later by something usable from a phone. The first two work today; the rest arrive with their tickets:

```
what2wear                      # today's outfit
what2wear --on 2026-08-24      # any date, past or future
what2wear --stay-home [date]   # this office day is now a home day
what2wear --go-in [date]       # this home day is now an office day
what2wear --reset [shirt]      # skip to the next shirt, or jump to a named one
```

Holidays and leave aren't separate concepts — they're just `--stay-home` on the relevant date.

## Configuration

Closets, the office weekday pattern, the anchor dates and the temperature threshold live in a hand-authored YAML file that the tool never rewrites. Recorded decisions — day type overrides, resets, and resolved home layers — go to append-only logs the tool owns, kept separate so recording one can never corrupt your closet.

Each closet carries its shirts, its three pants rows and its own anchor, and the anchor is expressed the way you'd actually say it:

```yaml
office_weekdays: [mon, wed, fri]

office:
  anchor: { date: 2026-08-17, shirt: dblue }
  shirts:
    - { name: dblue, pants: tan }
    # ...
  pants:
    tan: { sweater: black, shoes: black, fallback: grey }
    # ...

home:
  anchor: { date: 2026-08-15, shirt: lgreen }
  shirts:
    - { name: white, pants: blue }
    # ...
  pants:
    blue: { sweater: yellow, jacket: brown, shoes: black }
    # ...
```

Re-anchoring is just "today I'm wearing X".

A `fallback` is the sweater to take when the primary is already worn that week. It's always another row's primary — the config refuses one that isn't — which is what lets the fallback bring that row's shoes along with it.

The tool reads `what2wear.yaml` in the working directory. Set `WHAT2WEAR_CONFIG` to keep it elsewhere, or pass `--config`.

## Layout

```
CONTEXT.md                  glossary — authoritative for naming
docs/adr/                   architecture decisions
docs/agents/                conventions for agent workflows
.scratch/outfit-rotation/   spec and implementation tickets
src/what2wear/              the package
```

## Design

The architecture is a functional core with an imperative shell. All domain logic sits behind a single pure entry point taking parsed state, a date and a weather mapping; the shell only reads files, reads the clock, fetches the forecast, prints and appends. That one seam is the whole test surface — no mocks, no fixtures on disk, no clock reads in tests.

Read [`CONTEXT.md`](CONTEXT.md) before touching anything, then the ADRs for the area you're working in.

Built with uv, ruff, pytest and pydantic. No dataframe library — the data is a few dozen records.
