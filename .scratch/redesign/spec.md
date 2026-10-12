# Redesign

Status: ready-for-agent

Charted by [the redesign wayfinder map](../redesign-wayfinder/map.md).
Each decision here comes from one of its tickets. It restyles the
[Phone spec](../phone/spec.md), and that spec's decisions stand unless
this one reverses them. Governed by ADR-0009, ADR-0010 and ADR-0012.
Adds one ADR: "The pages may use JS, but every day is a URL and every
write a form".

## Problem Statement

what2wear works on the phone, but it looks like a bare web page.
The Day page is a column of default-styled forms and links, with small
32-unit icons drawn too small for their strokes. A Home Shirt and an
Office Shirt are drawn the same, though one is a tee and the other a
collared button-up. The actions (Make this a Home Day, Wear a
different shirt, Switch to the jacket) get as much room as the Outfit,
which is the thing the wearer opened the page to see. Moving between
days means tapping small ‹ prev / next › links. The Closet is a page of
links grouped by Pants Row, with no picture of the clothes. Settings is
seven checkboxes and a number box. The small widget leaves empty space
at the bottom of the tile, uses small text, and draws Black and other
dark Garments as shapes you can barely see on its dark background.

## Solution

The same web app, still saved to the Home Screen and still served from
PythonAnywhere free, made to look and feel like a native iOS app:

- **One look** across Day, Closet and Settings: a Day / Closet /
  Settings segmented control pinned at the top, heavy 40 pt titles,
  content on filled rounded cards, monochrome capsule buttons. The
  Garments' own Colors are the only color on the page. Light and dark
  follow the system.
- **New garment art**, shared by the pages and the widget: one
  emoji-style icon per Garment in its Color, with a darker outline (or
  a lighter one for a dark Color) and a soft shade under it. An Office
  Shirt is drawn as a collared button-up and a Home Shirt as a tee.
- **The Day page** gives the screen to the Outfit. The Day is the
  title, a Mon–Sun week strip sits above it, and below come one row
  per Garment, sized so that every row fits on one screen. The date,
  "Today" and a "⋯" menu holding the actions sit in a floating toolbar
  at the bottom, within reach of the thumb. Swipe the page to move a
  day, or swipe the strip to move a week.
- **The Closet page** is a grid of Shirts drawn in their Colors, each
  showing when it is next due, followed by smaller grids for the rest
  of the Wardrobe. Tapping a Shirt or a Garment opens a sheet with its
  Outfit, Swap and Replace. While you edit, the art redraws live.
- **Settings** has two cards: day chips for the Office Weekdays and a
  stepper for the Cold Threshold. A Save button appears only once a
  card has changed.
- **Notices** appear as a toast at the top that fades away.
- **The widget** is the same list, made bigger. The rows share the
  tile's height, labels drop the kind, Outerwear comes last, and dark
  Colors get a lighter outline.

## User Stories

### The look

1. As the wearer, I want the pages to look like an iOS app rather than
   a web page, so that what2wear feels at home on my Home Screen.
2. As the wearer, I want a Day / Closet / Settings segmented control
   pinned at the top of every page, under a blurred bar, so that I can
   always get anywhere in one tap.
3. As the wearer, I want the segment for the page I'm on to be
   selected, so that I know where I am.
4. As the wearer, I want each page's title large and heavy, so that I
   can read the page at a glance.
5. As the wearer, I want content on filled rounded cards with no
   hairline dividers, so that the page looks calm and modern.
6. As the wearer, I want the buttons to be monochrome capsules, so
   that the only color on the page is my clothes.
7. As the wearer, I want light and dark to follow my phone's setting,
   so that the app matches everything else at night.
8. As the wearer, I want the system font, so that the type matches
   iOS.

### The garment art

9. As the wearer, I want each Garment drawn as a large emoji-style
   icon in its Color, so that I recognise it at a glance.
10. As the wearer, I want each icon outlined in a darker shade of its
    own Color, so that a White Garment still shows on a light card.
11. As the wearer, I want a dark Garment (Black, Dark Blue, Dark
    Green, Brown) outlined in a lighter shade instead, so that it
    still shows on a dark background.
12. As the wearer, I want a soft shade under each icon and no gloss,
    so that the art has depth without looking cheap.
13. As the wearer, I want every Office Shirt drawn as a long-sleeve
    button-up with a collar, placket and buttons, so that it looks
    like what I wear to the office.
