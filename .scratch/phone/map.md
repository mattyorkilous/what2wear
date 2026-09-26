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

## Not yet specified

- How each command becomes UI: which are screens, which are forms
  (`replace`, `swap`, `set-office-weekdays`), and whether `show-closet`
  is the home screen.
- Moving the existing `state.json` to wherever the State lives next.
- What becomes of `cli.py` and its tests once the phone replaces it.
- How the phone behaves offline or when its data is stale, especially
  the widget's timeline.

## Out of scope

- Keeping the Mac CLI alive alongside the phone. That needs two
  writers and sync, and belongs to a later effort if it's wanted.
