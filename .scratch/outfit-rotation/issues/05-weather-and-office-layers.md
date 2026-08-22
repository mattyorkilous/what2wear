# 05 — Weather and office Outerwear

**What to build:** Outfits gain outerwear when the day is cold. This ticket covers the office half, which has no alternation — below the threshold you wear the sweater the pants map to, and that's the whole rule.

It also establishes how the tool behaves when it doesn't know the weather, which matters more than the happy path. Everything except the temperature is purely derived and knowable for any date — including *which* Outerwear the date calls for. So a date past the forecast horizon, or a lookup that fails, returns the Shirt, pants, shoes and the named Outerwear garment, hedging only the condition: "that sweater, if it's cold." A user must be able to tell "no Outerwear needed" apart from "can't say yet", and a network problem must never stop the tool answering the question it can answer.

Note this is narrower than it once was. An earlier draft marked the whole Outerwear unknown, conflating which garment with whether to wear it; those are separate questions and only the second depends on the forecast.

Forecasts come from a provider needing no API key, for fixed coordinates, against a configurable temperature threshold defaulting to 50°F.

**Blocked by:** 02 — Sweaters, shoes, and the office Week Fallback

**Status:** superseded — do not build

Re-cut under `.scratch/given-wardrobe/spec.md`. The behavior described
here is still wanted, but it is specified against the hand-authored
config file and the append-only decision log, both of which are gone.

- [ ] Below the threshold, an Office Day Outfit includes the pants-mapped sweater as its Outerwear
- [ ] At or above the threshold, no Outerwear is included
- [ ] The threshold is configurable
- [ ] Forecasts are fetched for fixed coordinates from a provider requiring no API key or stored secret
- [ ] A date beyond the forecast horizon returns Shirt, pants, shoes and the named Outerwear garment, with only the cold/warm condition unresolved
- [ ] A failed or unavailable forecast degrades identically to being beyond the horizon, never to an error
- [ ] "No Outerwear needed" and "this Outerwear, if it's cold" are distinguishable in the output
- [ ] Weather enters the pure entry point as an argument — a mapping of date to daily high — so the core stays free of network access
- [ ] Tests cover the cold case, the warm case, the beyond-horizon case and the lookup-failure case without touching the network
