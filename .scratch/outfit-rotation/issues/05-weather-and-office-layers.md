# 05 — Weather and office Layers

**What to build:** Outfits gain a Layer when the day is cold. This ticket covers the office half, which has no alternation — below the threshold you wear the sweater the pants map to, and that's the whole rule.

It also establishes how the tool behaves when it doesn't know the weather, which matters more than the happy path. Everything except the temperature is purely derived and knowable for any date — including *which* Layer the date calls for. So a date past the forecast horizon, or a lookup that fails, returns the Shirt, pants, shoes and the named Layer garment, hedging only the condition: "that sweater, if it's cold." A user must be able to tell "no Layer needed" apart from "can't say yet", and a network problem must never stop the tool answering the question it can answer.

Note this is narrower than it once was. An earlier draft marked the whole Layer unknown, conflating which garment with whether to wear it; those are separate questions and only the second depends on the forecast.

Forecasts come from a provider needing no API key, for fixed coordinates, against a configurable temperature threshold defaulting to 50°F.

**Blocked by:** 02 — Sweaters, shoes, and the office Week Fallback

**Status:** ready-for-agent

- [ ] Below the threshold, an Office Day Outfit includes the pants-mapped sweater as its Layer
- [ ] At or above the threshold, no Layer is included
- [ ] The threshold is configurable
- [ ] Forecasts are fetched for fixed coordinates from a provider requiring no API key or stored secret
- [ ] A date beyond the forecast horizon returns Shirt, pants, shoes and the named Layer garment, with only the cold/warm condition unresolved
- [ ] A failed or unavailable forecast degrades identically to being beyond the horizon, never to an error
- [ ] "No Layer needed" and "this Layer, if it's cold" are distinguishable in the output
- [ ] Weather enters the pure entry point as an argument — a mapping of date to daily high — so the core stays free of network access
- [ ] Tests cover the cold case, the warm case, the beyond-horizon case and the lookup-failure case without touching the network
