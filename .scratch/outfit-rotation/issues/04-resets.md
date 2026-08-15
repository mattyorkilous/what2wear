# 04 — Resets

**What to build:** A way to move the Rotation on when the Shirt you've been given isn't the one you want — because it's in the wash, or you just don't fancy it.

Two forms. Bare, it advances to the next Shirt. Given a Shirt name, it jumps straight to that Shirt, with the Closet inferred from whether the date is an Office Day or a Home Day; naming a Shirt that isn't in that Closet is an error rather than a silent guess. Naming a Shirt never changes the day's type — if both are wanted, that's an override followed by a reset, as two deliberate commands.

A Reset is recorded as a permanent shift from that date forward, per ADR-0001. Every later date moves with it; the Rotation stays continuous rather than snapping back the next day. This is also why look-ahead is only valid until the next Reset.

**Blocked by:** 03 — Day Type Overrides (shares the append-only decision log)

**Status:** ready-for-agent

- [ ] A bare reset advances the day's Rotation by one Shirt
- [ ] A reset naming a Shirt jumps to that Shirt on that date
- [ ] The Closet is inferred from the date's type; a Shirt name absent from that Closet is a clear error
- [ ] Naming a Shirt never alters the date's type
- [ ] A Reset shifts every subsequent date's Position, permanently
- [ ] Resets and Day Type Overrides interleave correctly in the same log, in date order
- [ ] Multiple Resets accumulate rather than replacing one another
- [ ] Look-ahead performed before a Reset and the same date resolved after it differ by exactly the recorded shift
