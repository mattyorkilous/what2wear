# 01 — The garment art and the widget

**What to build:** Every Garment is drawn as the new emoji-style art on
both the Day page and the small widget. The widget is laid out the new
way: bigger, with no empty space, and dark Colors still showing on its
dark tile. The pages keep their current layout. Ticket 02 restyles
them around this art.

See [the spec](../spec.md): *Garment art*, *Widget JSON contract* and
*Scriptable widget*. The reference is `prototype/the-widget` (`?v=O`):
its `prototype_art.py` holds the silhouettes, the stripe cutting, the
tone rule and the 76-unit placement, and its `widget_prototype.js`
holds the DrawContext drawing. Read it and rebuild it to
`CODING_STANDARDS.md`. Don't merge it.

The layer shape, from the prototype:

```python
{"d": "M… L… Q… C… Z", "fill": "#rrggbb", "alpha": 0.22}  # alpha omitted when 1
{"d": "M… L… Q… C… Z", "stroke": "#rrggbb", "width": 2}   # exactly one of fill/stroke
```

**Blocked by:** None — can start immediately

**Status:** done

### The art

- [ ] One icon per Garment, as an ordered list of layers in a 76-unit
      box, with offsets and scale baked into the paths. The paths use
      only `M L Q C Z`.
- [ ] The Shirt's cut follows its Closet: an Office Shirt is a
      long-sleeve button-up with a collar, a placket and five buttons,
      and a Home Shirt is a one-piece short-sleeve crew-neck tee.
      Shoes are drawn as a pair.
- [ ] The layers are a soft offset shade (black at ~22%), the body in
      the Color, then stripes, details and outline in the tone, plus
      the buttons on an Office Shirt. There is no gloss.
- [ ] The tone is the Color mixed ~42% toward black, or ~62% toward
      white when its luminance is below about 0.35, so the given Black
      gets a lighter outline.
- [ ] Stripes are cut to the silhouette ahead of time, as plain
      polygons running the full height of the top, sleeves included.
      They apply to Shirts, sweaters and jackets.
- [ ] The Day page draws the same layers as inline SVG
      (`viewBox="0 0 76 76"`), without the old dark tile and white
      detail stroke.

### The JSON

- [ ] Each outfit item carries `art` (the layer list) in place of
      `icon`. `label` stays the bare Label, and `if_cold` is
      unchanged.

### The widget

- [ ] The path parser handles `C`. Each layer is filled or stroked in
      its color and alpha, with stroke widths scaled to the drawn
      size. The widget no longer has its own detail stroke constant.
- [ ] The header is one line, 13 pt semibold rounded: the Day word in
      bold ("Office" / "Home") and the short date in grey ("Mon 12").
      The stale ⚠︎ date and the failure messages still work as today.
- [ ] The rows share the height under the header. At 3 or 4 rows (an
      Outfit is never more), the art is 34 or 27 pt and the label 17
      or 16 pt semibold rounded. Columns line up through fixed-size
      art stacks and spacers.
- [ ] Labels drop the kind ("Light Blue").
- [ ] An "if cold" row is drawn at 40% alpha, with a small grey "if
      cold" at its right.
- [ ] The background follows light and dark (`#ffffff` / `#1c1c1e`)
      through `Color.dynamic`.
- [ ] The rows follow the JSON's order. Ticket 02 moves Outerwear
      last.

### Tests and docs

- [ ] `tests/test_web.py` covers the art through the Day page SVG and
      the JSON:
      - an Office Shirt's art differs from a Home Shirt's in the same
        Color;
      - only `M L Q C Z` appear in the paths, and every layer has
        exactly one of fill or stroke;
      - a striped Garment carries layers in its stripe Color;
      - a light Color's outline is darker than its fill, and Black's
        is lighter than its fill;
      - the page and the JSON carry the same layers for the same
        Garment.
- [ ] The existing `icon`-shaped tests are rewritten for `art`.
- [ ] The README says to re-paste the widget whenever the server is
      deployed with this change.
- [ ] Manual check in Scriptable: 3 and 4 rows; a striped Shirt;
      Black on the dark widget; airplane mode (cached, with the ⚠︎
      date); a wrong token.
