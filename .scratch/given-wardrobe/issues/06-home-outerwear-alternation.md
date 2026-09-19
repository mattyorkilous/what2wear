# 06 — Home Outerwear alternation

**What to build:** The home half of the Outerwear rule. Every Home Day is
a jacket day or a sweater day, decided by the **Home Outerwear
Rotation** — a Rotation of length 2 that advances on every Home Day and
derives its Position from the calendar like every other. The weather
decides only whether the Outerwear is worn. A warm Home Day wears nothing
and still spends its turn.

Per ADR-0004 this replaces the stored cursor ADR-0002 described. Nothing
is written when Outerwear resolves.

The accepted consequence is that a cold, mild, cold run gives jacket,
nothing, jacket: the mild day consumed the sweater turn while the wearer
wore no sweater. Assert this rather than work around it. In exchange the
alternation advances on days the tool is never opened, so there is no
"behavior after a gap" case at all.

This Rotation brings the third Anchor, which appears in the State file
here rather than being reserved in advance — a missing Anchor reads as
the given one, so nothing has to be migrated. `reset-outerwear` moves it
and leaves the Shirt Anchors alone; `reset` does the reverse. It takes no
argument, because over two items "advance by one" and "flip to the other"
are the same operation. It is legal on an Office Day: that day consults
no home Rotation, but the Anchor move lands on the next Home Day, which
is what someone typing it on a Wednesday means.

Re-cut from the superseded `.scratch/outfit-rotation/issues/06`, which
specified this against the decision log and the hand-authored anchor.

**Blocked by:** 05 — Weather and office Outerwear

**Status:** done

- [x] Consecutive cold Home Days alternate jacket, sweater, jacket
- [x] A warm Home Day names no Outerwear and still spends its turn, so the days either side land on the same kind — asserted, not worked around
- [x] Office sweaters interleaved through the same Weeks have no effect on the home alternation
- [x] The Home Outerwear Rotation counts from its own Anchor, which arrives in the State file in this ticket; a State written before it reads as the given Anchor
- [x] Nothing is written when Outerwear resolves, and there is no second file
- [x] Look-ahead to a Home Day past the forecast horizon names the garment and hedges only the condition, per 05
- [x] `reset-outerwear` takes no argument and shifts every subsequent Home Day's Outerwear
- [x] `reset-outerwear` leaves both Shirt Anchors untouched, and a Shirt `reset` leaves the Outerwear Anchor untouched
- [x] `reset-outerwear` issued on an Office Day is accepted and takes effect on the next Home Day
- [x] Home has no no-repeat rule
- [x] The README describes the home alternation and the full command surface
