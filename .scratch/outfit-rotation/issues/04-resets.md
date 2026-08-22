# 04 — Resets

**What to build:** A way to move the Rotation on when the Shirt you've been given isn't the one you want — because it's in the wash, or you just don't fancy it.

Two forms. Bare, it advances to the next Shirt. Given a Shirt name, it jumps straight to that Shirt, with the Closet inferred from whether the date is an Office Day or a Home Day; naming a Shirt that isn't in that Closet is an error rather than a silent guess. Naming a Shirt never changes the day's type — if both are wanted, that's an override followed by a reset, as two deliberate commands.

A Reset is recorded as a permanent shift from that date forward, per ADR-0001. Every later date moves with it; the Rotation stays continuous rather than snapping back the next day. This is also why look-ahead is only valid until the next Reset.

The record is `(date, rotation, offset)` — it names which Rotation it shifts, even though this ticket only ever writes `shirt`. Ticket 06 adds the Home Outerwear Rotation as a second target. The field is spent now rather than retrofitted because the log is append-only: adding a discriminator later means either migrating written records or inventing a defaulting rule for the ones without it, and one field costs less than either.

**Blocked by:** 03 — Day Type Overrides (shares the append-only decision log)

**Status:** done

- [x] A bare reset advances the day's Rotation by one Shirt
- [x] A reset naming a Shirt jumps to that Shirt on that date
- [x] The Closet is inferred from the date's type; a Shirt name absent from that Closet is a clear error
- [x] Naming a Shirt never alters the date's type
- [x] A Reset shifts every subsequent date's Position, permanently
- [x] A recorded Reset names the Rotation it shifts; this ticket writes only `shirt`, and an unknown target is a clear error rather than a silent default
- [x] Resets and Day Type Overrides interleave correctly in the same log, in date order
- [x] Multiple Resets accumulate rather than replacing one another
- [x] Look-ahead performed before a Reset and the same date resolved after it differ by exactly the recorded shift

## Comments

**Post-review, 2026-08-18.** Two things surfaced reviewing this ticket that the ticket itself doesn't cover.

*The Anchor Date is now the last word.* A Reset dated before its Closet's Anchor Date no longer counts. Without that rule, re-authoring the anchor by hand left every earlier Reset stacked on top of it, so naming a Shirt in the config landed you some arbitrary number of Shirts past it. Recorded in ADR-0001.

*Re-anchoring was considered as the record shape and deferred.* A Reset and an Anchor Date are the same fact --- "on this date you were on this Shirt" --- stored in two shapes in two files. Recording Resets as further anchors, with the latest one on or before a date winning, would collapse them into one concept, match how a Reset is actually thought about, and remove the Closet inference below. It was not taken because this ticket prescribes `(date, rotation, offset)`, and because an offset survives a Closet edit where a recorded Shirt name is left stranded (ADR-0001 accepts Closet edits). Worth reopening if the inference below bites.

*Known consequence, not fixed.* Which Closet a Reset moves is derived at read time from its date's type, because the record names the Rotation and not the Closet. So a Day Type Override recorded later against a Reset's own date carries that Reset to the other Closet, applying an offset computed in one Closet's length to the other's. Reachable in practice: `--reset` in the morning, `--stay-home` for the same date in the afternoon. Fixing it properly means a fourth field on the record, which is a change to this ticket.

