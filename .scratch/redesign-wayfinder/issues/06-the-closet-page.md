# 06 — The Closet page

Type: prototype
Status: resolved
Blocked by: 02, 03

## Question

How does the Closet become a visual, rather than a page of links?

Starting idea: a grid of the 9 Home Shirts, then the 5 Office Shirts,
drawn in their Colors. Tapping a Shirt brings up its Outfit (on its
next due date?), when it's next due, and Replace and Swap. Where the
Pants, sweaters, jackets and shoes are reached for Replace.

## Answer

**A — a Shirt grid with sheets**, chosen over one card per Pants Row
with each Garment on its own page (B) and an "up next" list of Shirts
by due date with a Day-page-like page per Shirt (C). Two changes were
made to A: sweaters, jackets and shoes each get their own grid instead
of sharing one, and a short last row of Shirts sits centred.

The prototype is on the throwaway branch `prototype/the-closet-page`
(`src/what2wear/templates/closet.html` and `_proto_closet.html`, run
with `uv run python prototype_the_closet_page.py`), showing A with
`?v=A`.

What the Closet page is, as prototyped:

- **Title**: "Closet", in look B's heavy title, under the Day / Closet
  / Settings segmented control.
- **The Shirts**: one grid per Closet, Home Shirts then Office Shirts,
  three to a row. Each tile is the Shirt drawn in its Color, its Label,
  and when it's next due ("Today", "Tomorrow", a weekday within the
  week, else "Mon 26 Oct"; "Not due this year" if never). Today and
  Tomorrow are red. A short last row is centred, so the Office
  Closet's 5 sit 3 over 2.
- **The rest of the Wardrobe**, below the Shirts, as smaller grids four
  to a row, one per kind and never combined: Pants (shared, so once),
  then Home sweaters, Home jackets, Home shoes, Office sweaters, Office
  shoes. Each tile is the art and the Label.
- **Tapping a Shirt** opens a bottom sheet over the Closet, never a new
  page: the Shirt's art and name, a "Next due <when> ›" button that
  goes to that Day, its Outfit on that date ("Worn with": Pants, shoes,
  then any Outerwear), "Swap with" as tiles of the Shirts sharing its
  Pants (tapping one posts the Swap), and "Replace this Shirt".
- **The Outerwear on a due date with no forecast** shows as the Day
  page does: its own "If it's cold" section, the row saying
  "<Kind> · no forecast yet".
- **Replace** is a sheet too, from "Replace this Shirt" or from tapping
  any other Garment: the art large, then Name, Color and Striped (with
  its stripe Color), and a "Replace the <kind>" button. The art redraws
  as the Colors change, before saving.
- A Shirt with no Swap partner says it can't Swap and why.
- Each write is still a POST form that lands back on the Closet with
  its notice.

Not decided here: the separate Garment page (`/closet/<key>`) has
nothing linking to it once Replace is a sheet; whether it stays as a
no-JS fallback or goes is left to the spec.
