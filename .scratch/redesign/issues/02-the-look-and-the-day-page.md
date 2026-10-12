# 02 — The look and the Day page

**What to build:** The shared look across Day, Closet and Settings,
with notices as a fading toast. The Day page in that look: the Outfit
fills the screen, with a week strip and swiping between days. The
Closet and Settings take on the base layout here and get their own
redesign in 03.

Every page still works without script. Each day is its own URL, and
every write is a POST form answered with a 303 and `?notice`.

See [the spec](../spec.md): *Principles*, *The look*, *Day type
lookup*, *Day page*, *Swiping between days*, *Notices* and *Docs*.
The visual references are `prototype/the-look` (`?variant=B`) and
`prototype/swiping-between-days` (`?v=D`, the Day page to build).
Read these branches and rebuild them to `CODING_STANDARDS.md`. Don't
merge them.

**Blocked by:** 01 — The garment art and the widget

**Status:** done

### The look

- [ ] The base layout:
      - a pinned Day / Closet / Settings segmented control under a
        blurred bar, with the current page selected;
      - `system-ui`, with 40 pt weight-800 titles and 22 pt bold
        section heads;
      - cards `#f2f2f7` / `#1c1c1e` with 20–26 pt radii and no
        dividers;
      - monochrome capsule buttons;
      - light and dark through `prefers-color-scheme`.
- [ ] Notices and refusal messages show as a capsule toast under the
      segmented control. With script, it fades after a few seconds and
      `notice` is stripped from the URL, so a reload doesn't show it
      again.
- [ ] Menus and sheets use the HTML `popover` attribute, with their
      forms in the page from the start.
- [ ] A new ADR: "The pages may use JS, but every day is a URL and
      every write a form".

### The Day page

- [ ] The title is "Office Day" or "Home Day". The past-date and
      unavoidable-repeat notes sit as a grey caption under it.
- [ ] One card per Garment: the art on the left, the Label (22 pt,
      800), and the kind small and grey beneath. The order is Shirt,
      Pants, shoes, then Outerwear, and the widget JSON follows the
      same order.
- [ ] Outerwear on a cold day is a plain row, and on a warm day there
      is none. With no forecast it goes in its own "If it's cold"
      section, reading "<Kind> · no forecast yet". The ", if it's
      cold" suffix goes.
- [ ] The rows share the height between the strip and the toolbar, the
      "If it's cold" section included. The Shirt's row is a little
      taller, and the art scales with its row, up to 150 pt. This is
      done in CSS only.
- [ ] The floating bottom toolbar holds:
      - the date, a native date input that goes to the picked day
        (without script, its GET form still submits);
      - "Today", absent on today;
      - "⋯".
- [ ] The "⋯" popover holds "Make this a(n) Office/Home Day", "Wear a
      different shirt" and "Switch to the jacket/sweater". The last
      shows under the same conditions as today.
- [ ] "Wear a different shirt" opens a sheet with a grid of the
      Closet's Shirts as submit buttons, with the current one
      outlined. The `<select>` goes.
- [ ] Core's day-type lookup becomes public (`get_day_type`).
- [ ] A Mon–Sun week strip sits above the title for the shown date's
      Week. Each day shows its weekday letter, day number and O/H.
      The shown day is filled and today is red. Each day links to its
      Day page. ‹ prev / next › go.

### Swiping between days

- [ ] A swipe on the page moves one day, and a swipe on the strip
      moves one week. The page follows the finger and commits past a
      quarter of the screen width; otherwise it springs back.
- [ ] A committed swipe loads the new day with `location.replace`,
      and the new day slides in from the swipe's side. Tapping a strip
      day also replaces the history entry.
- [ ] Vertical scrolling still works. Swipes that start within 24 px
      of either edge are left to Safari.

### Tests

- [ ] `tests/test_outerwear.py` (or wherever core is tested):
      `get_day_type` agrees with `answer(...).day_type` for an
      Override, a Holiday and a plain weekday.
- [ ] `tests/test_web.py`, rewritten wherever it pins removed behavior
      (prev/next, the Shirt `<select>`, the ", if it's cold" suffix,
      the date in the title):
      - the Day title, the week strip's dates, links and O/H (with an
        Override), and the Outfit order on the page and in the JSON;
      - the "If it's cold" section, and "Today" present or absent;
      - the "⋯" forms post to the same routes, and the Shirt sheet
        offers that Closet's Shirts with the current one marked;
      - the notice still reaches every page after a write.
- [ ] The unchanged guarantees stay green: a wrong token is a 404,
      responses are `no-store`, a fresh install writes nothing, the
      State is written only on change, recorded vs already, and an
      unreadable State is a 500.
- [ ] Manual check on the phone:
      - light and dark on each page;
      - swiping a day and a week, the spring-back, the edge gesture,
        and back leaving the Day page;
      - a day with no forecast (four rows and the "If it's cold"
        heading) fitting on the smallest iPhone;
      - the "⋯" popover and the Shirt sheet;
      - the toast fading and not returning on reload.
