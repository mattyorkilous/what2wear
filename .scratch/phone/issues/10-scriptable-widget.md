# 10 — Scriptable widget

**What to build:** A small Home Screen widget showing today's Outfit,
drawn from the JSON endpoint, that keeps showing the last good Outfit
when it can't fetch. The script lives in the repo and is pasted into
Scriptable. See `.scratch/phone/spec.md`.

**Blocked by:** 09 — Widget JSON endpoint.

**Status:** ready-for-agent (the install and check on the phone are
HITL)

- [ ] Host and token are constants at the top of the script
- [ ] Fetches the phone's own date; header is 🏢 Office / 🏠 Home and a
      short date ("Mon 28")
- [ ] Draws icons with `DrawContext` from the paths (`M`/`L`/`Q`/`Z` →
      `move`/`addLine`/`addQuadCurve`/`closeSubpath`), scaling 32×32,
      with the full name beside each; system font
- [ ] Detail stroke translucent white, width 1.2; an `if_cold` row
      dimmed
- [ ] Tapping opens the Day page
- [ ] Caches every good response in `FileManager.local()` and draws
      from it on any failure
- [ ] ⚠︎ and a warning colour on the date only when the cached date
      isn't today
- [ ] `{"error"}` 500 → header "⚠︎ State won't read"; any non-JSON
      answer → "⚠︎ Renew PythonAnywhere?"; no cache → the message alone
- [ ] README says how to install the script and add the widget
- [ ] Checked by hand: a normal tile, a dimmed row, a striped Shirt,
      airplane mode, a wrong token
