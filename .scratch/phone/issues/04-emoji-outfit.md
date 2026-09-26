# 04 — What an emoji Outfit looks like

Type: prototype
Status: resolved
Blocked by: none

## Question

How should one day's Outfit look as emoji?

Labels are colours or cuts ("ecru", "lblue", "striped"), and 👕 comes in
only one colour. So how does the rendering show:
- the Shirt, Pants and shoes
- any Outerwear, and whether it's worn or only called for "if it's cold"
- Office Day vs Home Day

Prototype a few renderings against real Outfits from the given
Wardrobe and pick one.

## Answer

**A small widget of drawn, emoji-style garment icons in each garment's
real colour, each followed by its full name.** Picked by prototype on
2026-09-26 (variant E in
[the prototype](../prototype/emoji_outfit.py); regenerate its page with
`uv run python .scratch/phone/prototype/emoji_outfit.py`).

```
🏢 Office · Mon 28
[👕 light blue]  Light Blue Shirt
[👖 black]       Black Pants
[🧶 grey]        Grey Sweater      ← dimmed when only "if it's cold"
[👞 white]       White Shoes
```

- **Size:** the small widget.
- **Header:** 🏢 Office or 🏠 Home, then a short date ("Mon 28"). The
  month is dropped so the header fits.
- **Rows:** Shirt, Pants, any Outerwear, then shoes. Each row is an
  icon for that kind of Garment (shirt, pants, sweater, jacket, shoes),
  drawn and filled with the Label's colour, plus the full name: "Light
  Blue Shirt", not `lblue`. `striped` gets stripes.
- **Outerwear:** worn → shown plainly. "If it's cold" (no forecast) →
  the row is dimmed, with no extra words; "if cold" didn't fit on a
  small tile. Warm → no Outerwear row.
- **Font:** Apple's system font (SF Pro).

Why the others lost:
- Unicode emoji (A, B, D) have one 👕, one 👖. Colour hearts or squares
  collapse `lgreen`/`dgreen` and `tan`/`brown`/`beige`, and `striped`
  has no colour.
- The paper doll (C) can't tell a sweater from a jacket.
- A bare Label (`lblue`) reads worse than a full name.

What this leaves open (now tickets): how the icons get drawn on the
phone, since Scriptable can't show SVG; and where each Label's full name
and colour come from, since a Label can be replaced with anything.
