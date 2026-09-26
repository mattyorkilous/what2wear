# 03 — Widgets and apps without a native build

Type: research
Status: resolved
Blocked by: none

## Question

Without writing a native app, what can show the day's Outfit on the
iPhone home screen or Today view, and what can offer every CLI command?

- Can a Scriptable widget fetch JSON from a URL and render emoji text,
  and how often does it refresh?
- Can Apple Shortcuts widgets do the same?
- Can a home-screen web app (PWA) on iOS cover the full command set,
  and does it have any widget story?
- Does Pythonista or a-Shell run Python on the phone well enough to
  host the core locally, and can either drive a widget?

Research: research/03-widgets-without-a-native-app.md

## Answer

Nothing without a native build covers both the widget and every
command. The best pairing is a home-screen web app plus a Scriptable
widget. Detail, sources and a comparison of the three paths for
"Choose the approach" are in `research/03-widgets-without-a-native-app.md`.

- **Scriptable:** free. It fetches JSON (with a token header) and shows
  emoji text on the Home Screen and Lock Screen. iOS decides when it
  refreshes, roughly every 15–60 minutes, so it can show yesterday's
  Outfit for up to an hour after midnight. It was last updated in
  September 2024.
- **Shortcuts widgets** are only buttons that run shortcuts; they can't
  display an Outfit. Still useful as glue, e.g. a morning automation.
- **Home-screen web app:** free and can offer every command, but iOS
  gives web apps no widgets. The core runs in the page unchanged under
  Pyodide (Python 3.14.2, and `holidays` installs). The page fetches
  Open-Meteo itself (Open-Meteo allows it) and passes the forecast to
  `answer`. Home-screen web apps aren't hit by Safari's 7-day data
  deletion. But Scriptable can't read the web app's data, so the
  widget would still need something hosted.
- **Pythonista:** ruled out. $9.99, Python 3.10, and its widget used the
  Today view that iOS 18 removed.
- **a-Shell:** free, Python 3.13. All 342 tests pass on 3.13 with a
  small backport: parenthesise the `except` in `forecast.py` and add
  `from __future__ import annotations` to each module (tested outside
  the repo). No widget of its own, but a morning Shortcuts automation
  could run it and write today's Outfit to iCloud Drive for a
  Scriptable widget, with no hosting. Whether that automation runs
  while the phone is locked is unconfirmed.