14. As the wearer, I want every Home Shirt drawn as a short-sleeve
    crew-neck tee in one piece, so that it looks like what I wear at
    home.
15. As the wearer, I want a striped Garment's stripes to run the full
    height of the top, sleeves included, so that it looks striped and
    not patched.
16. As the wearer, I want shoes drawn as a pair, so that they read as
    shoes.
17. As the wearer, I want a sweater and a jacket drawn clearly
    differently, so that I reach for the right Outerwear.
18. As the wearer, I want the pages and the widget to draw exactly the
    same art, so that a Garment looks the same wherever I see it.

### The Day page

19. As the wearer, I want the Day page's title to be the Day ("Office
    Day" or "Home Day"), so that I know at once which Closet I'm
    dressing from.
20. As the wearer, I want one card per Garment, with the art on the
    left and the Label large and heavy beside it, so that the Outfit
    is the main thing on the screen.
21. As the wearer, I want the Garment's kind in small grey text under
    its Label, so that the name still reads as "Light Blue · Shirt"
    without shouting it.
22. As the wearer, I want the Outfit in the order Shirt, Pants, shoes,
    then Outerwear, so that the essentials come first.
23. As the wearer, I want every row to fit on one screen without
    scrolling, whether the Outfit has three Garments or four, so that
    I see the whole Outfit at once.
24. As the wearer, I want the Shirt's row a little taller than the
    others, so that the Shirt, the thing I reach for first, stands
    out.
25. As the wearer, I want the art to grow to fill its row, so that a
    short Outfit doesn't stop partway down the screen.
26. As the wearer, I want Outerwear worn on a cold day to be a plain
    row in the list, so that it reads like any other Garment.
27. As the wearer, I want no Outerwear row on a warm day, so that I'm
    not told to wear what I don't need.
28. As the wearer, I want Outerwear on a day with no forecast yet in
    its own "If it's cold" section, its row saying "<Kind> · no
    forecast yet", so that a failed forecast still dresses me without
    implying it's cold.
29. As the wearer, I want the past-date note and the unavoidable-repeat
    note as a grey caption under the title, so that they're there
    without crowding the Outfit.
30. As the wearer, I want a floating toolbar at the bottom holding the
    date, "Today" and "⋯", so that the controls sit under my thumb.
31. As the wearer, I want tapping the date to open the native date
    picker and go to the date I pick, so that I can jump to any date.
32. As the wearer, I want a "Today" button that's hidden when I'm
    already on today, so that I can get back from any day in one tap.
33. As the wearer, I want the actions in a small "⋯" menu above the
    toolbar, so that they're kept but out of the way.
34. As the wearer, I want "Make this a Home Day" or "Make this an
    Office Day" (whichever the date isn't) in the menu, so that I can
    record a Day Type Override in one tap.
35. As the wearer, I want "Wear a different shirt" in the menu to open
    a sheet with a grid of that Closet's Shirts drawn in their Colors,
    the current one outlined, so that I can pick the one I want by
    sight.
36. As the wearer, I want tapping a Shirt in that sheet to Reset the
    Rotation to it at once, so that it takes one tap.
37. As the wearer, I want "Switch to the jacket" or "Switch to the
    sweater" in the menu on today's Home Day, when it applies, so that
    I can put the Home Outerwear Rotation back in step.
38. As the wearer, I want no confirm steps, so that every action is
    one tap and undone from the same place.

### Swiping between days

39. As the wearer, I want a Mon–Sun week strip above the title, each
    day showing its weekday letter, its day number and O or H for its
    Day, so that I can see my week at a glance.
40. As the wearer, I want the day shown filled and today in red on the
    strip, so that I can tell which is which.
41. As the wearer, I want tapping a day on the strip to go to it, so
    that any day this week is one tap away.
42. As the wearer, I want to swipe the page left or right to move one
    day, so that stepping through days feels like an app.
43. As the wearer, I want to swipe the week strip to move one week, so
    that I can get further quickly.
44. As the wearer, I want the page to follow my finger and commit only
    past a quarter of the screen width, springing back otherwise, so
    that a small drag doesn't change the day.
45. As the wearer, I want the new day to slide in from the side I
    swiped from, so that the motion makes sense.
46. As the wearer, I want vertical scrolling to keep working, so that
    a swipe never gets in the way of scrolling.
47. As the wearer, I want swipes that start within 24 px of either
    edge left to Safari, so that its own back and forward gesture
    still works.
