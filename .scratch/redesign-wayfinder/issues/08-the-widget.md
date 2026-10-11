# 08 — The widget

Type: prototype
Status: resolved
Blocked by: 01, 03

## Question

How does the small widget use its space, so that it has no excess empty
space, larger text, and everything aligned?

Header, row sizes, icon size, font size and weight, padding, and the
new garment art, within what Scriptable can draw. Today's widget is
`widget.js`.

## Answer

**A — the list, made bigger, with a lighter outline on dark Colors
(O)**, chosen over tiles (B) and big type with a strip (C), and in
dark mode over a lighter card behind each icon (K).

The prototype is on the throwaway branch `prototype/the-widget`
(`src/what2wear/templates/_proto_widget.html` and
`widget_prototype.js`, run with `uv run python prototype_the_widget.py`
and open `/proto/proto/widget`), showing the winner with `?v=O`. The
first commit there holds B and C. Not yet run in Scriptable itself.

What the widget is, as prototyped:

- **Header**: one line, "Office · Mon 12" (the Day word bold, the
  short date grey), 13 pt rounded. A stale cached date turns orange
  with ⚠︎; a message ("⚠︎ Can't reach server") replaces the line, as
  today.
- **Rows**: one per Garment, Shirt, Pants, shoes, then Outerwear last,
  as on the Day page. They share the height under the header: with 3,
  4 or 5 rows the art is 34, 27 or 21 pt and the label 17, 16 or 14 pt
  semibold rounded, so a short Outfit fills the tile rather than
  leaving space at the bottom.
- **Labels drop the kind**: "Light Blue", not "Light Blue Shirt"; the
  art says what it is. This reverses the Phone spec's full names on
  the widget.
- **"If cold" Outerwear**: dimmed to 40%, with a small grey "if cold"
  at the row's right.
- **The art**: the settled emoji tiles, drawn in DrawContext from a
  76-unit box of layers the JSON carries (`M L Q C Z` paths, fills and
  strokes with alpha). The widget's background follows light and dark
  (`#ffffff` / `#1c1c1e`) through `Color.dynamic`.
- **A lighter outline on dark Colors**: the art can't know light from
  dark (`Color.dynamic` doesn't resolve in DrawContext, and
  `Device.isUsingDarkAppearance()` isn't supported in widgets), so it
  is one outline for both modes. Any Color darker than about 0.35
  luminance (Black, Dark Blue, Dark Green, Brown) is outlined in a mix
  ~62% toward white, so it still shows on the dark widget; in light
  mode those garments get a grey edge.
- **This changes the garment art, not just the widget.** The art's old
  cutoff (0.12) let Black (`#26262a`, 0.15) through, so its outline was
  drawn darker than its fill. The new rule is part of the one art the
  pages and the widget share.

## Comments

- Prototype in progress on the throwaway branch `prototype/the-widget`
  (worktree `../what2wear-the-widget`): run
  `uv run python prototype_the_widget.py`, open `/proto/proto/widget`
  and flip `?v=A|B|C`. `widget_prototype.js` draws the same three in
  Scriptable, picked by the widget's Parameter.
