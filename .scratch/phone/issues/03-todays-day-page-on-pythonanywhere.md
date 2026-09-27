# 03 — Today's Day page on PythonAnywhere

**What to build:** The tracer bullet. A Flask web shell, deployed to
PythonAnywhere free, that shows any date's Outfit as text on a Day
page reached through a secret token in the URL. The wearer opens the
bookmark on the phone and sees today's Outfit. Icons come later; each
garment reads as its Label and kind. See `.scratch/phone/spec.md`.

**Blocked by:** 01 — Outfits carry Garments with a told Color.

**Status:** ready-for-agent (the deploy steps are HITL)

- [ ] Core runs on 3.13: `requires-python = ">=3.13"`,
      `.python-version` 3.13, the `except` in `forecast` parenthesised
- [ ] Flask is a dependency; `web.app(state_path, token, fetch_weather)`
      builds the app, and tests pass a temp path and a weather stub
- [ ] The token is the first path segment, checked once with
      `hmac.compare_digest`; a wrong one is a plain 404
- [ ] `TIMEZONE = ZoneInfo("America/New_York")` in `wardrobe`; `/` is
      today there, `/day/YYYY-MM-DD` any date
- [ ] The Day page shows Office/Home Day, the Outfit, ‹ prev / next ›
      by one calendar day, a GET date picker, and nav to Day, Closet
      and Settings
- [ ] The past-date note, the unavoidable-repeat note, and the
      ", if it's cold" hedge while the forecast is unknown
- [ ] Every response is `Cache-Control: no-store`
- [ ] An unreadable State is a 500 page with the message and the nav
- [ ] A fresh install answers and writes nothing
- [ ] Tested through Flask's `test_client()`
- [ ] Deployed: git clone, `uv sync --frozen --no-dev --python
      python3.13`, WSGI file calling `web.app(...)`; the page opens on
      the phone and is saved to the Home Screen