48. As the wearer, I want every day to keep its own URL, so that
    bookmarks and the widget's tap still land on a day.
49. As the wearer, I want swiping and the strip to replace the history
    entry rather than add one, so that back leaves the Day page
    instead of walking back through every day I swiped past.

### The Closet page

50. As the wearer, I want the Closet page to be a grid of my Shirts
    drawn in their Colors, three to a row, so that I can see my
    Wardrobe instead of reading it.
51. As the wearer, I want the Home Shirts first and then the Office
    Shirts, each Closet its own grid, so that the two never mix.
52. As the wearer, I want a short last row centered, so that the
    Office Closet's five sit three over two and look tidy.
53. As the wearer, I want each Shirt tile to say when it's next due
    ("Today", "Tomorrow", a weekday within the coming week, otherwise
    "Mon 26 Oct"), so that I can answer "when do I wear this" at a
    glance.
54. As the wearer, I want "Today" in red and every other due date in
    grey, so that only today stands out.
55. As the wearer, I want a Shirt no day within a year wears to say
    "Not due this year", so that it doesn't look broken.
56. As the wearer, I want the rest of the Wardrobe below the Shirts in
    smaller grids, four to a row and one per kind: Pants (once, since
    they're shared), then Home sweaters, Home jackets, Home shoes,
    Office sweaters and Office shoes, so that every Garment can be
    reached for Replace.
57. As the wearer, I want tapping a Shirt to open a sheet over the
    Closet instead of a new page, so that I keep my place.
58. As the wearer, I want the Shirt's sheet to show its art, its name,
    and a "Next due <when> ›" button that goes to that Day, so that I
    can jump to the day I'll wear it.
59. As the wearer, I want the sheet to show the Shirt's Outfit on that
    date under "Worn with" (Pants, shoes, then any Outerwear), so that
    I can see the whole look without leaving the Closet.
60. As the wearer, I want that Outfit's Outerwear on a date with no
    forecast shown as the Day page shows it, in its own "If it's cold"
    section, so that the two pages agree.
61. As the wearer, I want "Swap with" as tiles of only the Shirts
    sharing its Pants, so that I'm never offered a Swap that would be
    refused.
62. As the wearer, I want tapping a Swap tile to Swap at once, so that
    it takes one tap.
63. As the wearer, I want a Shirt with no Swap partner to say it can't
    Swap and why, so that a missing option isn't a mystery.
64. As the wearer, I want "Replace this Shirt", or tapping any other
    Garment, to open a Replace sheet with the art large, then Name,
    Color and Striped (with its stripe Color), and a "Replace the
    <kind>" button, so that Replace feels like editing the Garment
    itself.
65. As the wearer, I want the art in the Replace sheet to redraw as I
    change the Colors, before I save, so that I can see what I'm
    choosing.
66. As the wearer, I want a refused Replace to bring back the Closet
    with that Replace sheet open, filled with what I typed and showing
    the message, so that I can correct it without retyping.

### Settings

67. As the wearer, I want the Settings page to have only two cards,
    "Office Weekdays" and "Cold Threshold", so that it holds only what
    I can tell the tool.
68. As the wearer, I want the Office Weekdays as one row of seven
    round chips, M T W T F S S, with Office days filled and Home days
    outlined, so that they read like the Day page's week strip.
69. As the wearer, I want a footnote under that card saying "Changing
    these keeps every Rotation where it is", so that I'm not afraid to
    change them.
70. As the wearer, I want the Cold Threshold as a stepper (− 50°F +),
    the value large and one whole degree per tap, so that I can change
    it without a keyboard.
71. As the wearer, I want the stepper to stop at 0°F and at 100°F, so
    that I can't set a nonsense threshold.
72. As the wearer, I want a stored decimal threshold shown rounded and
    saved as a whole degree, so that an old 52.5 doesn't break the
    stepper.
73. As the wearer, I want a card's Save button to appear only once
    I've changed that card, so that the page isn't cluttered with
    buttons that do nothing.
74. As the wearer, I want the Office Weekdays' Save enabled only at
    exactly three days, with a footnote counting down ("Pick 1 more"),
    so that I know why I can't save yet.
75. As the wearer, I want a Cold Threshold outside 0–100°F, or not a
    whole number, refused by the server with a message, so that the
    State stays sound however the request arrives.

### Notices

76. As the wearer, I want a notice to show as a small capsule toast at
    the top, under the segmented control, that fades after a few
    seconds, so that I see that a write worked without it staying on
    the page.
77. As the wearer, I want a reload after a notice not to show it
    again, so that an old notice doesn't look like a new write.
78. As the wearer, I want a refusal's message shown the same way, with
    the form still filled in, so that I can correct it.

### Working without JS

79. As the wearer, I want every page to keep working if its script
    fails to load (the Outfit shows, the forms post, the links go),
    so that a slow or broken script never stops me getting dressed.

### The widget

80. As the wearer, I want the widget's header to be one line, "Office
    · Mon 12", with the Day bold and the short date grey, so that it
    takes as little room as possible.
81. As the wearer, I want the widget's rows to share the tile's
    height, so that a short Outfit fills the tile instead of leaving
    space at the bottom.
82. As the wearer, I want the art and the text as large as the number
    of rows allows (art 34 or 27 pt and labels 17 or 16 pt for 3 or 4
    rows), so that the widget is readable at a glance.
83. As the wearer, I want the widget's labels without the kind ("Light
    Blue", not "Light Blue Shirt"), so that they fit large, since the
    art already shows the kind.
84. As the wearer, I want the widget's rows to go Shirt, Pants, shoes,
    then Outerwear, so that it reads like the Day page.
85. As the wearer, I want "if cold" Outerwear dimmed, with a small
    grey "if cold" at the right of its row, so that I know it depends
    on the weather.
86. As the wearer, I want the widget's background to follow light and
    dark, so that it matches my Home Screen.
87. As the wearer, I want a dark Garment to have the same lighter
    outline in the widget, so that Black still shows on the dark tile.
88. As the wearer, I want the stale-date ⚠︎ in orange and the "⚠︎ Can't
    reach server" style messages to keep working, so that I'm never
    shown yesterday's Outfit unknowingly.
89. As the wearer, I want tapping the widget still to open today's Day
    page, so that the full detail is one tap away.

### Maintenance

90. As the maintainer, I want one source of garment art in Python that
    both the pages and the widget draw from, so that the two can never
    disagree.
91. As the maintainer, I want the art made only of what Scriptable's
    DrawContext can draw, so that no server-rendered image is needed.
92. As the maintainer, I want the server tests to keep running without
    a browser, so that the suite stays fast and simple.

## Implementation Decisions

### Principles

- **Still the Phone spec's web app.** Flask on PythonAnywhere free, the
  token in the first path segment, `no-store` everywhere, and the State
  written only when it changes. Core does not move, except for the
  Cold Threshold limits and one public day-type lookup (below).
- **JS is allowed, as an enhancement.** Each page is fully rendered on
  the server and works without script: the Outfit shows, every write
  is a plain POST form answered with a 303 and `?notice`, and every
  day is a GET URL. The script adds swiping, history replacement, the
  toast's fade, the Save capsule's show/hide, the stepper and the
  live redraw. This reverses the Phone spec's "No JS on the pages".
- **Menus and sheets use the HTML `popover` attribute** (with
  `popovertarget` buttons), so they open without script on iOS 17+.
  Their forms are in the page from the start.
- **No new dependencies** and no build step. The CSS and the one
  script file are hand-written and served as Flask static files, or
  inline in the base layout.

### The look (base layout)

- The base layout holds the pinned segmented control (Day / Closet /
  Settings, the current one selected) under a blurred bar, and the
  toast.
- Type: `system-ui` (SF Pro). Page titles 40 pt weight 800 with tight
  tracking. Section heads 22 pt bold. Eyebrows and captions small
  grey.
- Surfaces: page background white / black. Cards `#f2f2f7` / `#1c1c1e`
  with radii of 20–26 pt and no dividers.
- Buttons: filled capsules in the label color (black on light, white
  on dark).
- Colors are CSS custom properties, switched by
  `prefers-color-scheme`.

### Garment art (the icons module, rewritten)

- **One icon per Garment** in one **76-unit box** shared by the pages
  and the widget. The silhouettes are drawn in a 64-unit space and
  placed into the box with their offsets and scale baked into the path
  numbers, because DrawContext has no transforms. The shoes are two
  shoes placed as a pair, the far one up and behind.
- **The art depends on the Closet.** A Shirt's silhouette comes from
  its Closet: Office gets a button-up with a collar, a placket and
  five buttons, and Home gets a one-piece crew-neck tee. The function
  that draws a Garment therefore takes the kind, the Garment and the
  Closet's Day type.
- **Output is an ordered list of layers**, each one path filled or
  stroked in one solid color with an optional alpha. This shape comes
  from the widget prototype:

  ```python
  # one layer, in drawing order
  {"d": "M… L… Q… C… Z", "fill": "#rrggbb", "alpha": 0.22}
  {"d": "M… L… Q… C… Z", "stroke": "#rrggbb", "width": 2}
  # "alpha" is omitted when 1; exactly one of "fill"/"stroke"
  ```

  Paths use only `M L Q C Z`.
- **Layer order for one Garment:** the soft shade (the body offset
  downward, black at ~22%), the body in its Color, the stripes (if
  striped), the detail parts in the tone, the detail lines stroked in
  the tone, the outline stroked in the tone, then the buttons on an
  Office Shirt (a light mix of the Color, outlined in the tone). There
  is no glossy highlight.
- **The tone** is the outline-and-detail color, worked out from the
  Color's luminance (Rec. 709 weights over the sRGB channels). Below
  about 0.35 it is the Color mixed ~62% toward white. Otherwise it is
  the Color mixed ~42% toward black. This one rule serves both modes,
  since the art can't know light from dark, and it replaces the
  prototype's old 0.12 cutoff.
- **Stripes** are the silhouette cut into vertical bands ahead of time,
  so each stripe is a plain polygon DrawContext can fill. They run the
  full height of the top, sleeves included. Stripes apply to Shirts,
  sweaters and jackets.
- **On the pages** the layers are rendered as inline SVG
  (`viewBox="0 0 76 76"`) on the card color. In the widget they are
  drawn by DrawContext.

### Day type lookup (core)

- The week strip needs the Day of seven dates. Core's private
  day-type lookup becomes public (`get_day_type(state, on)`), so the
  web shell doesn't answer a whole Outfit seven times just to read
  O/H. It follows the same rules as today: Day Type Override, then
  Holidays, then Office Weekdays.

### Day page

- **Title:** the Day ("Office Day" / "Home Day"). The date is not in
  the title.
- **The week strip** above the title: the Monday-start Week containing
  the shown date, seven links to their Day pages. Each shows the
  weekday letter, the day number and O/H. The shown date is filled and
  today is in red.
- **Notes:** the past-date note and the unavoidable-repeat note are a
  grey caption under the title. The web shell still owns their
  wording.
- **The Outfit:** one card per Garment, in the order Shirt, Pants,
  shoes, then Outerwear. Each card has the art on the left, the Label
  (22 pt, 800) and the kind small and grey beneath. This reverses the
  Phone spec's order (Outerwear before shoes) on the page.
- **Outerwear:** worn on a cold day, it's a plain row. On a warm day
  there is none. With no forecast it gets its own section after the
  list, under an uppercase grey "If it's cold" heading, its row
  reading "<Kind> · no forecast yet". It is no longer faded into the
  list, and the ", if it's cold" suffix goes.
- **Rows fit the screen:** the rows share the height between the
  strip and the toolbar, the "If it's cold" section included, with
  the Shirt's row a little taller. The art scales with its row, up to
  150 pt. This is CSS only (flex rows with the art sized to its row),
  with no measuring script.
- **The toolbar:** a floating blurred capsule at the bottom holding the
  date (a native `<input type="date">`: changing it goes to that day,
  and without script its GET form still submits to the date picker
  route), "Today" (a link, absent when the shown date is today) and
  "⋯".
- **The "⋯" menu:** a popover above the toolbar with "Make this a(n)
  Office/Home Day" (the existing day-type POST), "Wear a different
  shirt", and "Switch to the jacket/sweater" (the existing outerwear
  POST, shown only on today, on a Home Day, when the day isn't warm,
  as today).
