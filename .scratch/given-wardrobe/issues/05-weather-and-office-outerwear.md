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

**Status:** done

- [x] On a cold Office Day the Outfit names the sweater the Pants map to
- [x] At or above the threshold no Outerwear is named at all
- [x] The Response distinguishes three states — worn, not worn, and named-but-conditional
- [x] A date beyond the forecast horizon returns Shirt, Pants, shoes and the named garment with only the cold/warm condition open
- [x] A failed or unavailable forecast degrades identically to being beyond the horizon, never to an error
- [x] Weather enters the answering seam as an argument — a mapping of date to daily high — so the core touches no network
- [x] Forecasts come from a provider needing no API key or stored secret, for coordinates given in source
- [x] The temperature threshold's starting value is given in source; 07 is what makes it settable, and nothing here should be shaped to prevent that
- [x] The forecast endpoint only; no historical archive is called, for any date
- [x] Tests cover cold, warm, beyond-horizon and lookup-failure without touching the network
- [x] The README describes Outerwear as it now behaves

## Comments

**The threshold applies at home too, to the row's sweater.** Leaving
home unconditioned would name a sweater on a 90°F Home Day while the
office named none, and `Response.cold` would mean different things per
Closet. 06 changes only *which* garment a Home Day names;
`_apply_weather` settles only *whether*, so it carries over unchanged.
The three `TestHomeOuterwear` cases and the README's "home outerwear
still names the pants row's sweater" are 06's to rewrite.

**Which sweater is weather-free.** The Week walk runs without weather
and the condition is applied afterwards, so a warm Monday still spends
its sweater for the Week. Anything else would let a later forecast
change an earlier-named garment, which is what the horizon hedge rules
out. Asserted in `test_a_warm_monday_does_not_free_its_sweater_for_the_week`.

**A warm day can still carry the repeat note.** On a fourth Office Day
the note "already worn this week -- no free sweater left" still prints
on a warm day, which has no sweater line. The shoes do repeat, since office sweaters and
shoes are one-to-one. Left alone.

**The threshold is read from `wardrobe.py` in `_apply_weather`.** 07
passes it in from the State, as it will for `DEFAULT_OFFICE_WEEKDAYS`.
