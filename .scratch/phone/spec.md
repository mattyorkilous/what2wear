# Phone

Status: ready-for-agent

Charted by [the phone wayfinder map](../phone-wayfinder/map.md); every decision here is
detailed in one of its tickets. Governed by ADR-0005, ADR-0006,
ADR-0008 and ADR-0009. Adds an ADR, "Garments carry a told Color".

## Problem Statement

what2wear lives in a terminal on the Mac. The wearer decides what to
put on in the morning, away from the Mac, often before it's even
open. To find out today's Outfit, or to tell the tool they're staying
home, they have to get to the Mac and type a command. The answer they
get back is a bare Label like `lblue`, which reads worse than a name.
There's no way to glance at the day's Outfit, and nothing works from
the phone that's always in their pocket.

## Solution

The CLI is replaced by a small web app on PythonAnywhere's free plan,
used from an iPhone:

- The State file moves onto PythonAnywhere's disk. The web app is its
  only writer, and a secret token in the URL guards it.
- Three plain HTML pages, saved to the Home Screen, cover every
  command. **Day** shows one date's Outfit and the actions for that
  date. **Closet** shows both Closets and handles Replace, Swap and
  "when is this Shirt next due". **Settings** holds the Office
  Weekdays and the Cold Threshold.
- A Scriptable widget on the Home Screen shows today's Outfit as drawn
  garment icons, each in its Garment's real Color, with full names
  ("Light Blue Shirt").
- Labels become full names as typed ("Light Blue"). Each Garment
  gains a told Color, and an optional stripe Color, which Replace sets
  and Swap carries.
- The CLI, its tests and `platformdirs` are deleted once the State has
  moved.

It costs $0. The one chore is clicking "renew" on PythonAnywhere once
a month and downloading `state.json` as a backup at the same time.

## User Stories

### Day page

1. As the wearer, I want the Home Screen bookmark to open today's
   Outfit, so that I see what to wear with one tap.
2. As the wearer, I want "today" to be today in New York, not the
   server's UTC date, so that the page doesn't jump to tomorrow at 8 pm.
3. As the wearer, I want the Day page to say whether it's an Office Day
   or a Home Day, so that I know which Closet I'm dressing from.
4. As the wearer, I want each Garment drawn as an icon in its Color
   with its full name ("Light Blue Shirt"), so that I recognise it at a
   glance.
5. As the wearer, I want a striped Shirt drawn with vertical stripes in
   its stripe Color, so that it's told apart from a plain one.
6. As the wearer, I want a sweater and a jacket drawn differently, so
   that I reach for the right Outerwear.
7. As the wearer, I want Outerwear shown plainly when it's cold,
   omitted when it's warm, and marked ", if it's cold" when the
   forecast is unknown, so that a failed forecast still dresses me.
8. As the wearer, I want ‹ prev and next › links, so that I can step
   one calendar day at a time.
9. As the wearer, I want a native date picker, so that I can jump to
   any date.
10. As the wearer, I want every Day page to have its own URL, so that
    the back button and bookmarks work.
11. As the wearer, I want a past date to say that it shows where the
    Rotation stands now, not what was worn, so that I don't read it as
    history.
12. As the wearer, I want the Day page to say when a sweater repeats
    within the Week because it can't be avoided, so that the repeat
    isn't a surprise.
13. As the wearer, I want one button, "Make this a Home Day" or "Make
    this an Office Day" (whichever the date isn't), so that I can
    record a Day Type Override in one tap.
14. As the wearer, I want "Wear a different shirt" with a list of that
    date's Closet's Shirts, so that I can Reset the Rotation to the
    Shirt I want.
15. As the wearer, I want "Switch to the jacket" or "Switch to the
    sweater" on today's page when today is a Home Day, so that I can
    put the Home Outerwear Rotation back in step with what I wore.
16. As the wearer, I want no confirm steps, so that each action takes
    one tap. I can undo it from the same page.
17. As the wearer, I want a nav to Day, Closet and Settings on every
    page, so that I can always get anywhere.

### Closet page

18. As the wearer, I want both Closets on one page, grouped by Pants
    Row, so that I can see the whole Wardrobe.
19. As the wearer, I want each Shirt to show the next date it's due,
    linked to that Day page, so that I can answer "when do I wear
    this" without a command.