- **"Wear a different shirt"** opens a bottom sheet: a grid of that
  Closet's Shirts drawn in their Colors, each a submit button of the
  existing shirt POST, the current Shirt outlined. The `<select>` goes.
- **‹ prev / next › go.** The strip, swiping and "Today" replace them.

### Swiping between days (the page script)

- A horizontal drag on the page moves one day, and a drag on the strip
  moves one week. The page follows the finger. Past a quarter of the
  screen width it commits: it slides off and loads the new day's URL
  with `location.replace`. Short of that, it springs back.
- The new page slides in from the side the swipe came from. The
  direction is handed over in a way that leaves the day's URL clean,
  for example `sessionStorage`.
- A drag that is mostly vertical is left to scrolling. A drag that
  starts within 24 px of either edge is left to Safari.
- Tapping a strip day also uses `location.replace`. Without script,
  the strip days are ordinary links.
- Nothing is fetched ahead. Each day is a full page load.

### Closet page

- **Shirts:** one grid per Closet, Home then Office, three to a row,
  with a short last row centered. Each tile shows the Shirt's art, its
  Label and its due text.
- **Due text** comes from the existing next-due lookup and is
  formatted by the web shell: "Today", "Tomorrow", the weekday name
  for a date within the next six days, otherwise "Mon 26 Oct". A Shirt
  no day within the horizon wears says "Not due this year". Only
  "Today" is red.
