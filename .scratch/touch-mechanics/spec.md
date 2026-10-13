# Touch mechanics

Status: ready-for-agent

Changes how the pages answer the finger. It refines the swiping settled
in [the redesign wayfinder's "Swiping between days"](../redesign-wayfinder/issues/05-swiping-between-days.md)
and the [Redesign spec](../redesign/spec.md), whose decisions stand
unless this one reverses them. Governed by ADR-0013: every day is still
a URL loaded whole, and the script only enhances a page that works
without it.

## Problem Statement

Three things about how the pages respond to touch feel wrong on the
phone.

On the Day page, a sideways drag on the Outfit drags the whole page —
the week strip included — so the strip seems to move with the day,
though a drag on the strip moves only the strip. The strip ought to stay
put while the days change under it.

On the Closet page, a Garment's sheet can be closed only by tapping
outside it. The sheet has a grabber bar at its top, as an iOS sheet
does, but it can't be pulled down the way an iOS sheet can.

Tapping "Closet" in the segment bar takes a moment to answer, and in
that moment nothing changes: the highlight stays on the old segment and
the old page stays on screen. It feels as if the tap missed, so the
wearer taps again. The page is already compressed on the way out, so
the delay is the server's round trip, not the size of the page.

## Solution

On the Day page, a sideways drag means one thing per place it starts:

- On the **Outfit** — any of its rows, the "If it's cold" heading, and
  the gaps between them — it moves a day, and only the Outfit follows
  the finger. The strip and the title stay still.
- On the **week strip** it moves a Week, as now.
- **Anywhere else** — the title, the captions, the toolbar — it does
  nothing.

There is no swiping between pages, on the Day page or anywhere else.
The pages are changed only by tapping the segment bar, and that tap now
answers at once: the highlight moves to the tapped segment and the page
is replaced by the new page's title alone, until the new page arrives
and takes its place.

Every sheet can be pulled down to close. It follows the finger, and
closes when let go far enough down or flicked; otherwise it springs
back.

## User Stories

1. As the wearer, I want a sideways drag on the Outfit to move to the
   next or previous day, so that I can look through the coming days
   with the biggest target on the page.
2. As the wearer, I want only the Outfit to follow my finger while I
   drag it, so that the week strip stays still and I can see which day
   I'm heading to.
3. As the wearer, I want the "Home Day" or "Office Day" title to stay
   still while I drag the Outfit, so that only the thing I'm dragging
   moves.
4. As the wearer, I want a drag that starts on the "If it's cold"
   heading or its rows to move a day like the rest of the Outfit, so
   that the whole Outfit is one target.
5. As the wearer, I want a drag that starts in the gap between two
   Outfit rows to move a day, so that I don't have to aim for a row.
6. As the wearer, I want the next day's Outfit to slide in from the
   side I swiped toward, so that the change of day reads as the
   continuation of my swipe.
7. As the wearer, I want only the Outfit to slide in on the new day,
   with the strip and the title simply showing the new day, so that the
   page doesn't seem to jump.
8. As the wearer, I want a drag that isn't past a quarter of the screen
   to spring back, so that a small or accidental drag doesn't change the
   day.
9. As the wearer, I want a drag on the week strip to keep moving a whole
   Week, with only the strip following my finger, so that I can jump
   ahead quickly.
10. As the wearer, I want a sideways drag that starts on the title, the
    captions or the toolbar to do nothing, so that a swipe never does
    something I didn't aim for.
11. As the wearer, I want vertical drags on the Day page to keep working
    as they do, so that nothing about swiping gets in the way of
    scrolling.
12. As the wearer, I want swipes that start at the very edges of the
    screen to be left alone, so that the system's own edge gestures
    still work.
13. As the wearer, I want swiping between days to leave my history as it
    does now, so that back still leaves the Day page rather than walking
    back through every day I swiped past.
14. As the wearer, I want a sideways drag on the Closet or Settings
    page to do nothing, so that the pages behave the same as the Day
    page's non-Outfit parts.
15. As the wearer, I want the segment I tap to show as selected the
    moment I lift my finger, so that I know my tap landed and don't tap
    again.
16. As the wearer, I want the page to switch to the tapped page's title
    at once, even before its art has loaded, so that the app feels like
    it moved instantly.
17. As the wearer, I want tapping "Day" from the Closet or Settings to
    show today's real title ("Home Day" or "Office Day") straight away,
    so that the placeholder matches the page I land on.
18. As the wearer, I want the full page to replace the placeholder as
    soon as it arrives, so that I never have to do anything more to see
    it.
19. As the wearer, I want tapping the segment I'm already on to do
    nothing, so that it doesn't blank and reload the page.
20. As the wearer, I want a touch on the segment bar that turns into a
    scroll not to move the highlight, so that it doesn't flicker.
21. As the wearer, I want a page I return to with back or forward to
    show itself and its own highlighted segment, not a leftover
    placeholder, so that going back is never broken.
22. As the wearer, I want the segment bar to keep working as ordinary
    links when script hasn't run, so that the app still gets me dressed
    if the script is slow or broken.
23. As the wearer, I want to pull a Shirt's sheet on the Closet page down
    to close it, so that I can dismiss it the way I would on iOS.
24. As the wearer, I want to pull a Replace sheet down to close it, so
    that every sheet closes the same way.
25. As the wearer, I want to pull the Day page's "Wear a different
    shirt" sheet down to close it, so that sheets close the same way on
    every page.
26. As the wearer, I want a sheet to follow my finger as I pull it down,
    so that I can see it's about to close.
27. As the wearer, I want a sheet I let go of past about a quarter of its
    height to close, so that I don't have to drag it all the way off.
28. As the wearer, I want a quick flick down to close a sheet even if it
    went only a little way, so that closing is fast.
29. As the wearer, I want a sheet I let go of only a little way down to
    spring back, so that a small pull doesn't close it.
30. As the wearer, I want a pull down on a sheet that's scrolled partway
    to scroll it back up rather than close it, so that a long sheet
    stays readable.
31. As the wearer, I want a pull down that starts anywhere on a sheet —
    its art, its rows, its fields — to close it once it's scrolled to
    the top, so that I don't have to aim for the grabber.
32. As the wearer, I want pulling down a Replace sheet that I opened from
    a Shirt's sheet to bring me back to that Shirt's sheet, so that I
    retrace the step I took.
33. As the wearer, I want a Replace sheet pulled closed to forget its
    unsaved edits, as tapping outside it does now, so that closing a
    sheet never writes anything.
34. As the wearer, I want tapping outside a sheet to still close it, so
    that the old way keeps working.
35. As the wearer, I want the "⋯" menu to stay as it is, so that a small
    menu doesn't move under my thumb.

## Implementation Decisions

- **The Outfit is one block on the Day page.** Its worn rows, the "If
  it's cold" heading and that section's rows sit inside a single
  element. The week strip, the title and the captions sit outside it.
  The rows keep sharing the height between the strip and the toolbar,
  as the Redesign settled, the "If it's cold" section included.
- **The day swipe listens on the Outfit block, and moves only it.** A
  drag that starts inside the block moves a day; one that starts on the
  strip moves a Week and moves only the strip; one that starts anywhere
  else on the page is ignored. The rest of the gesture is unchanged:
  the axis is chosen after a small slop, it commits past a quarter of
  the screen width, swipes starting within 24 px of either edge are
  ignored, a drag never fires a tap, and no swipe starts while a popover
  is open.
- **The new day's slide-in is the Outfit's alone.** The hand-over that
  tells the next page which side the swipe came from now animates only
  the Outfit block. The strip and title render in place.
- **Swiping still loads each day whole.** The day's URL is loaded with
  `location.replace`, nothing is fetched ahead, and back leaves the Day
  page — all as ADR-0013 says.
- **There are no page swipes.** Closet and Settings get no horizontal
  gesture. Swiping between pages and days by where the finger lands was
  weighed and turned down: the regions would be invisible, the
  page-swipe region on the Day page would be the thin band around the
  title, and a segmented control is tapped, not swiped.
- **Each segment link carries the title of the page it opens.** The
  Closet's is "Closet" and Settings' is "Settings". The Day segment's is
  today's real title, "Home Day" or "Office Day", which means every
  page works out today's Day Type to render the segment bar. The links
  stay ordinary links to the same URLs.
- **A segment tap switches at once.** On the tap — the click, not the
  touch-down, so a touch that turns into a scroll doesn't flicker — the
  script moves the current-page mark to the tapped segment, replaces
  the page's main content with the carried title alone, and lets the
  link navigate as it would without script. Tapping the current
  segment does nothing. A page restored from the back-forward cache
  undoes the placeholder and puts the mark back on its own segment.
  Modified clicks (to open in a new tab and the like) are left to the
  browser.
- **Every sheet can be pulled down to close.** That's every `.sheet`
  popover: the Closet's Shirt sheets, each Replace sheet, and the Day
  page's "Wear a different shirt". The "⋯" menu is not a sheet and
  doesn't take part. A downward drag that starts anywhere on a sheet
  scrolled to its top moves the sheet with the finger; past a quarter of
  its height, or on a fast downward flick, it closes with
  `hidePopover`; otherwise it springs back. When the sheet is scrolled
  partway, the drag scrolls it as now. Upward drags are left to
  scrolling.
- **Closing a nested sheet uncovers its parent.** A Replace sheet opened
  from a Shirt's sheet is that sheet's child popover, so closing it
  leaves the Shirt's sheet open.
- **Closing writes nothing.** A pulled-closed Replace sheet discards its
  unsaved fields exactly as a light dismiss does.
- **All of it stays in the inline script of the base layout**, by hand,
  with no dependency or build step, as ADR-0013 requires.

## Testing Decisions

- A good test drives the app through Flask's test client and asserts on
  the HTML the script works from — the elements, links and attributes —
  never on the script itself. ADR-0013 puts the script's behaviour
  outside the suite; it is checked by hand on the phone.
- The web module's tests cover:
  - every Outfit row on the Day page, the "If it's cold" heading and
    its rows included, is inside one Outfit block, and the week strip
    and title are not;
  - each segment link carries its page's title: "Closet", "Settings",
    and for Day today's title, "Home Day" on a Home Day and "Office Day"
    on an Office Day — checked from the Closet and Settings pages as
    well as the Day page, and against a Day Type Override for today;
  - the segment links still go to the same URLs, so the bar works
    without script.
- Prior art: the existing web tests that read the week strip out of a
  Day page, check that every page links to Day, Closet and Settings,
  and check the title is the day.
- To check by hand on the phone: day swipes from each part of the
  Outfit, Week swipes on the strip, dead swipes on the title, captions,
  toolbar, Closet and Settings; the instant segment switch and a back
  to a switched-away page; pulling down each kind of sheet, flicking
  one, pulling a scrolled one, and pulling a Replace sheet opened from a
  Shirt's sheet. How a sheet's pull feels against its form fields
  should be checked especially.

## Out of Scope

- **Making the Closet load faster.** The delay is the server's round
  trip, which the instant switch hides. PythonAnywhere already
  compresses the page, so compressing it here would do nothing.
- **Fetching pages ahead or drawing them in place.** ADR-0013 rules it
  out.
- **Swiping between pages.** Turned down above.
- **Changing the "⋯" menu's behaviour.**
- **Any change to the domain or `CONTEXT.md`.** These are behaviours of
  the pages, not of the Wardrobe or its Rotations.

## Further Notes

- The redesign wayfinder's "Swiping between days" said a horizontal
  swipe *on the page* moves a day. This narrows it to the Outfit, and
  makes the rest of the page dead to sideways swipes.
- Whether a pulled sheet's drag should start inside a focused text field
  is left to the hand check: if pulling from the Name field fights the
  cursor, drags that start in a focused field may be left to it.
