# what2wear

Tells you what to wear today, and what you'll wear on any other day.

It walks a fixed list of shirts — one closet for the office, one for home — advancing each rotation only on days of its own kind. Pants come welded to the shirt; shoes and sweaters follow from the pants. At the office it guarantees no sweater and no pair of shoes repeats within a Monday-start week. When it's cold you wear the outerwear your pants call for — at the office their sweater, at home their sweater or their jacket, whichever kind the day's turn says.

> **Status: on the phone.** A small web app on PythonAnywhere is the one interface, with a Scriptable widget beside it. The Day page gives you the shirt, its pants, its shoes, whether it's an office day, and whether the forecast calls for its sweater or jacket, for today or any date you pick; a past date answers too, with a note that it says where the rotation stands now rather than what was worn. From the Day page you switch a date between office and home, wear a different shirt, or move the home outerwear rotation on by one. The Closet page lists every garment with when each shirt is next due, swaps two shirts that share pants, and replaces a garment's label and color. The Settings page sets which three weekdays you go in and how cold is cold. Everything it's been told lives in one state file it owns.

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

Below the cold threshold — 50°F until you say otherwise on the Settings page — you wear outerwear; at or above it, none, and the Day page shows no outerwear. The forecast decides only *whether*: which garment a date calls for is worked out without it, so a date too far out for the forecast still names one:

```
  Beige Sweater                  # cold: wear it
                                 # warm: no outerwear
  Beige Sweater, if it's cold    # no forecast for that date yet
```

The last is also what you get when the forecast can't be fetched at all. A network problem never stops the tool answering — it just can't say yet whether you'll want it.

At the office it is always a sweater — the one your pants call for, or the week's fallback when that one is taken. A warm Monday still spends its sweater for the week.

At home each day is a jacket day or a sweater day, taking turns across home days, and the pants row supplies the garment: the blue pants' jacket is brown, the tan and black pants share one black jacket. The turn is spent whatever the weather, so cold, mild, cold gives jacket, nothing, jacket — the mild day took the sweater's turn. Office days don't take a turn, and home has no rule against wearing the same thing twice in a week. When the turn has fallen out of step with what you actually wore, "Switch to the …" on today's Day page moves it on by one from today. Only today's page offers it, and only on a home day not known to be warm: the turn is only ever put right from where you stand, when you're about to wear it.

