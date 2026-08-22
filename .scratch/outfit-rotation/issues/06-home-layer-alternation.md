# 06 — Home Outerwear alternation

**What to build:** The home half of the Outerwear rule. Every Home Day is a jacket day or a sweater day, decided by the **Home Outerwear Rotation** — a Rotation of length 2 that advances on every Home Day and is derived from the calendar like every other Position. The weather decides only whether the Outerwear is worn. A warm Home Day wears nothing and still spends its turn.

Per ADR-0004 this replaces the stored cursor ADR-0002 described. There is no Outerwear log, nothing is recorded when outerwear resolves, and `handle` needs no new state — the existing decision log already carries everything.

The accepted consequence is that a cold, mild, cold run gives jacket, nothing, jacket: the mild day consumed the sweater turn while you wore no sweater. Assert this rather than work around it. In exchange the alternation advances on days the tool isn't opened, so there is no "behavior after a gap" case at all.

Two Rotations now run over the same Home Days, counting independently. `--reset-outerwear` shifts the Outerwear Rotation and leaves the Shirt Rotation alone; a bare or named `--reset` does the reverse. `--reset-outerwear` takes no argument — over two items, "advance by one" and "flip to the other" are the same operation. It is legal on an Office Day: that day doesn't consult the Rotation, but the offset lands on the next Home Day, which is what someone typing it on a Wednesday means.

This ticket reaches into the config boundary, which the earlier draft did not. The home anchor gains a required `outerwear:` naming the Outerwear worn on the anchor date, fixing Position 0 of the Outerwear Rotation. `config.py`, its validation, `example.yaml` and the anchor examples in `README.md` all change; office anchors are untouched. Those three files are deliberately left alone until this ticket lands, because config parsing is strict and an unknown key is an error — documenting `outerwear:` early would document config the tool rejects.

**Blocked by:** 05 — Weather and office Outerwear

**Status:** superseded — do not build

Re-cut under `.scratch/given-wardrobe/spec.md`. The behavior described
here is still wanted, but it is specified against the hand-authored
config file and the append-only decision log, both of which are gone.

- [ ] The home anchor requires a `outerwear:` of `sweater` or `jacket`; a missing or unknown value is a clear config error naming the field
- [ ] Below the threshold, a Home Day Outfit includes the Outerwear its Rotation Position calls for, with the garment resolved from pants as with every other garment
- [ ] At or above the threshold no Outerwear is worn, the output says nothing about which kind it would have been, and the Rotation advances anyway
- [ ] Cold, warm, cold across three consecutive Home Days yields the same kind of Outerwear on the first and third — the ADR-0004 consequence, asserted directly
- [ ] Office Days advance neither home Rotation, and office sweaters never influence the Outerwear Rotation
- [ ] A Day Type Override that makes a date a Home Day advances both home Rotations
- [ ] Nothing is written when outerwear resolves, and there is no second log
- [ ] Look-ahead to a Home Day past the forecast horizon names the garment and hedges only the condition, per 05
- [ ] `--reset-outerwear` shifts every subsequent Home Day's Outerwear and leaves the Shirt Rotation's Positions unchanged
- [ ] A `--reset` on the Shirt Rotation leaves the Outerwear Rotation's Positions unchanged
- [ ] `--reset-outerwear` issued on an Office Day is accepted and takes effect on the next Home Day
- [ ] Multiple Outerwear resets accumulate, in date order, interleaved with Shirt resets and Day Type Overrides in the same log
