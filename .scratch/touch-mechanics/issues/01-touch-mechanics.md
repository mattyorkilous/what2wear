# 01 — The Outfit swipes days, segment taps answer at once, sheets pull down to close

**What to build:** the three touch changes in [the Touch mechanics
spec](../spec.md). On the Day page only a drag on the Outfit moves a
day, and only the Outfit follows the finger; the week strip still moves
a Week; a drag anywhere else does nothing. Tapping a segment moves its
highlight at once and shows the new page's title alone until the page
arrives. Every sheet can be pulled down to close.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

### The Outfit swipes days

- [x] The Outfit's worn rows, the "If it's cold" heading and that
      section's rows sit inside one Outfit block; the week strip, title
      and captions sit outside it. The rows still share the height
      between the strip and the toolbar.
- [x] A sideways drag that starts in the Outfit block moves a day, and
      only the block follows the finger; past a quarter of the screen
      width it commits, otherwise it springs back.
- [x] On the new day only the Outfit block slides in, from the side the
      swipe came from; the strip and title render in place.
- [x] A drag on the strip moves a Week and moves only the strip.
- [x] A sideways drag starting on the title, the captions or the
      toolbar does nothing; vertical scrolling, the 24 px edge rule, the
      open-popover guard and `location.replace` are unchanged.
- [x] A web test asserts every Outfit row, the "If it's cold" heading
      included, is inside the one block, and the strip and title are not.

### A segment tap answers at once

- [x] Each segment link carries the title of the page it opens:
      "Closet", "Settings", and for Day today's title, "Home Day" or
      "Office Day". The links still go to the same URLs.
- [x] On a plain tap (click, not touch-down) of another segment, the
      highlight moves to it and the page's main content is replaced by
      that title alone, then the link navigates as it would without
      script. Modified clicks are left to the browser.
- [x] Tapping the current segment does nothing.
- [x] A page restored from the back-forward cache shows itself with its
      own segment highlighted, not the placeholder.
- [x] Web tests assert the carried titles from the Day, Closet and
      Settings pages, on a Home Day, on an Office Day, and with a Day
      Type Override on today.

### Sheets pull down to close

- [x] Every `.sheet` popover — the Closet's Shirt sheets, each Replace
      sheet, and the Day page's "Wear a different shirt" — follows a
      downward drag that starts anywhere on it while it's scrolled to
      its top. The "⋯" menu doesn't.
- [x] Let go past about a quarter of its height, or flicked down fast,
      the sheet closes; otherwise it springs back. A sheet scrolled
      partway scrolls instead.
- [x] Pulling closed a Replace sheet opened from a Shirt's sheet leaves
      the Shirt's sheet open, and discards its unsaved fields as a tap
      outside does. Tapping outside still closes any sheet.

### Checked by hand on the phone

- [ ] Day swipes from each part of the Outfit; Week swipes on the strip;
      dead swipes on the title, captions, toolbar, Closet and Settings.
- [ ] The instant segment switch, and back to a page switched away from.
- [ ] Pulling each kind of sheet, a flick, a scrolled sheet, a nested
      Replace sheet, and a pull starting in the Name field (if it fights
      the cursor, drags from a focused field may be left to it).