Forecasts are daily highs from [Open-Meteo](https://open-meteo.com), which needs no API key, for the coordinates in `wardrobe.py`. It covers the next sixteen days. Only the forecast endpoint is ever called — no historical archive — so a past date hedges the same way.

## Interface

Three pages, linked from the top of each: Day, Closet and Settings.

- **Day** — one date's outfit, today unless you've picked another with the date box or ‹ prev / next ›. "Make this a Home Day" (or Office Day) switches that date's side; the shirt list moves the rotation to the shirt you'd rather wear that day; on today's page, at home, "Switch to the …" moves the home outerwear rotation on by one.
- **Closet** — each closet grouped by pants, every shirt with the date it's next due. Two shirts on the same pants can swap places. Tap any garment to replace it: a new label and color, with an optional stripe color.
- **Settings** — the three office weekdays and the cold threshold.

US federal holidays, on their observed dates, and the Friday after Thanksgiving are home days without your saying so — a Saturday July 4 makes Friday one, a Sunday holiday makes Monday one. Making the holiday an office day on its Day page is also how to say your employer doesn't give you one. Leave is just making the date a home day. See [ADR-0011](docs/adr/0011-holidays-are-given-home-days.md).

Office weekdays must be exactly three different days, weekends included. Only *which* three is yours to say: *how many* is a change to the source, because the closet sizes only stay varied against three office days and four home days a week, and three office sweaters cannot keep a fourth day from repeating. See [ADR-0007](docs/adr/0007-office-weekdays-and-the-cold-threshold-are-told.md). Changing them would reclassify the past, and every rotation counts days of its kind since its anchor, so saving them moves all three anchors to today at the positions they held there first: no rotation jumps, and it says so. Overrides you've already recorded stay as they were, and a date can still be made a fourth office day in a week — with the repeat it can't avoid called out. A change mid-week does re-walk that week's earlier office days under the new pattern, so the week's fallback sweater can come out differently; that is accepted rather than stored around. The cold threshold moves nothing: it decides only whether outerwear is worn, never which.

A replace covers a worn-out garment and a mislabeled one alike — no garment's history is kept, so they are the same event. Pants belong to no closet: there is one set of Pants and both closets wear it, so replacing them changes both. Nothing is keyed by a label, so neither a replace nor a swap can move a rotation.

## On the phone

A small Flask app, `what2wear.web`, serves its pages from PythonAnywhere's free plan. Every URL starts with a secret token, so the bookmarked URL is the login; anything else is a plain 404. `/` is today in New York, `/day/YYYY-MM-DD` any other date.

To deploy, in a PythonAnywhere bash console:

```
git clone <this repo> what2wear && cd what2wear
pip install --user uv
uv sync --frozen --no-dev --python python3.13
```

Add a manual web app on Python 3.13, set its virtualenv to `~/what2wear/.venv`, and make its WSGI file:

```python
from pathlib import Path
from what2wear import web

application = web.app(Path.home() / "state.json", "<a long random token>")
```

Reload, open `https://<user>.pythonanywhere.com/<token>/` in Safari on the phone, and Share → Add to Home Screen.

To deploy a change, in a bash console:

```
cd ~/what2wear && git pull
uv sync --frozen --no-dev
```

then Reload on the Web tab.

The free plan stops the web app unless you renew it, so once a month click "renew" on the Web tab, and while you're there download `~/state.json` from the Files tab as the backup — it is the only live copy, and the most a lost month costs is a month of what you've told it. To restore, upload the backup in the Files tab over `~/state.json`. Then check today's Day page shows the shirt you expect: a file in the wrong place doesn't fail, it quietly starts a fresh state.

For the widget, install [Scriptable](https://scriptable.app) from the App Store, add a script, paste in [`widget.js`](widget.js), and set `HOST` and `TOKEN` at its top. Run it once in the app to see the tile. Then long-press the Home Screen, tap Edit → Add Widget, choose Scriptable's small widget, and long-press it → Edit Widget to pick the script. It shows today's Outfit on the phone's own date and opens the Day page when tapped. When it can't fetch it keeps the last good Outfit, with ⚠︎ on the date if that isn't today's; "⚠︎ State won't read" means open the Day page, and "⚠︎ Renew PythonAnywhere?" means the web app has lapsed or the token is wrong.

## The wardrobe is given

There is no configuration. Both closets, the pants they share, the forecast coordinates, and the starting values the state overlays — the labels, the anchors, the office weekdays and the cold threshold a fresh install starts from — all live in [`src/what2wear/wardrobe.py`](src/what2wear/wardrobe.py), because the rules only mean anything against this wardrobe's shape — office sweaters one-to-one with office shoes, a fallback that is always another row's sweater, closet sizes coprime with the office and home days in a week. A stranger's closet satisfying a schema and none of that would produce confident nonsense, and no amount of validation would catch it. See [ADR-0005](docs/adr/0005-what2wear-dresses-one-person-from-a-given-wardrobe.md).

So there is nothing to write, nothing to copy and no first run. The properties the rules lean on — those pairings, those sizes — are asserted once by `tests/test_wardrobe.py`.

An anchor is a date and the position a rotation stood at on it — a position rather than a shirt name, so that renaming a garment can never move a rotation. With nothing yet recorded the anchor is *today* at position 0, so a fresh install opens on `white` in whichever closet the day calls for; the first thing you record pins it, and from then on it stands still.

A pants row's `fallback` is the sweater to take when the row's own is already worn that week. It is always another row's own, which is what lets the fallback bring that row's shoes along with it.

Every string in `wardrobe.py` names a garment rather than stating what it is called: it is the label that garment shipped with. The state says what each is called now, keyed by where the garment hangs — `office.shirt.0`, `pants.1` — so no key is spelled with a label and a `replace` changes a value only.

## The state is one file the tool owns

Everything it's been told — what every garment is called, the three anchors (one per shirt rotation, one for home outerwear), the day type overrides, the office weekdays and the cold threshold — lives in the `state.json` the WSGI file hands `web.app`. Nobody authors it and there is nothing in it to edit; it is readable if you open it, but you are not expected to. The web app is its one writer. The file arrives with the first record; until then an installation has no state file at all.

It is rewritten whole rather than appended to, so it is written to a temporary file beside it and moved into place atomically — a recording that fails partway leaves the previous state intact. See [ADR-0006](docs/adr/0006-the-wardrobe-is-source-the-state-is-one-file-the-tool-owns.md).

## Layout

```
CONTEXT.md                  glossary — authoritative for naming
docs/adr/                   architecture decisions
docs/agents/                conventions for agent workflows
.scratch/                   specs and implementation tickets
src/what2wear/              the package
src/what2wear/wardrobe.py   the given wardrobe, and the starting values the state overlays
widget.js                   the Scriptable widget, pasted onto the phone
```

## Design

The architecture is a functional core with an imperative shell, and the core has two pure seams. One answers and never changes anything — `answer` for a whole outfit, `get_due_shirt` for where one rotation stands, `get_due_date` for the same rotation read backwards:

```
answer(state, on, weather)                       -> Response
get_due_shirt(state, day_type, on)               -> str
get_due_date(state, day_type, shirt, today)      -> date | None
```

`weather` maps each date the forecast reaches to its high, so the core never touches the network: the shell fetches and the core decides.

The other records and never renders anything — one function per thing that can be recorded:

```
record_override(state, on, day_type) -> State
reset(state, shirt, on)              -> State
reset_outerwear(state, today)        -> State
replace_(state, garment, label, color, stripe_color) -> State
swap(state, closet, first, second)   -> State
set_office_weekdays(state, weekdays, today) -> State
set_cold_threshold(state, threshold) -> State
```

That is seven functions rather than a single `apply` over a union of command objects, because nothing here queues, logs or replays a command — there was nothing for a command object to be. Each form the web shell serves posts to its own route, and that route calls one of them, so trading the CLI for the web shell traded the parser and the renderers and moved nothing in core. See [ADR-0009](docs/adr/0009-the-recording-seam-is-four-functions-not-a-command-union.md).

The shell composes the two seams, so a form that records shows its result for free. It only reads and writes the state file, reads the clock, fetches the forecast and renders pages. Those two seams are the whole test surface — no mocks, no files touched, no clock reads outside the shell's own tests. The wardrobe under test is the given one, so there is no fixture that can drift from what ships.

Read [`CONTEXT.md`](CONTEXT.md) before touching anything, then the ADRs for the area you're working in.

Built with uv, ruff, ty and pytest. No dataframe library — the data is a few dozen records.
