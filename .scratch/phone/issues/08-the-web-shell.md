# 08 — The web shell on PythonAnywhere

Type: grilling
Status: resolved
Blocked by: none

## Question

What is the server that wraps the core on PythonAnywhere?

- A framework (Flask, Bottle), or bare WSGI from the stdlib
- How the one secret token travels: a cookie set once, a URL segment,
  or a header (Scriptable can send headers; a Home Screen bookmark
  can't)
- The shape of the JSON endpoint the widget reads
- How the post-redirect notice line (see
  [Pages and forms for each command](06-pages-and-forms.md)) reaches
  the page it redirects to: a query parameter or a cookie

## Answer

**A Flask app in `web.py`, with the token as the first path segment.**
Settled by grilling on 2026-09-27.

- **Framework:** Flask with Jinja templates in
  `src/what2wear/templates/` (a base layout with the nav and notice,
  then Day, Closet and Settings). It beats stdlib WSGI on simplicity:
  routing, `request.form`, `redirect`, autoescaped Labels, and
  `test_client()` for the web shell's test checklist.
- **Token:** the first path segment of every URL,
  `https://<user>.pythonanywhere.com/<token>/day/…`. The Home Screen
  bookmark and the widget both carry it. There's no login and no
  cookie. It's checked once, in a `url_value_preprocessor`, with
  `hmac.compare_digest`, and a wrong token is a plain 404. The token
  will show up in history, screenshots and the access log. That's
  accepted: whoever holds the URL can read and write, which is fine for
  this data.
- **Configuration:** an app factory,
  `web.app(state_path=…, token=…)`, called from PythonAnywhere's WSGI
  file. The secret stays out of git, and tests point it at a temp
  file.
- **Today:** `TIMEZONE = ZoneInfo("America/New_York")` in `wardrobe.py`,
  next to `LATITUDE`/`LONGITUDE`. Every "today" in the web shell (`/`,
  the today-only `reset-outerwear`) comes from it, not the server's UTC
  clock.
- **Notice:** writes answer with a `303` to the originating page with
  `?notice=<text>`. It reappears on reload, which is harmless. The
  bookmark is `/`, so it never carries one.
- **Widget JSON:** `GET /<token>/day/YYYY-MM-DD.json`. The widget
  sends the phone's own date. Domain fields only:

  ```json
  {"date": "2026-09-28", "day": "office",
   "outfit": [{"garment": "shirt", "label": "lblue"},
              {"garment": "pants", "label": "khaki"},
              {"garment": "outerwear", "label": "jacket", "if_cold": true}]}
  ```

  Presentation fields (full names, colours, icons) are added by
  [Drawing the garment icons on the phone](09-drawing-the-icons.md) and
  [Full names and colours for Labels](10-full-names-and-colours.md).
- **Caching:** `Cache-Control: no-store` on every response, so a
  resumed Home Screen app never shows a stale Outfit.
- **Failures:** an unreadable State (`What2wearError`) gets a 500 page
  with the message and the nav, or `{"error": "…"}` with a 500 on the
  JSON endpoint. A failed forecast is not an error. It shows the
  outerwear with the ", if it's cold" hedge on the page, and
  `"if_cold": true` in the JSON, as the CLI does today.
- **Deploy:** `git clone` the GitHub repo in PythonAnywhere's bash
  console, `pip install --user uv`, then
  `uv sync --frozen --no-dev --python python3.13` to build `.venv`,
  which the web app's virtualenv setting points at. An update is
  `git pull`, `uv sync`, then Reload. `.python-version` becomes `3.13`
  along with `requires-python`.