- **The rest of the Wardrobe** in smaller grids, four to a row, one
  per kind and never combined: Pants (shared, so once), Home sweaters,
  Home jackets, Home shoes, Office sweaters, Office shoes. Each tile
  shows the art and the Label.
- **The Shirt sheet** (a popover per Shirt, rendered into the page):
  the art and name, a "Next due <when> ›" link to that Day page, the
  Shirt's Outfit on that date under "Worn with" (Pants, shoes, then
  any Outerwear, with no-forecast Outerwear in its own "If it's cold"
  section, as on the Day page), "Swap with" as submit tiles for the
  Shirts sharing its Pants (the existing swap POST), and "Replace this
  Shirt". A Shirt with no partner says it can't Swap because no other
  Shirt shares its Pants. A Shirt never due shows no Outfit and no
  "Next due" link. The sheet's Outfit is answered without a forecast,
  so its Outerwear is always under "If it's cold" and the Closet never
  waits on fetching one: a fetch on every load made the page slow.
- **The Replace sheet** (a popover per Garment): the art large, then
  Name, Color, Striped and its stripe Color, and a "Replace the
  <kind>" submit. It posts to the existing Replace route with the
  existing fields. The page script redraws the art as the Colors
  change, which means it needs the art for any Color client-side. The
  server embeds each Garment's layer template, its paths with
  placeholder colors, and the script recomputes the tone, using the
  same luminance rule, and the button color. The rule is small enough
  to keep in two places. A server test pins the Python side, and the
  manual check pins the script side.
