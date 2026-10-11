# 02 — The look

Type: prototype
Status: resolved
Blocked by: none

## Question

What single visual style do the pages share, so that they feel like a
native iOS app rather than a bare web page?

Type scale and weights (SF Pro / system-ui), colour and backgrounds in
light and dark, materials (blur, grouped lists), spacing, corner
radii, and how navigation between Day, Closet and Settings sits (an
iOS tab bar?). Today's pages are `src/what2wear/templates/`.

## Answer

**B — bold cards with a segmented control**, chosen over grouped
lists with a tab bar (A) and glass over colour (C).

The prototype is on the throwaway branch `prototype/the-look`
(`src/what2wear/templates/base.html`, run with
`uv run python prototype_the_look.py`), showing look B with
`?variant=B`.

What the look is, as prototyped:

- **Navigation**: a Day / Closet / Settings segmented control pinned
  to the top under a blurred bar, not a tab bar.
- **Type**: the system font (SF Pro). Page titles 40 pt heavy (800)
  with tight tracking; above the Day page's title, the date as a small
  15 pt semibold uppercase grey eyebrow. Section heads 22 pt bold.
- **Surfaces**: a plain background (white / black) with content on
  filled rounded cards (`#f2f2f7` / `#1c1c1e`), large radii (20–26 pt),
  no hairline dividers.
- **Colour**: monochrome. Buttons are filled capsules in the label
  colour (black on light, white on dark), so the Garments' own Colors
  are the only colour on the page.
- **Actions**: kept but tucked away. On the Day page they sit in a
  "⋯" bottom sheet, and the Outfit gets the screen as big tiles, the
  Shirt full width. (The exact Day layout is for **The Day page**;
  this sets the direction.)
- **Light and dark** follow the system.

Stopgap in the prototype, not decided here: the Outfit tiles are dark
in both modes only because today's icons outline in white. The tile
behind the art is for **The garment art**.