20. As the wearer, I want to tap a Garment and get a form pre-filled
    with its Label and Color, so that I can Replace it.
21. As the wearer, I want a "Striped" checkbox with a second color
    input, so that I can give a Garment a stripe Color.
22. As the wearer, I want the stripe color ignored when "Striped" is
    unchecked, so that a leftover value does nothing.
23. As the wearer, I want a Label with a `.` in it refused with a
    message, so that every Garment stays addressable.
24. As the wearer, I want a Label already used by another Garment of
    the same kind in that Closet refused with a message, so that one
    name means one Garment.
25. As the wearer, I want a "Swap with…" list on each Shirt showing
    only the Shirts that share its Pants, so that I'm never offered a
    Swap that would be refused.
26. As the wearer, I want a Swap to exchange Colors along with Labels,
    so that a Label and its Color always travel together.

### Settings page

27. As the wearer, I want the Office Weekdays as seven checkboxes with
    the current three ticked, so that I can see and change them in one
    place.
28. As the wearer, I want anything but exactly three weekdays refused
    with the CLI's message, so that the Closets stay varied.
29. As the wearer, I want a note that changing the Office Weekdays
    re-anchors every Rotation, so that I know no Position moves.
30. As the wearer, I want the Cold Threshold as a number in °F,
    pre-filled, so that I can see and change it.

### Writes and notices

31. As the wearer, I want every write to bring me back to the page I
    came from with a one-line notice of what was recorded, so that I
    know it worked.
32. As the wearer, I want the notice to say when what I asked for was
    already the case, so that I can tell "recorded" from "nothing to
    change".
33. As the wearer, I want a refused write to show the form again with
    the message, so that I can correct it.
34. As the wearer, I want reloading a page after a write not to repeat
    the write, so that a reload is harmless.
35. As the wearer, I want the State written only when it actually
    changes, so that browsing never touches the file.
36. As the wearer, I want a fresh install, with no State file yet, to
    answer from the given Wardrobe and write nothing, so that I have
    nothing to set up.
37. As the wearer, I want an unreadable State to show a clear message
    and the nav, so that I know what went wrong.
38. As the wearer, I want every page served uncached, so that a
    Home Screen app resumed the next morning never shows yesterday.

### Access

39. As the wearer, I want the token to be part of the bookmarked URL,
    so that there's no login on the phone.
40. As anyone without the token, I want a plain 404, so that the app
    reveals nothing.

### Widget

41. As the wearer, I want a small Home Screen widget showing 🏢 Office
    or 🏠 Home and a short date ("Mon 28"), so that I know the day at a
    glance.
42. As the wearer, I want the widget's rows to be Shirt, Pants, any
    Outerwear, then shoes, each an icon in its Color with its full name,
    so that it reads like the Day page.
43. As the wearer, I want an "if it's cold" Outerwear row dimmed with no
    extra words, so that it fits the small tile.
44. As the wearer, I want the widget to ask for the phone's own date,
    so that it agrees with the calendar in my pocket.
45. As the wearer, I want the widget to keep showing the last good
    Outfit when it can't fetch, so that no signal isn't a blank tile.
46. As the wearer, I want the header date marked with ⚠︎ in a warning
    colour when the Outfit shown isn't today's, so that I don't wear
    yesterday's by mistake.
47. As the wearer, I want the header to read "⚠︎ State won't read" when
    the server reports an error, so that I know to open the Day page.
48. As the wearer, I want the header to read "⚠︎ Renew PythonAnywhere?"
    when the server answers with something that isn't JSON, so that a
    lapsed web app reminds me to renew.
49. As the wearer, I want the widget to show only the message when it
    has nothing cached yet, so that it never shows a made-up Outfit.
50. As the wearer, I want tapping the widget to open the Day page, so
    that the full detail is one tap away.

### Moving, backing up, and upkeep

51. As the wearer, I want to upload my existing `state.json` and have it
    read unchanged, so that my Anchors and Overrides survive the move.
52. As the wearer, I want my never-replaced Labels to become full names
    ("Light Blue") by themselves, so that no conversion script is
    needed.
53. As the wearer, I want to check today's Day page against the Mac
    before I stop using the CLI, so that a wrong State path can't
    silently serve a fresh default State.
