# 05 — Weather and office Layers

**What to build:** Outfits gain a Layer when the day is cold. This ticket covers the office half, which has no alternation — below the threshold you wear the sweater the pants map to, and that's the whole rule.

It also establishes how the tool behaves when it doesn't know the weather, which matters more than the happy path. Dates past the forecast horizon, and forecast lookups that fail or are unavailable, must still return the Shirt, pants and shoes — all of which are purely derived and knowable for any date — with the Layer marked explicitly as unknown. A user must be able to tell "no Layer needed" apart from "can't say yet", and a network problem must never stop the tool answering the question it can answer.

Forecasts come from a provider needing no API key, for fixed coordinates, against a configurable temperature threshold defaulting to 50°F.

**Blocked by:** 02 — Sweaters, shoes, and the office Week Fallback

**Status:** ready-for-agent

- [ ] Below the threshold, an Office Day Outfit includes the pants-mapped sweater as its Layer
- [ ] At or above the threshold, no Layer is included
- [ ] The threshold is configurable
- [ ] Forecasts are fetched for fixed coordinates from a provider requiring no API key or stored secret
- [ ] A date beyond the forecast horizon returns Shirt, pants and shoes with the Layer marked unknown
- [ ] A failed or unavailable forecast degrades identically to being beyond the horizon, never to an error
- [ ] "No Layer needed" and "Layer unknown" are distinguishable in the output
- [ ] Weather enters the pure entry point as an argument — a mapping of date to daily high — so the core stays free of network access
- [ ] Tests cover the cold case, the warm case, the beyond-horizon case and the lookup-failure case without touching the network
