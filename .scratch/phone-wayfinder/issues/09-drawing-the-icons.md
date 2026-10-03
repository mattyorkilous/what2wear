# 09 — Drawing the garment icons on the phone

Type: grilling
Status: resolved
Blocked by: none

## Question

The widget shows a drawn, coloured icon for each Garment (see
[What an emoji Outfit looks like](04-emoji-outfit.md)). Scriptable
can't display SVG. Where are the icons drawn?

- The server renders PNGs and the widget loads them (keeps the drawing
  in Python, but likely needs Pillow or a hand-rolled rasteriser on
  PythonAnywhere)
- The Scriptable script draws them with `DrawContext` paths (no server
  change; the shapes live in the widget's JS)
- SF Symbols tinted in Scriptable (`tshirt.fill` exists; pants and a
  sweater probably don't)

This bears on the JSON endpoint in
[The web shell on PythonAnywhere](08-the-web-shell.md): colours and
kinds, or image URLs.

The Day page draws the same icons as inline SVG from Python (see
[Pages and forms for each command](06-pages-and-forms.md)), so the
shapes already exist server-side in some form either way.

## Answer

**The widget draws the icons itself with Scriptable's `DrawContext`,
from path strings the server sends.** Settled by grilling on
2026-09-27.

- **One source of shapes, in Python.** The prototype's shapes use only
  `M`, `L`, `Q`, `Z`, which map one-to-one onto Scriptable's `Path`
  (`move`, `addLine`, `addQuadCurve`, `closeSubpath`). The widget has a
  ~15-line parser; the Day page's inline SVG draws from the same data,
  so the two can't drift. No Pillow, no PNG fetches, no SF Symbols
  (they have no pants, and no sweater vs jacket).
- **Each icon is three layers** in a 32×32 box the widget scales:
  fill `shape` with `fill`; fill `pattern` with `pattern_fill` if
  present; stroke `detail`.
- **Stripes are vertical**, a set of thin rectangles inside the torso
  (about x 8–24, y 13–28), sent as the `pattern` path. `DrawContext`
  can't clip, so the stripes sit where no outline can be crossed. The
  Day page drops its horizontal `<pattern>` and uses the same path.
- **No dashes.** `DrawContext` can't dash, so the shirt placket is sent
  as short segments (`M16 9 L16 10 M16 13 L16 14 …`); the page uses the
  same.
- **Detail lines stay** on the widget: they're what tells a sweater
  from a jacket.
- **Widget constants**, not sent: the detail stroke (translucent white,
  width 1.2) and the dimming of an `if_cold` row (reduced alpha on
  icon and text).
- **JSON** — each outfit item in `/<token>/day/YYYY-MM-DD.json` (see
  [The web shell on PythonAnywhere](08-the-web-shell.md)) gains an
  `icon`; `pattern`/`pattern_fill` are omitted when there's none:

  ```json
  {"garment": "shirt", "label": "striped",
   "icon": {"shape": "M9 5 L4 8 … Z", "fill": "#f4f4f1",
            "pattern": "M10 13 L11.5 13 L11.5 28 L10 28 Z M14 13 …",
            "pattern_fill": "#3c67b4",
            "detail": "M16 9 L16 10 M16 13 L16 14 …"}}
  ```

  Which colours (and full names) a Label gets is
  [Full names and colours for Labels](10-full-names-and-colours.md);
  until then, the prototype's table, grey for an unknown Label.