54. As the wearer, I want to download `state.json` at each monthly
    renewal, so that I can lose at most a month of changes.
55. As the wearer, I want deploying an update to be `git pull`,
    `uv sync` and Reload, so that upkeep is three steps.
56. As the maintainer, I want the core to run on Python 3.13, so that
    it runs on PythonAnywhere.
57. As the maintainer, I want the CLI deleted once the State has moved,
    so that there's one interface and one writer.

## Implementation Decisions

### Core: Garment and Color

- **Label = full name** as typed, without the kind: "Light Blue". The
  page and widget append the kind ("Light Blue Shirt"). The given
  Wardrobe in `wardrobe` changes its starting Labels to full names,
  and gives each Garment a starting Color (and a stripe Color for the
  striped Shirt) beside it, taken from the emoji prototype's `FILL`
  table. Every Garment always has a Color.
- **State gains `colors`**, keyed exactly like `labels` (by where the
  Garment hangs, ADR-0010). Each value is a Color and an optional
  stripe Color. The store writes only the entries that differ from the
  given ones, as it does for `labels`, so the live file (whose
  `labels` is `{}`) reads unchanged.
- **Colors are `#rrggbb` strings**, the value an `<input type="color">`
  posts. `color` is the spelling everywhere: the term, the State key,
  form fields and JSON.
- **`Outfit` holds `Garment` values**, not Label strings:

  ```python
  @dataclass(frozen=True)
  class Garment:
      label: str
      color: str
      stripe_color: str | None = None
  ```

  `Outfit.shirt`, `.pants`, `.shoes` are `Garment`; `.sweater` and
  `.jacket` are `Garment | None`. `answer` looks up the Color at the
  same place it looks up the Label today, so the renderers read
  `outfit.shirt.color` directly. The given structure (`Shirt`,
  `PantsRow`, `Closet`) is untouched: it's given and holds no told
  data.
- **`replace_(state, garment, label, color, stripe_color=None)`**. The
  Garment is still addressed as `<closet>.<kind>.<label>` and split on
  the last dot. It refuses a Label containing `.`, and still refuses a
  Label held by another Garment of the same kind in that Closet.
- **`swap`** exchanges the `colors` entries along with the `labels`
  entries.
- **Python 3.13:** `requires-python = ">=3.13"`, `.python-version`
  `3.13`, and the `except` in `forecast` gets parentheses. Raise the pin
  again when PythonAnywhere offers 3.14.
- **`TIMEZONE = ZoneInfo("America/New_York")`** in `wardrobe`, next to
  `LATITUDE`/`LONGITUDE`. Every "today" in the web shell comes from it.

### Web shell

- **Flask**, a new dependency, in a `web` module, with Jinja templates:
  a base layout (nav and notice), then Day, Closet and Settings.
- **App factory:** `web.app(state_path, token, fetch_weather=...)`.
  PythonAnywhere's WSGI file calls it, and the secret token never
  enters git. Tests pass a temp path and a weather stub.
- **Token:** the first path segment of every URL
  (`/<token>/day/2026-09-28`). It's checked once, in a URL value
  preprocessor, with `hmac.compare_digest`. A wrong token is a plain
  404. There's no login and no cookie.
- **Routes** (all under `/<token>`):
  - `GET /` is today's Day page. `GET /day/YYYY-MM-DD` is any date's.
    The date picker is a GET form that lands on it.
  - `GET /closet`, `GET /settings`.
  - `POST` actions: day type (`record_override`), reset, reset
    outerwear (today only), replace, swap, office weekdays, cold
    threshold. Each calls the one core function (ADR-0009), writes the
    State only if the returned State differs, and answers `303` to the
    originating page with `?notice=<text>`. A refusal (`What2wearError`)
    re-renders the form with the message.
  - `GET /day/YYYY-MM-DD.json` is the widget endpoint.
- **Strings:** the web shell owns every confirmation line, the
  `, if it's cold` hedge, the past-date note and the unavoidable-repeat
  note, reworded as it needs. Refusal messages stay in core.
- **Day page:** icons are inline SVG built from the same path data the
  widget gets. Prev/next go one calendar day. "Switch to the
  jacket/sweater" appears only for today on a Home Day. There are no
  confirm steps.
