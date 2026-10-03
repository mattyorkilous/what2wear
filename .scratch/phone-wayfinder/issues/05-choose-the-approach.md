# 05 — Choose the approach

Type: grilling
Status: resolved
Blocked by: 01, 02, 03

## Question

Which approach gets what2wear onto the phone, within the map's
constraints?

Candidates:
- a free-signed SwiftUI app embedding Python
- a SwiftUI app over a hosted core
- Scriptable or a PWA over a hosted core
- Python on the phone

The answer also settles where the State lives.

## Answer

**A hosted core: PythonAnywhere free, serving Python-rendered HTML to
the phone, with a Scriptable widget.** Settled by grilling on
2026-09-26.

- **Where the State lives:** the existing State file, on
  PythonAnywhere's disk. The server is its only writer, and one secret
  token guards it. ADR-0006 stands unchanged.
- **Commands:** plain HTML pages and forms the server renders, saved to
  the Home Screen. No JS and no Pyodide. A Shortcuts front end can be
  added later against the same server; it isn't part of this effort.
- **Widget:** a Scriptable widget that fetches a JSON endpoint on the
  same server using the token. It looks like a native widget. The
  accepted costs: text only, no buttons, it refreshes on iOS's schedule
  (so it can show yesterday's Outfit for up to an hour after midnight),
  and Scriptable was last updated in September 2024.
- **Python 3.13:** the core stays runnable on 3.13 because
  PythonAnywhere tops out there. That means parenthesising the `except`
  in `forecast.py` and setting `requires-python = ">=3.13"`. Raise the
  pin again once PythonAnywhere offers 3.14.
- **Network:** accepted. With no signal there's no what2wear, the same
  as the forecast today.
- **Chore:** click "renew" on PythonAnywhere once a month.

Why the other routes lost:
- **Native SwiftUI + embedded Python:** it means Swift UI code. The user
  prefers all Python, and a Scriptable widget is good enough. The
  weekly Xcode re-sign was not an objection.
- **Pyodide web app:** its UI is JS glue, and the widget would still
  need something hosted, so the data would live in two places.
- **a-Shell:** a terminal UI, a background run nobody has confirmed,
  and it still needs the 3.13 backport.
- **Cloudflare Workers:** the fallback if PythonAnywhere free goes
  away. It rewrites the State I/O and `urllib`.
