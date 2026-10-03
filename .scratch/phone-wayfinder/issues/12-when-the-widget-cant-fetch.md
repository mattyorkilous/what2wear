# 12 — When the widget can't fetch

Type: grilling
Status: resolved
Blocked by: 09

## Question

The widget reads `/<token>/day/YYYY-MM-DD.json` (see
[The web shell on PythonAnywhere](08-the-web-shell.md)). What does it
show when:

- there's no network
- the server answers `{"error": "…"}` with a 500 (the State won't read)
- the web app has lapsed after a missed monthly renewal (PythonAnywhere
  serves its own page, not JSON)

Options include keeping the last good Outfit with a stale marker,
showing the error text, or a blank widget. Should a lapsed server
remind you to renew?

## Answer

**The widget shows the last good Outfit it has, and uses the header
line to say when something is wrong.** Settled by grilling on
2026-09-27.

- **Cache:** after each good fetch the widget saves the JSON to
  `FileManager.local()`. Whatever the failure, it draws from that copy.
- **Stale marker:** only when the cached date isn't today. The header
  date then turns a warning colour and gets a ⚠︎. A cached copy of
  today is shown plainly.
- **No network:** the cached Outfit and the stale marker, with no
  message. It fixes itself.
- **500 with `{"error": …}`:** the cached Outfit, and the header line
  becomes "⚠︎ State won't read". The error text is too long for a small
  tile. Tapping the widget opens the Day page, which shows the full
  message.
- **Non-JSON answer** (a lapsed web app, a wrong token's 404, or any
  page from PythonAnywhere): the cached Outfit, and the header becomes
  "⚠︎ Renew PythonAnywhere?". This is the renewal reminder, alongside
  PythonAnywhere's own expiry emails. The question mark is there because
  a wrong token looks the same. The widget never parses PythonAnywhere's
  HTML.
- **No cache yet:** the header message alone ("⚠︎ Can't reach server"
  when offline), with no placeholder Outfit.
- **No prefetch of tomorrow.** iOS refreshes widgets several times a
  day, and the stale marker covers the gap. Revisit if stale mornings
  actually happen.