- **Closet page:** both Closets grouped by Pants Row. Each Shirt shows
  its next due date (`get_due_date`) linking to its Day page, and a
  "Swap with…" `<select>` listing only Shirts that share its Pants.
  Each Garment opens a Replace form: a name box, an
  `<input type="color">`, and a "Striped" checkbox with a second color
  input that's ignored when the box is unchecked. No JS.
- **Settings page:** seven weekday checkboxes, and
  `<input type="number" step="any">` for the Cold Threshold in °F,
  both pre-filled.
- **Caching:** `Cache-Control: no-store` on every response.
- **Failures:** an unreadable State gives a 500 page with the message
  and the nav, or `{"error": "…"}` with a 500 on the JSON endpoint. A
  failed forecast is not an error; it gives the ", if it's cold" hedge
  and `"if_cold": true`.

### Icons

- One source of shapes, in Python. Each kind (shirt, pants, sweater,
  jacket, shoes) has a `shape` path and a `detail` path in a 32×32 box,
  using only `M`, `L`, `Q` and `Z`. There are no dashes: the shirt
  placket is short segments.
- A striped Garment adds a `pattern` path: vertical rectangles inside
  the torso (about x 8–24, y 13–28), since the widget can't clip. The
  Day page uses the same path, not an SVG `<pattern>`.
- Each icon is drawn in three layers: fill `shape` with `fill`, fill
  `pattern` with `pattern_fill` if it's present, then stroke `detail`.

### Widget JSON contract

Built from the web shell and icon tickets:

```json
{"date": "2026-09-28", "day": "office",
 "outfit": [
   {"garment": "shirt", "label": "Striped",
    "icon": {"shape": "M9 5 L4 8 … Z", "fill": "#f4f4f1",
             "pattern": "M10 13 L11.5 13 L11.5 28 L10 28 Z …",
             "pattern_fill": "#3c67b4",
             "detail": "M16 9 L16 10 M16 13 L16 14 …"}},
   {"garment": "pants", "label": "Khaki", "icon": {…}},
   {"garment": "sweater", "label": "Grey", "if_cold": true,
    "icon": {…}},
   {"garment": "shoes", "label": "White", "icon": {…}}]}
```

Items are in widget order (Shirt, Pants, any Outerwear, shoes).
`pattern`/`pattern_fill` are omitted when there's no stripe, and
`if_cold` is present only when the forecast is unknown.

### Scriptable widget

- A single script, kept in the repo, that the wearer pastes into
  Scriptable. Its token and host are constants at the top.
- It fetches `/<token>/day/<phone's date>.json`. It draws with
  `DrawContext` from the paths (a ~15-line parser mapping `M`/`L`/`Q`/`Z`
  to `move`/`addLine`/`addQuadCurve`/`closeSubpath`), scaling the 32×32
  box.
- Widget constants, not sent: the detail stroke (translucent white,
  width 1.2) and the dimming of an `if_cold` row (reduced alpha on icon
  and text). The font is the system font.
- Its tap URL is the Day page.
- **When it can't fetch:**
  - It caches every good response in `FileManager.local()` and draws
    from the cache on any failure.
  - The header date gets ⚠︎ in a warning colour only when the cached
    date isn't today.
  - No network: cache plus that marker, with no message.
  - `{"error"}` with a 500: cache, with the header "⚠︎ State won't
    read".
  - Any non-JSON answer: cache, with the header "⚠︎ Renew
    PythonAnywhere?". The widget never parses PythonAnywhere's HTML.
  - No cache: the header message alone.
  - It doesn't prefetch tomorrow.

### Deploy, move, and CLI removal

- **Deploy:** in PythonAnywhere's bash console, `git clone`, then
  `pip install --user uv`, then
  `uv sync --frozen --no-dev --python python3.13`. The web app's
  virtualenv setting points at `.venv`. An update is `git pull`,
  `uv sync`, then Reload.
- **Order:**
  1. Deploy the web shell with the CLI still in the repo.
  2. Upload `state.json` in the Files tab to the WSGI file's
     `state_path`.
  3. Check today's Day page against `what2wear` on the Mac.
  4. Stop using the Mac CLI.
  5. Commit and deploy the CLI deletion: `cli`, `test_cli`, the
     `[project.scripts]` entry, `platformdirs`, and the CLI's
     per-file ruff ignores. The Mac file stays as a frozen copy.
