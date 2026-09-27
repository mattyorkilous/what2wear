# 12 — When the widget can't fetch

Type: grilling
Status: open
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
