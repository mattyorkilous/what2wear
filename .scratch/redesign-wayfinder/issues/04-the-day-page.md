# 04 — The Day page

Type: prototype
Status: resolved
Blocked by: 02, 03

## Question

How does the Day page look, with the Outfit taking up most of the
screen?

Where the date and Office/Home Day go, quietly; how the Outerwear hedge,
past-date note and unavoidable-repeat note show; and where the actions
go, kept but less visible: Make this a Home/Office Day, Wear a different
shirt, Switch to the jacket/sweater, and the date picker (a "⋯" sheet?).

## Comments

- From **The garment art**: a lean, not a decision. Tops take a
  full-width card and pants and shoes share a row below. See
  `prototype/the-garment-art`.

## Answer

**C — a list with a bottom toolbar**, chosen over a title with a "⋯"
sheet (A) and a tap-to-change poster (B).

The prototype is on the throwaway branch `prototype/the-day-page`
(`src/what2wear/templates/day.html`, run with
`uv run python prototype_the_day_page.py`), showing C with `?v=C`.

What the Day page is, as prototyped:

- **Title**: the Day ("Office Day" / "Home Day") as look B's heavy
  40 pt title. The date is not in the title; it lives in the toolbar.
- **The Outfit**: one filled rounded card per Garment, as a list read
  top to bottom (Shirt, Pants, shoes): the art at ~96 pt (the Shirt
  ~120 pt) on the left, the Garment's label large and heavy (22 pt,
  800), its kind small and grey beneath.
- **The Outerwear hedge**: when there's no forecast yet, the Outerwear
  isn't faded into the list — it gets its own section under an
  uppercase grey "If it's cold" heading, its row saying
  "<Kind> · no forecast yet". With a forecast, Outerwear that's worn
  is simply a row in the list.
- **The notes** (past date, unavoidable repeat): a grey caption under
  the title, above the Outfit.
- **The bottom toolbar**: a floating blurred capsule at the thumb —
  ‹, the date (tapping it opens the native date picker, which goes to
  that day on change), ›, and a "⋯" button.
- **The "⋯" menu**: a small popover above the toolbar, not a full
  sheet: "Make this a(n) Office/Home Day", "Wear a different shirt",
  and "Switch to the jacket/sweater" (when it applies). "Wear a
  different shirt" opens a bottom sheet with a grid of the Closet's
  Shirts drawn in their Colors; tapping one posts it, the current one
  outlined.
- The Day / Closet / Settings segmented control stays at the top, as
  look B set it.

Left open, not decided here: on a short Outfit (no Outerwear) the list
ends partway down the screen. Stretching the rows to fill it pushed the
"If it's cold" section off-screen, so it was left as is.
