# 06 — Pages and forms for each command

Type: grilling
Status: resolved
Blocked by: 04

## Question

The phone gets server-rendered HTML pages. How does each command
become one?

- Which commands are pages, which are forms (`replace`, `swap`,
  `set-office-weekdays`), and which are buttons on another page
- What the home page is: today's Outfit, `show-closet`, or both
- How "every command acts on one date" (ADR-0008) shows up: a date
  picker, prev/next links, or today only

## Answer

**Three pages: Day, Closet, Settings.** Settled by grilling on
2026-09-27. Plain HTML, no JS; nav links to all three on every page.

- **Day** (`/day/YYYY-MM-DD`; `/` is today, and is the Home Screen
  bookmark). One date's Outfit, drawn the same way as the widget (see
  [What an emoji Outfit looks like](04-emoji-outfit.md)) as inline SVG
  from Python; until
  [Full names and colours for Labels](10-full-names-and-colours.md)
  settles, the Label as written stands in.
  - Date: ‹ prev / next › step one calendar day, plus a GET form with
    a native `<input type="date">`. A past date carries the CLI's note
    that it's where the Rotation stands now, not what was worn.
  - `go-in` / `stay-home` → one button, "Make this an Office Day" or
    "Make this a Home Day", whichever it isn't now.
  - `reset` → "Wear a different shirt": a `<select>` of that date's
    Closet's Shirts.
  - `reset-outerwear` → "Switch to the jacket/sweater", shown only when
    the page is today and today is a Home Day (the command is undated).
  - No confirm steps; each is undone from the same page.
- **Closet.** `show-closet` is the page: both Closets, grouped by Pants
  Row.
  - `when` stops being a command: each Shirt shows its next due date,
    linking to that Day page.
  - `replace` → tap a Garment for a text box pre-filled with its Label.
  - `swap` → a "Swap with…" `<select>` on each Shirt, listing only
    Shirts sharing its Pants, so a refused Swap is never offered.
- **Settings.** The show commands fold into their set forms, pre-filled.
  - Office Weekdays: seven checkboxes; the server refuses anything but
    exactly three, with the CLI's message. The page notes that changing
    them re-anchors every Rotation, so no Position moves.
  - Cold Threshold: `<input type="number" step="any">`, °F.
- **Writes** are POST → redirect back to the originating page with a
  one-line notice at the top, worded as the CLI's confirmation strings.
  Errors re-show the form with the message.
