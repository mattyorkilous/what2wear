---
Status: superseded by ADR-0004
---

# The Home Layer alternation is a stored cursor

> Superseded by [ADR-0004](./0004-home-layers-alternate-on-the-calendar.md). The
> alternation now advances on every Home Day rather than every cold one, which
> makes it derivable and removes the cursor and its log entirely. The reasoning
> below is kept because it explains why the exception looked necessary.

Home Layers alternate: on a cold Home Day you wear a jacket if your last Home Layer was a sweater, and a sweater if it was a jacket. Warm days are skipped over rather than resetting the alternation. We record each resolved Home Layer in an append-only log and read the most recent entry, rather than deriving the alternation from history as ADR-0001 requires of Positions.

This is a knowing exception. The alternation has to flip once per *cold* Home Day, so reconstructing it across a gap requires knowing which past days were below the threshold — and unlike the calendar, past weather is not knowable from configuration. Honouring ADR-0001 would have meant caching observed daily highs and backfilling gaps from a weather archive endpoint, which is a disproportionate amount of machinery for a two-state flip.

## Consequences

- **The alternation does not advance on days the app isn't opened.** After a gap you may get a jacket two days running. It self-corrects the following day, and on days you didn't consult the app you dressed yourself anyway.
- Weather is otherwise a pure input: today's temperature decides *whether* a Layer is worn, never what the Rotation does.
- Look-ahead past the forecast horizon reports the Shirt, pants and shoes — which stay purely derived — and marks the Layer unknown rather than guessing.
- A future reader who finds this cursor and assumes it is an oversight should read ADR-0001 first; the inconsistency is the point.
