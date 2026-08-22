# 05 — Weather and office Outerwear

**What to build:** Outfits gain Outerwear when the day is cold. This
ticket covers the office half, which has no alternation — below the
threshold you wear the sweater the Pants map to, and that is the whole
rule.

The value is in what happens when the weather isn't known, which matters
more than the happy path. Everything except the temperature is derived
and knowable for any date, *including which* Outerwear the date calls
for. So a date past the forecast horizon, or a lookup that fails, returns
the Shirt, its Pants, its shoes and the named Outerwear garment, hedging
only the condition: "that sweater, if it's cold." The wearer must be able
to tell "no Outerwear needed" from "can't say yet", and a network problem
must never stop the tool answering the question it can answer.

Re-cut from the superseded `.scratch/outfit-rotation/issues/05`, which
specified the same behavior against the old seam.

**Blocked by:** 03 — One State file and the two seams

**Status:** ready-for-agent

- [ ] On a cold Office Day the Outfit names the sweater the Pants map to
- [ ] At or above the threshold no Outerwear is named at all
- [ ] The Response distinguishes three states — worn, not worn, and named-but-conditional
- [ ] A date beyond the forecast horizon returns Shirt, Pants, shoes and the named garment with only the cold/warm condition open
- [ ] A failed or unavailable forecast degrades identically to being beyond the horizon, never to an error
- [ ] Weather enters the answering seam as an argument — a mapping of date to daily high — so the core touches no network
- [ ] Forecasts come from a provider needing no API key or stored secret, for coordinates given in source
- [ ] The temperature threshold is given in source and is not settable at runtime
- [ ] The forecast endpoint only; no historical archive is called, for any date
- [ ] Tests cover cold, warm, beyond-horizon and lookup-failure without touching the network
- [ ] The README describes Outerwear as it now behaves
