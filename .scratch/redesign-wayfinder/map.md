# Redesign — wayfinder map

Label: wayfinder:map

## Destination

A handoff spec at `.scratch/redesign/spec.md` for making what2wear look
and feel like a native iOS app: the Day, Closet and Settings pages
restyled, the Outfit's drawn garments filling the Day page, swiping
between days, a visual Closet, and a tidied small widget.

## Notes

- Domain: `CONTEXT.md` is authoritative for naming. The Phone spec
  (`.scratch/phone/spec.md`) is the baseline this effort restyles; its
  decisions stand unless a ticket here reverses one.
- Standing constraints, settled while charting:
  - **Still a web app**, saved to the Home Screen, that *feels* native.
    The hosted Python core on PythonAnywhere free is unchanged. No
    native iOS app.
  - **JS is allowed on the pages**, reversing the Phone spec's "no JS".
    Each day keeps its own URL and every write stays a POST form, so
    the back button, bookmarks and the widget's tap URL keep working.
  - **The garments keep their virtual, emoji-like look**, drawn better
    and in each Garment's Color. No photos.
  - **Only the small widget.** A medium widget is still out of scope.
  - **Light and dark follow the system.**
  - **Shirts are cut by Closet:** every Office Shirt is a long-sleeve
    button-up with a collar, every Home Shirt a short-sleeve crew-neck
    tee (now in `CONTEXT.md`).
  - **The Outfit is the main thing.** The options all stay, but less
    visible.
- Consult `/grilling` and `/domain-modeling` on grilling tickets,
  `/prototype` on prototype tickets, and `/research` on research tickets.

## Decisions so far

- [What Scriptable can draw](issues/01-what-scriptable-can-draw.md) — solid fills, alpha and curves but no gradients, clipping or shadows in DrawContext; gradient backgrounds on stacks; design for a 158 pt tile with rounded SF fonts; keep the art in DrawContext, PNG only as a last resort
- [The look](issues/02-the-look.md) — bold cards: a top segmented control, heavy 40 pt titles, filled rounded cards, monochrome capsule buttons, actions behind a "⋯" sheet; light/dark follow the system
- [The garment art](issues/03-the-garment-art.md) — emoji-style icons, one per Garment, in its Color with a darker-shade outline and a soft shade, no gloss; one-piece tee for Home, buttoned collared shirt for Office; full-height stripes cut to shape; all drawable in DrawContext
- [The Day page](issues/04-the-day-page.md) — a list with a bottom toolbar: the Day as the title, one row per Garment (art left, label large), the no-forecast Outerwear in its own "If it's cold" section, notes under the title; ‹ date › and a "⋯" menu in a floating toolbar at the thumb

## Not yet specified

- Whether Replace and Swap become sheets over the Closet or stay their
  own pages. Waits on the Closet page.
- What a Shirt's Outfit shows for Outerwear when it's opened from the
  Closet and its due date has no forecast yet.

## Out of scope

- A native iOS app, a medium or large widget, and photos of real
  Garments.
