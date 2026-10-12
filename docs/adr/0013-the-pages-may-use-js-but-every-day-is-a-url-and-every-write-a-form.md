# The pages may use JS, but every day is a URL and every write a form

The pages may carry script. The Day page follows the finger when it is
swiped to the next day or Week, notices fade and leave the URL, and
later pages will show and hide their Save buttons and redraw the art as
a Color changes. This reverses the Phone spec's "No JS on the pages".

Script only enhances a page that already works without it. Each page is
rendered whole on the server: the Outfit shows, every day is its own
`GET /day/YYYY-MM-DD`, and every write is a plain POST form answered
with a `303` and `?notice=<text>`. Menus and sheets use the HTML
`popover` attribute, so they open without script, and their forms are
in the page from the start. A swipe or a tap on the week strip loads
the next day's URL whole, with `location.replace` so back leaves the
Day page; it doesn't fetch the day and draw it in place.

What2wear is a Home Screen web app that should feel like an iOS app,
and following the finger, a fading toast and a stepper are what that
takes. Keeping the server-rendered page as the whole contract is what
lets the suite test the pages without a browser, through Flask's test
client alone: what the tests can hold is the HTML, so the HTML has to
be enough. It also means a slow or broken script never stops the wearer
getting dressed.

## Consequences

- **No client-side routing, no fetched days, no JSON writes.** A
  carousel of days fetched ahead was prototyped and turned down: the
  day's URL, the history entry and the page would all have to be kept
  in step by script.
- **The script is inline in the base layout**, hand-written, with no
  build step and no dependency. Every Flask URL starts with the token,
  so a static file would need one too.
- **Anything only script can do is a nicety.** Without script the
  toast stays put, the date picker needs its Go button, and the strip
  days are ordinary links that add history entries.
- **The script's behavior is checked by hand on the phone**, never by
  the suite. A test asserts on the forms, links and text the script
  works from, never on the script itself.
