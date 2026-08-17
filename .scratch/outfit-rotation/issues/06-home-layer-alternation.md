# 06 — Home Layer alternation

**What to build:** The home half of the Layer rule. Every Home Day is a jacket day or a sweater day, decided by the **Home Layer Rotation** — a Rotation of length 2 that advances on every Home Day and is derived from the calendar like every other Position. The weather decides only whether the Layer is worn. A warm Home Day wears nothing and still spends its turn.

Per ADR-0004 this replaces the stored cursor ADR-0002 described. There is no Layer log, nothing is recorded when a Layer resolves, and `handle` needs no new state — the existing decision log already carries everything.

The accepted consequence is that a cold, mild, cold run gives jacket, nothing, jacket: the mild day consumed the sweater turn while you wore no sweater. Assert this rather than work around it. In exchange the alternation advances on days the tool isn't opened, so there is no "behaviour after a gap" case at all.

Two Rotations now run over the same Home Days, counting independently. `--reset-layer` shifts the Layer Rotation and leaves the Shirt Rotation alone; a bare or named `--reset` does the reverse. `--reset-layer` takes no argument — over two items, "advance by one" and "flip to the other" are the same operation. It is legal on an Office Day: that day doesn't consult the Rotation, but the offset lands on the next Home Day, which is what someone typing it on a Wednesday means.

This ticket reaches into the config boundary, which the earlier draft did not. The home anchor gains a required `layer:` naming the Layer worn on the anchor date, fixing Position 0 of the Layer Rotation. `config.py`, its validation, `example.yaml` and the anchor examples in `README.md` all change; office anchors are untouched. Those three files are deliberately left alone until this ticket lands, because config parsing is strict and an unknown key is an error — documenting `layer:` early would document config the tool rejects.

**Blocked by:** 05 — Weather and office Layers

**Status:** ready-for-agent

- [ ] The home anchor requires a `layer:` of `sweater` or `jacket`; a missing or unknown value is a clear config error naming the field
- [ ] Below the threshold, a Home Day Outfit includes the Layer its Rotation Position calls for, with the garment resolved from pants as with every other garment
- [ ] At or above the threshold no Layer is worn, the output says nothing about which kind it would have been, and the Rotation advances anyway
- [ ] Cold, warm, cold across three consecutive Home Days yields the same kind of Layer on the first and third — the ADR-0004 consequence, asserted directly
- [ ] Office Days advance neither home Rotation, and office sweaters never influence the Layer Rotation
- [ ] A Day Type Override that makes a date a Home Day advances both home Rotations
- [ ] Nothing is written when a Layer resolves, and there is no second log
- [ ] Look-ahead to a Home Day past the forecast horizon names the garment and hedges only the condition, per 05
- [ ] `--reset-layer` shifts every subsequent Home Day's Layer and leaves the Shirt Rotation's Positions unchanged
- [ ] A `--reset` on the Shirt Rotation leaves the Layer Rotation's Positions unchanged
- [ ] `--reset-layer` issued on an Office Day is accepted and takes effect on the next Home Day
- [ ] Multiple Layer resets accumulate, in date order, interleaved with Shirt resets and Day Type Overrides in the same log