- **The separate Garment page goes.** Nothing links to `GET
  /closet/<key>` once Replace is a sheet, so the route and its
  template are deleted. `POST /closet/<key>` stays. Its refusal (a
  `.` in the Label, or a Label already held) now re-renders the Closet
  page with a 422, the message as the notice, and that Garment's
  Replace sheet open and filled with what was posted. Opening it on
  load is the one thing that needs script, and without script the
  message still shows.

### Settings page

- **Two cards**, each its own POST form as today, under 22 pt heads:
  "Office Weekdays", then "Cold Threshold". Nothing else is on the
  page.
- **Office Weekdays:** seven checkboxes styled as round chips, M T W T
  F S S. Checked means Office, filled in the label color, and
  unchecked means Home, outlined. They post the same `weekday` fields
  as today. Under the card: "Changing these keeps every Rotation where
  it is."
- **Cold Threshold:** a stepper (− value +) over the same `threshold`
  field, one whole degree per tap, clamped 0–100. A stored decimal is
  shown rounded, and Save posts the whole degree.
- **Save capsules:** with script, hidden until the card differs from
  how it loaded. For the weekdays, Save is enabled only at exactly
  three, with a footnote counting down ("Pick 1 more", "Pick 2 more",
  "Untick 1"). Without script, both Saves always show and the server
  refuses as it does today.
- **The server enforces the limits.** `set_cold_threshold` in core
  refuses a threshold below 0, above 100, or not a whole number, with
  a `What2wearError` whose message the page shows. The refusal lives
  in core because refusal messages live in core (Phone spec) and
  "whole degrees from 0 to 100" is already in `CONTEXT.md`. The web
  shell's parse still answers 400 for text that isn't a number.
- **An existing decimal in the State** is left alone until the wearer
  saves. Reading it isn't refused, only setting it.

### Notices

