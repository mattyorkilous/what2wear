# 03 — The Closet and Settings

**What to build:** The Closet becomes a visual: grids of the
Garments drawn in their Colors, with sheets for a Shirt's Outfit,
Swap and Replace. Settings becomes two cards: day chips for the
Office Weekdays and a stepper for the Cold Threshold, which the
server now limits to whole degrees from 0 to 100.

Both pages still work without script. Every write is a POST form
answered with a 303 and `?notice`.

See [the spec](../spec.md): *Closet page* and *Settings page*. The
visual reference is `prototype/the-closet-page` (`?v=A`). Settings
has no prototype; its spec section is the reference. Read the branch
and rebuild it to `CODING_STANDARDS.md`. Don't merge it.

**Blocked by:** 02 — The look and the Day page

**Status:** ready-for-agent

### The Closet page

- [ ] The Shirts are in one grid per Closet, Home then Office, three
      to a row, with a short last row centered. Each tile shows the
      art, the Label and the due text: "Today" (red), "Tomorrow", a
      weekday within the next six days, otherwise "Mon 26 Oct", or
      "Not due this year".
- [ ] The rest of the Wardrobe is in smaller grids, four to a row,
      one per kind: Pants once, then Home sweaters, Home jackets, Home
      shoes, Office sweaters and Office shoes.
- [ ] A Shirt's sheet holds:
      - its art and name;
      - "Next due <when> ›", linking to that Day;
      - "Worn with": the Outfit on that date, with the no-forecast
        "If it's cold" section;
      - "Swap with" tiles for the Shirts sharing its Pants, or a
        reason it can't Swap;
      - "Replace this Shirt".
- [ ] Every Garment has a Replace sheet:
      - the art large;
      - Name, Color, Striped and the stripe Color;
      - a "Replace the <kind>" button, posting to the existing route.
- [ ] With script, the art redraws live as the Colors change. The
      script uses the same tone rule as 01.
- [ ] A refused Replace answers 422 with the Closet page, that
      Garment's Replace sheet open and filled with what was posted,
      and the message.
- [ ] `GET /closet/<key>` and its template are deleted.

### Settings

- [ ] The page has two cards, "Office Weekdays" and "Cold Threshold",
      and nothing else.
- [ ] The Office Weekdays are seven chip checkboxes, M T W T F S S:
      Office filled, Home outlined. Under the card: "Changing these
      keeps every Rotation where it is."
- [ ] The Cold Threshold is a stepper (− value +), one whole degree
      per tap, clamped to 0–100. A stored decimal shows rounded.
- [ ] With script, each card's Save appears only once that card has
      changed. The weekdays' Save is enabled only at exactly three,
      with a countdown footnote. Without script, both Saves always
      show.
- [ ] Core's `set_cold_threshold` refuses a value below 0, above 100
      or not whole, with a message. A stored decimal is left alone
      until it's saved.

### Tests

- [ ] `tests/test_outerwear.py` (or wherever the threshold is tested):
      0 and 100 are accepted, and −1, 101 and 52.5 are refused, moving
      nothing.
- [ ] `tests/test_web.py`, rewritten wherever it pins removed behavior
      (the Garment page, the Closet grouped by Pants Row, the
      checkboxes and number box):
      - the Closet's order, due text against a pinned today, each
        sheet's Outfit, and Swap partners or the reason there are
        none;
      - a prefilled Replace form for every Garment, the refused
        Replace's 422 with what was posted, and `GET /closet/<key>`
        a 404;
      - Settings' checked chips, the rounded threshold, and 101 / 52.5
        refused while a whole threshold saves.
- [ ] The unchanged guarantees stay green, as in 02.
- [ ] Manual check on the phone:
      - light and dark on the Closet and Settings;
      - the Shirt and Replace sheets, and the live redraw;
      - a refused Replace reopening its sheet;
      - the Save capsule and countdown.
