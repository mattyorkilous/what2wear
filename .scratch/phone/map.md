# Phone — wayfinder map

Label: wayfinder:map

## Destination

A handoff spec at `.scratch/phone/spec.md` for the interface that
replaces the CLI: every current command usable from an iPhone, ideally
with a widget showing the day's Outfit as emoji. It names the approach,
where the State lives, and what the phone shows.

## Notes

- Domain: `CONTEXT.md` is authoritative for naming; ADR-0009 says
  swapping the interface trades the parser, chooser and renderers and
  moves nothing in core.
- Standing constraints, settled while charting:
  - **The phone replaces the CLI.** There is one writer of the State,
    so no two-device sync.
  - **The phone works without the Mac** being on or reachable.
  - **$0.** No Apple Developer Program. Re-signing a free-provisioned
    app every 7 days is acceptable.
  - **The widget is preferred, not required.** It counts in an
    approach's favour but can't veto one.
  - **Keep the core in Python** if at all possible; a Swift port of the
    core is the thing to avoid.
  - **If the State is hosted, one secret token is enough.** The data is
    low-sensitivity.
- Consult `/grilling` and `/domain-modeling` on grilling tickets and
  `/prototype` on prototype tickets.

## Decisions so far

- [Free hosting for the Python core](issues/02-free-python-hosting.md) — PythonAnywhere free fits nearly unchanged (3.13 means one `except` line needs parentheses; renew every month); next best is Cloudflare Python Workers with a Durable Object for the State
- [Python on iOS, free-signed](issues/01-python-on-ios.md) — works: a SwiftUI app embeds CPython 3.14 via BeeWare, the widget reads JSON the app precomputes, and re-signing is weekly via Xcode or SideStore
- [Widgets and apps without a native build](issues/03-widgets-without-a-native-app.md) — no single tool does both; best is a web app (Pyodide can run the core in the page) plus a Scriptable widget, which needs a hosted State or an a-Shell + iCloud Drive relay; Pythonista is ruled out
- [Choose the approach](issues/05-choose-the-approach.md) — a hosted core on PythonAnywhere free: the State file lives on its disk behind one token, the phone gets Python-rendered HTML pages, a Scriptable widget reads JSON from the same server, and the core holds to Python 3.13
- [What an emoji Outfit looks like](issues/04-emoji-outfit.md) — a small widget: 🏢/🏠 and a short date, then drawn icons in each Garment's real colour with its full name ("Light Blue Shirt"); Outerwear worn only if it's cold is dimmed
- [Pages and forms for each command](issues/06-pages-and-forms.md) — three pages (Day at `/`, Closet, Settings); dates in the URL with prev/next and a date picker; writes POST-redirect with a notice; `when` folds into the Closet, the show commands into their set forms
- [What becomes of the CLI](issues/07-what-becomes-of-the-cli.md) — deleted with its tests, script entry and `platformdirs`, as the last step once the State is hosted; the web shell owns the confirmation strings; the shell behaviours worth keeping become the web shell's test checklist
- [The web shell on PythonAnywhere](issues/08-the-web-shell.md) — Flask in `web.py`; the token is the first URL segment (no login); today is America/New_York from `wardrobe.py`; notices ride `?notice=`; the widget reads `/<token>/day/YYYY-MM-DD.json`; deployed by git clone + `uv sync`
- [Drawing the garment icons on the phone](issues/09-drawing-the-icons.md) — the Scriptable widget draws them with `DrawContext` from path strings in the JSON (shape, optional pattern, detail), the same data the Day page's SVG uses; stripes are vertical bars inside the torso, dashes become segments
- [Full names and colours for Labels](issues/10-full-names-and-colours.md) — the Label becomes the full name as typed ("Light Blue"); each Garment gains a told Color (and optional stripe Color) in the State, set by Replace's color picker and carried by Swap; old Labels convert once at the move

## Not yet specified

Nothing right now: both patches became tickets, [Moving and backing up the State](issues/11-moving-and-backing-up-the-state.md) and [When the widget can't fetch](issues/12-when-the-widget-cant-fetch.md).

## Out of scope

- Keeping the Mac CLI alive alongside the phone. That needs two
  writers and sync, and belongs to a later effort if it's wanted.
