# 05 — Swiping between days

Type: prototype
Status: resolved
Blocked by: 04

## Question

How does swiping left and right move between days?

A snapping carousel of rendered days or a gesture that loads the next
day's URL; whether neighbouring days are fetched ahead; how the URL and
the back button follow the swipe; and what replaces ‹ prev / next ›.

## Comments

- From **The Day page**: the Day page is a list with a floating bottom
  toolbar holding ‹, the date (opens the date picker) and ›, beside a
  "⋯" menu. Swiping supplements or replaces that toolbar's ‹ ›. See
  `prototype/the-day-page`, `?v=C`.

## Answer

**D — a week strip, with the rows fitting the screen**, chosen over
drag-then-load with ‹ › kept (A), a carousel of fetched days (B), the
week strip alone (C), and the week strip with Pants and shoes paired
(E). C was the favourite, but it couldn't show a whole Outfit with a
sweater on one screen. D keeps C and fixes that.

The prototype is on the throwaway branch `prototype/swiping-between-days`
(`src/what2wear/templates/day.html`, run with
`uv run python prototype_swiping_between_days.py`), showing D with `?v=D`.

What swiping is, as prototyped:

- **The week strip replaces ‹ ›.** It's a Mon–Sun row above the title:
  weekday letter, day number, and O/H for the Day under each. The
  shown day is filled and today is in red. Tapping a day goes to it.
- **The gesture:** a horizontal swipe on the page moves a day. A swipe
  on the strip moves a week. The page follows the finger and commits
  past a quarter of the screen width. It then slides off and the new
  day's URL loads, sliding in from the side the swipe came from.
  Otherwise it springs back. Vertical scrolling still works. Swipes
  that start within 24 px of either edge are left to Safari's own
  back/forward gesture.
- **Each day stays its own URL, loaded as a full page.** Nothing is
  fetched ahead. Swiping and tapping the strip *replace* the history
  entry, so back leaves the Day page instead of walking back through
  days.
- **The toolbar** is now the date (tap opens the date picker),
  "Today" (hidden on today) and "⋯".
- **The rows fit the screen.** The Outfit's rows share the height
  between the strip and the toolbar, the "If it's cold" section
  included. The Shirt's row is a little taller, and the art scales
  with its row (up to 150 pt). So 3, 4 or 5 Garments all fit with no
  scrolling, and a short Outfit no longer stops partway down. That
  settles what **The Day page** left open.
- **Outerwear goes last:** Shirt, Pants, shoes, then the sweater or
  jacket. It's the least essential part of the Outfit. This changes
  **The Day page**'s top-to-bottom order.

Not checked on a phone: how small the art gets on a five-row day
(no-forecast Outerwear) on the smallest iPhones.