- On every page the notice (or a refusal's message) is a small capsule
  toast at the top, under the segmented control. With script it fades
  after a few seconds, and the script strips `notice` from the URL
  with `history.replaceState`, so a reload doesn't show it again.
  Without script it stays put, as today.

### Widget JSON contract (changed)

```json
{"date": "2026-10-12", "day": "office",
 "outfit": [
   {"garment": "shirt", "label": "Light Blue",
    "art": [{"d": "M…Z", "fill": "#000000", "alpha": 0.22},
            {"d": "M…Z", "fill": "#9cc3e6"},
            {"d": "M…", "stroke": "#5a7185", "width": 2}, …]},
   {"garment": "pants", "label": "Khaki", "art": […]},
   {"garment": "shoes", "label": "White", "art": […]},
   {"garment": "sweater", "label": "Grey", "if_cold": true, "art": […]}]}
```

- Items are in the new order: Shirt, Pants, shoes, then Outerwear.
- `icon` (shape / pattern / detail) is replaced by `art`, the layer
  list in the 76-unit box, the same layers the pages draw.
- `label` stays the bare Label, and the widget no longer appends the
  kind.
- `if_cold` is present only when the forecast is unknown, as today.

### Scriptable widget

- **The header** is one line in 13 pt semibold rounded: the Day word
  bold ("Office" / "Home") and the short date grey ("Mon 12"). A stale
  cached date turns orange with ⚠︎. The failure messages ("⚠︎ State
  won't read", "⚠︎ Renew PythonAnywhere?", "⚠︎ Can't reach server")
  replace the line, as today.
- **Rows** share the height under the header. An Outfit is a Shirt,
  Pants and shoes, with at most one piece of Outerwear, so there are
  3 rows or 4. With 3 the art is 34 pt and the label 17 pt, and with 4
  the art is 27 pt and the label 16 pt, semibold rounded. Columns line up through fixed-size art stacks and fixed
  spacers, because stacks ignore text alignment.
- **"if cold"** rows draw art and label at 40% alpha, with a small
  grey "if cold" at the right.
- **The drawing:** the path parser gains `C` (`addCurve`). Each layer
  is filled or stroked with its color and alpha. Stroke widths scale
  with the box. The widget no longer has its own detail stroke
  constant.
- **The background** follows light and dark through `Color.dynamic`
  (`#ffffff` / `#1c1c1e`). The art can't, which is why the tone rule
  lightens dark Colors.
- Design for a 158 pt tile, with 16 pt margins (11 pt where tight).
- Caching, the tap URL and the failure handling are unchanged from the
  Phone spec.

### Docs

- **New ADR, "The pages may use JS, but every day is a URL and every
  write a form":** reverses the Phone spec's no-JS rule, and records
  that script only enhances the pages: no client-side routing, no
  fetched days, no JSON writes.
- **README:** re-paste the widget after deploying, because the JSON's
  `icon` became `art`.
- `CONTEXT.md` already has the Shirt cuts and the Cold Threshold's
  limits, so it needs nothing new.

## Testing Decisions

- **Seams: the existing two, no new ones.** The Flask `test_client()`
  on `web.app(state_path, token, fetch_weather=…)` is the main one,
  and core's public functions cover the Cold Threshold refusal. No
  browser tests are added. That's why every page has to work without
  script: the server-rendered HTML is the contract the tests can hold.
- **Test external behavior only.** Web tests assert on status codes,
  redirects, the notice, rendered text, the forms and links present,
  the JSON and the State on disk. They never assert on templates,
  CSS, helpers or exact markup beyond what the wearer acts on (a form's
  action, a link's URL, a field's value, an SVG path's colors).
- **Prior art:** `tests/test_web.py` for the web seam (fixtures
  `client`/`state_path`, weather stubbed with `dict` or a fixed
  mapping), and `tests/test_outerwear.py` for `set_cold_threshold`.
  Existing tests that pin removed things (the ‹ prev / next › links,
  the `<select>` of Shirts, the Garment page's GET, the ", if it's
  cold" suffix, the `icon` JSON, the date in the title) are rewritten
  to the new behavior, not deleted without replacement.
- **Core (`test_outerwear` or wherever the threshold is tested):**
  - 0 and 100 are accepted, and −1, 101 and 52.5 are refused with a
    message.
  - A refused threshold moves nothing.
  - `get_day_type` agrees with `answer(...).day_type` for an Override,
    a Holiday and a plain weekday.
- **Web, the Day page:**
  - The title names the Day.
  - The week strip holds the seven dates of the shown date's Week, each
    linking to its Day page and each marked O or H by its Day,
    including a Day Type Override.
  - The Outfit reads Shirt, Pants, shoes, then Outerwear, in that order
    in the page.
  - With no forecast, the Outerwear is under "If it's cold" with "no
    forecast yet". On a cold day it's a plain row, and on a warm day
    it's absent.
  - "Today" is present on another date and absent on today.
  - The "⋯" actions post to the same routes as before. "Wear a
    different shirt" offers that Closet's Shirts as submit buttons,
    with the current one marked.
  - The past-date and unavoidable-repeat notes still show.
- **Web, the art (through the Day page SVG and the JSON):**
  - An Office Shirt's art differs from a Home Shirt's for the same
    Color (the Shirt cut follows the Closet).
  - Every path uses only `M L Q C Z`, and every layer has exactly one
    of fill/stroke.
  - A striped Garment carries layers in its stripe Color.
  - A light Color's outline is darker than its fill, and a Color below
    the luminance cutoff (the given Black) gets an outline lighter than
    its fill.
  - The page's SVG and the JSON's `art` carry the same layers for the
    same Garment.
- **Web, the JSON:** the new order, `art` in place of `icon`, the bare
  `label`, `if_cold` only when unknown, and errors unchanged.
- **Web, the Closet page:**
  - Home Shirts come before Office Shirts.
  - Each Shirt shows its due text ("Today" / "Tomorrow" / weekday /
    "Mon 26 Oct", checked against `get_due_date` with a pinned today)
    and links to its due Day.
  - Each Shirt's sheet holds its Outfit on that date.
  - Swap offers only Shirts sharing Pants, and a Shirt with none says
    so.
  - Every Garment (the shared Pants once, each kind's grid) has a
    Replace form prefilled with its Label and Colors, and a striped
    one has Striped ticked.
  - A refused Replace answers 422 with the message, the Closet page
    and that form filled with what was posted.
  - `GET /closet/<key>` is gone (404).
- **Web, Settings:** checked chips for the current Office Weekdays.
  The threshold is shown rounded (a State holding 52.5 shows 53). A
  threshold of 101 or 52.5 is refused with the message and writes
  nothing. A whole threshold saves.
- **Web, unchanged guarantees** stay covered: a wrong token is a 404,
  every response is `no-store`, a fresh install writes nothing, the
  State is written only on change, recorded vs already in the notice,
  and the unreadable State is a 500.
- **Manual check on the phone, after deploy** (no automated test):
  light and dark mode on each page; swiping a day and a week, the
  spring-back, the edge gesture, and back leaving the Day page; the
  rows fitting on a day with no forecast (four rows and the "If it's
  cold" heading) on the smallest supported iPhone; the
  "⋯" popover and the Shirt sheet; the Closet sheets and the live
  redraw in Replace; the Settings Save capsule and countdown; the
  toast fading and not returning on reload; the widget at 3, 4 and 5
  rows, a striped Shirt, Black on the dark widget, airplane mode
  (cached, ⚠︎ date) and a wrong token.

## Out of Scope

- A native iOS app, or any change to the hosting, the token or the
  State's shape.
- A medium or large widget, widget buttons, and prefetching tomorrow.
- Photos of real Garments, and server-rendered PNG art.
- Fetching neighboring days ahead, a carousel of rendered days, and
  client-side routing or JSON writes.
- Anything on Settings beyond the Office Weekdays and the Cold
  Threshold: the widget URL, About, Holidays.
- Browser automation tests.
- Gradients, gloss, blur or clipping in the art itself.

## Further Notes

- The throwaway prototype branches are the visual reference and should
  be read, not merged: `prototype/the-look` (`?variant=B`),
  `prototype/the-garment-art` (`?art=A`), `prototype/the-day-page`
  (`?v=C`), `prototype/swiping-between-days` (`?v=D`, the Day page to
  build), `prototype/the-closet-page` (`?v=A`), and
  `prototype/the-widget` (`?v=O`, whose `prototype_art.py` has the
  silhouettes, the stripe cutting, the tone rule and the 76-unit
  placement, and whose `widget_prototype.js` has the DrawContext
  drawing). Research on what Scriptable can draw is on
  `research/what-scriptable-can-draw`.
- Not yet checked on a phone: how small the art gets on a four-row Day
  page with the "If it's cold" heading on the smallest iPhones, and the widget prototype in Scriptable
  itself. Both are in the manual check.
- Deploying the server before re-pasting the widget leaves the old
  widget without `icon`. It will draw labels with no art, or fall back
  to its cache, until the new script is pasted. Do both in the same
  sitting.
- The `popover` attribute needs iOS 17 or later. Older phones fall
  back to the forms being reachable only with script.
