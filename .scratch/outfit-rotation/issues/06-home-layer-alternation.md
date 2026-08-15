# 06 — Home Layer alternation

**What to build:** The home half of the Layer rule, which unlike the office half carries state. On a cold Home Day you wear a jacket if the last home Layer you wore was a sweater, and a sweater if it was a jacket. Warm days are skipped over entirely rather than resetting the alternation — a mild day between two cold ones must not put you back in the same kind of Layer you just wore. Office sweaters are never consulted and never recorded here; the two settings alternate independently.

This ticket introduces the separate append-only Layer log. Per ADR-0002 this is the one stored cursor in a system that otherwise derives everything from the calendar, and the exception is deliberate: the alternation has to flip once per cold Home Day, and past weather is not reconstructable from configuration the way the calendar is.

The accepted cost is that the alternation does not advance on days the tool isn't run, so after a gap you may get the same kind of Layer twice running. That is expected behaviour, not a defect — it self-corrects the following day.

**Blocked by:** 05 — Weather and office Layers

**Status:** ready-for-agent

- [ ] Below the threshold, a Home Day Outfit includes a Layer of the opposite kind to the most recently recorded home Layer
- [ ] The jacket or sweater itself resolves from pants, as with every other garment
- [ ] Warm Home Days record nothing and leave the alternation untouched
- [ ] Office sweaters neither influence the alternation nor get recorded in the Layer log
- [ ] Resolved home Layers are appended to a log separate from the decision log
- [ ] Look-ahead simulates the alternation forward without recording anything
- [ ] Behaviour after a stretch with no recorded Layer is defined and tested, matching the limitation ADR-0002 accepts
- [ ] A sequence of cold, warm and office days is asserted end to end: jacket, then sweater, with an intervening warm day and an intervening Office Day proving neither disturbs the flip
