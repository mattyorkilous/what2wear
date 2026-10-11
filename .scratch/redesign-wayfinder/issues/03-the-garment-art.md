# 03 — The garment art

Type: prototype
Status: resolved
Blocked by: 01

## Question

What do the redrawn garments look like, keeping the virtual, emoji-like
vibe but looking much better?

- Each kind (Shirt, Pants, sweater, jacket, shoes) in its Color, with
  stripes for a striped Garment.
- A Home Shirt is a short-sleeve crew-neck tee; an Office Shirt is a
  long-sleeve button-up with a collar.
- Laid out as one composition that fills the screen (a flat-lay?)
  or as a stack of large icons.
- Drawable by the widget too, within what Scriptable can draw, or with
  a server-rendered fallback.

Today's art is `src/what2wear/icons.py`.

## Answer

**A — emoji tiles, without the gloss**, chosen over a flat-lay (B) and
die-cut stickers (C).

The prototype is on the throwaway branch `prototype/the-garment-art`
(`src/what2wear/prototype_art.py`, run with
`uv run python prototype_the_garment_art.py`), showing the art with
`?art=A`.

What the art is, as prototyped:

- **One icon per Garment** in a 64-unit box, not one composition:
  rounded silhouettes drawn with curves (`M L Q C Z`).
- **Fill** in the Garment's Color. **Outline and details** (neckline,
  cuffs, hem bands, zip, waistband, laces) in a darker shade of that
  same Color, or a lighter one for a very dark Color, so a White
  Garment still shows on a light card.
- **Depth** from a soft offset shade (black at ~20%) under the shape
  only. **No glossy highlight.**
- **A Home Shirt** is a short-sleeve crew-neck tee in one piece, with no
  seam between sleeve and body. **An Office Shirt** is a long-sleeve
  button-up with a collar, a placket and five visible buttons (a light
  shade of its Color, outlined in the darker one).
- **Shoes** are drawn as a pair, the far shoe up and behind.
- **Stripes** run the full height of the top, sleeves included. The
  widget can't clip, so each stripe is the silhouette cut to a band
  ahead of time, a plain polygon it can fill.
- **On the cards:** the art sits on look B's light filled card
  (`#f2f2f7` / `#1c1c1e`), replacing that prototype's stopgap dark tile.
- **Drawable by the widget:** every layer is a solid fill or stroke
  with alpha, which DrawContext supports. No server-rendered PNG.

A lean for **The Day page**, not decided here: tops (the Shirt, and
the sweater or jacket) take a full-width card, then pants and shoes
share a row, so no card is left half-empty.