- **Backup:** download `state.json` from the Files tab at each monthly
  renewal. Restore by uploading it. There's no endpoint for either.

### Docs

- **CONTEXT.md:**
  - **Label** becomes "what a Garment is called, in words you'd say
    (Light Blue)". It's no longer "the whole of what the tool prints".
    Drop `color` from its _Avoid_, and drop the `show-closet` /
    `office.shirt.ecru` wording under Garment.
  - Add **Color**: "the color a Garment is drawn in, told with its
    Label", with an optional stripe Color. Cross-link it with Label.
  - Garment's "its Label is the only thing about it that can change"
    becomes "its Label and Color".
- **New ADR, "Garments carry a told Color":** the State gains
  `colors`, reversing "the Label is the whole of what the tool prints".
  An `Outfit` now carries `Garment` values.
- ADR-0009 stands. The web shell replaces the CLI's chooser and
  renderers, and core doesn't move beyond the Color change.
- README: how to deploy, renew and back up, and how to install the
  widget.

## Testing Decisions

- **Test external behaviour only.** Core tests call the public
  functions and assert on the returned State or `Response`. Web tests
  go through Flask's `test_client()` and assert on status codes,
  redirects, the notice, the rendered text, the JSON and the file on
  disk, never on templates or helpers.
- **Core** (existing seam, extended):
  - Every `outfit.<kind> == "…"` assertion becomes
    `outfit.<kind>.label == "…"`. This is the first step, done
    mechanically.
  - `test_replace`: Replace sets the Color and stripe Color, refuses a
    `.` in the Label, and moves no Rotation.
  - `test_swap`: Colors travel with Labels.
  - `test_store`: `colors` round-trips, only changed entries are
    written, and a file without `colors` (the live one) reads with the
    given Colors.
  - `test_wardrobe`: every given Garment has a Color, and every given
    Label is a full name with no `.`.
- **Web shell** (new seam, one test module, prior art `test_cli.py`,
  which it replaces). Weather is injected, so no test touches the
  network. The checklist from the CLI ticket, plus the new surface:
  - A fresh install answers and writes nothing.
  - The State is written only when it changes.
  - `recorded` vs `already` in the notice.
  - The past-date note.
  - The unavoidable-repeat note.
  - The Outerwear hedge while the forecast is unknown.
  - A clear message for an unreadable State (page and JSON, both 500).
  - A wrong token is a 404.
  - `/` is today in `TIMEZONE`.
  - Each write answers 303 to its page with the notice.
  - A refusal re-shows the form with the core message.
  - Swap offers only Shirts sharing Pants.
  - "Switch to the jacket/sweater" shows only for today on a Home Day.
  - The JSON matches the contract above, including a striped Shirt's
    `pattern` and an unknown forecast's `if_cold`.
  - Every response is `no-store`.
- **Widget:** there's no automated test. A manual check on the phone
  after install covers a normal tile, a dimmed "if it's cold" row, a
  striped Shirt, airplane mode (cached Outfit with the ⚠︎ date the next
  day), and a wrong token ("⚠︎ Renew PythonAnywhere?").
- **The move:** there's no automated test. Step 3 of the order, today's
  Day page against the Mac, is the check.

## Out of Scope

- Keeping the Mac CLI alive alongside the phone. That needs two writers
  and sync.
- A native iOS app, Pyodide, a-Shell, or Cloudflare Workers.
  Cloudflare is the fallback only if PythonAnywhere free goes away.
- A Shortcuts front end. It could be added later against the same
  server.
- Login, cookies or accounts beyond the one token.
- Download, restore or backup endpoints, and scheduled backups.
- A medium or large widget, widget buttons, or prefetching tomorrow.
- JS on the pages.

## Further Notes

- Accepted costs: no signal means no what2wear. The widget refreshes
  on iOS's schedule, so it can show yesterday's Outfit for up to an
  hour after midnight, and the ⚠︎ date covers that. Scriptable was last
  updated in September 2024. The token shows in history, screenshots
  and the access log, which is fine for this data.
- If a Label is replaced on the Mac before the move, it gets retyped
  once on the Replace form after the move. There's no short-Label
  compatibility.
- The emoji prototype (`../phone-wayfinder/prototype/emoji_outfit.py`, variant E) is the
  reference for the look and the starting Colors.
