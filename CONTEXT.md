# what2wear

Tells you what to wear today, and what you'll wear on a future day, by
walking a fixed set of shirts in a repeating order that is aware of
whether you're going into the office and how cold it is.

It dresses one person out of one known Wardrobe. Nobody configures it;
the only things it can be told are which garments have been replaced,
what kind of day a date is, and where a Rotation stands.

## Language

### Clothing

**Wardrobe**:
Every garment you own and how they go together — the two Closets, the
Pants they share, and which sweater, shoes and jacket follow from each
pair of Pants. The Wardrobe is *given*: its shape is a fact about the
person the tool dresses, not something the tool is told, so nothing in
it can be added to, removed or re-paired while the tool is running.
_Avoid_: settings, profile, config, closet file

**Closet**:
An ordered list of Shirts for one setting, together with the Pants Rows
that dress them. There are exactly two, the Office Closet and the Home
Closet, and they are independently and permanently sized.
_Avoid_: collection, drawer

**Garment**:
Anything you put on — a Shirt, a pair of Pants, a sweater, a jacket, a
pair of shoes. Every Garment has a fixed identity and a Label that can
change. Within one Closet a Label names exactly one Garment; the same
Label in the two Closets names two different Garments.
_Avoid_: item, piece, article

**Label**:
What a Garment is called — usually its color, sometimes its cut. A
Label is the only thing about the Wardrobe that moves, and it is the
whole of what the tool prints at you, so it has to be something you can
act on. Changing one never disturbs a Rotation, because nothing is
keyed by it.
_Avoid_: color, name, description

**Shirt**:
One position in a Closet, carrying the Pants welded to it. Its sweater,
its shoes and its jacket all follow from those Pants.
_Avoid_: look, outfit, combination, top

**Pants**:
The trousers a Shirt is welded to. There is one set of them and both
Closets wear it — the same Pants, not two pairs that match. What they
are *worn with* differs by Closet, which is the Pants Row.
_Avoid_: trousers, bottoms, legwear

**Pants Row**:
What one Closet pairs with one pair of Pants — the sweater and shoes
that follow from them, plus the jacket or the Fallback, depending on
the Closet. Each Closet has its own row per pair of Pants, so the same
Pants dress differently at the office than at home.
_Avoid_: mapping, entry, pairing, combination

**Outerwear**:
A sweater or a jacket, worn over a Shirt when the day is cold enough.
The jacket is a light indoor one, worn in the same places and for the
same reason as the sweater — nothing here is a coat. The Office Closet
has sweaters only; the Home Closet has both, and which of the two a
Home Day calls for comes from the Home Outerwear Rotation, not from the
weather. Temperature decides only _whether_ Outerwear is worn, so a
warm Home Day spends its turn wearing nothing.
_Avoid_: layer, overlayer, coat, outer layer

**Outfit**:
The fully resolved set of garments for one date — a Shirt, its Pants,
its shoes, and any Outerwear. An Outfit is always derived and never stored.
_Avoid_: look, combination, ensemble

### Calendar

**Office Day**:
A date on which you go into the office, and therefore draw from the
Office Closet. Which dates those are comes from the Office Weekdays,
unless a Day Type Override says otherwise.
_Avoid_: in-office day, commute day

**Home Day**:
A date on which you do not go into the office, and therefore draw from
the Home Closet. Weekends are Home Days unless the Office Weekdays say
otherwise.
_Avoid_: WFH day, remote day, day off

Every date is exactly one of an Office Day or a Home Day. There is no
third, unclassified kind of day.

**Week**:
A Monday-start calendar week. It exists in this domain only as the
scope within which office sweaters may not repeat.
_Avoid_: work week, rotation week, sprint

### Sequencing

**Rotation**:
The repeating traversal of an ordered list, in order, wrapping at the
end. A Rotation advances only on days of its own kind — Office Days do
not move a home Rotation, or vice versa. There are three: a Shirt
Rotation per Closet, and the Home Outerwear Rotation. Each has its own
Anchor and is Reset independently.
_Avoid_: cycle, schedule, queue

**Shirt Rotation**:
The Rotation over one Closet's Shirts. Where a Closet is in scope and
Outerwear is not, "Rotation" unqualified means this one.
_Avoid_: closet rotation, main rotation

**Home Outerwear Rotation**:
The Rotation over the two kinds of home Outerwear, sweater and jacket,
that decides which kind a Home Day calls for. It advances on the same
Home Days as the Home Shirt Rotation but counts from its own Anchor, so
a Reset to one leaves the other where it was. The Office Closet has no
equivalent — office Outerwear follows from Pants alone.
_Avoid_: parity, cursor, flip, toggle

**Position**:
Where a Rotation stands on a given date — counted forward from its
Anchor over days of its own kind. A Position is derived, never stored
and never consumed, so every date is the same derivation: past, today
and years out alike. A past Position is a fact about the present, not
a record of what was worn, because a Reset rewrites it.
_Avoid_: cursor, pointer, index

**Resolution**:
The per-date step that turns a Shirt into an Outfit by settling its
sweater, its shoes and its Outerwear. Distinct from Rotation: Rotation
picks the Shirt, Resolution decides everything else about the day.
_Avoid_: selection, calculation, assembly

**Fallback**:
The alternate sweater a Pants Row offers during Resolution when its own
sweater has already been worn that Week. Always another row's sweater,
so the shoes come across with it.
_Avoid_: secondary, backup, alternate, substitute

### The State

**State**:
Everything the tool has been told, in the one file it owns. It holds
the Labels, the Anchors, the Day Type Overrides, the Office Weekdays
and the Cold Threshold. What may appear here is something the wearer
told the tool; what may not is the Wardrobe's shape, which is given.
It is the only thing the tool writes, and no human authors it.
_Avoid_: config, settings, database, log

**Anchor**:
A date and the Position one Rotation stood at on it. Every Position is
counted from here. There is one Anchor per Rotation, each moved on its
own by a Reset, and each stores a Position rather than a Label so that
a Swap or a Replace cannot move it.
_Avoid_: epoch, start date, origin, anchor date

**Day Type Override**:
A record that a specific date is an Office Day or a Home Day regardless
of the Office Weekdays. Holidays, leave, going in on a Saturday and
staying home on a Wednesday are all the same thing. One record per
date, so saying it again replaces what was said before.
_Avoid_: exception, holiday, PTO, absence

**Office Weekdays**:
The three weekdays that are Office Days unless a Day Type Override says
otherwise. Which three is told; that there are exactly three is given,
because the Closet sizes only stay varied against three Office Days and
four Home Days a week. Changing them re-anchors every Rotation, so no
Position moves.
_Avoid_: schedule, pattern, weekly pattern, work week

**Cold Threshold**:
The temperature below which Outerwear is worn. It decides only whether,
never which — a warm Home Day still spends its Home Outerwear Rotation
turn wearing nothing.
_Avoid_: temperature threshold, cutoff, limit, tolerance

**Reset**:
The act of moving a Rotation's Anchor to a date and a Position you name.
The date is today unless you say otherwise. Used when the Shirt you were
given isn't the one you want, or when the Home Outerwear Rotation has
fallen out of step with what you actually wore. It is the only way a
Rotation is corrected, and it takes the whole Rotation with it rather
than skipping a day — so a Reset dated ahead of today moves today too.
_Avoid_: skip, reroll, shuffle, override, re-anchor

**Replace**:
The act of giving a Garment a new Label, because you replaced it or
because it was called the wrong thing. Nothing distinguishes those two:
no Garment's history is kept, so a new sweater in the same Pants Row
and a corrected name for the old one are the same event.
_Avoid_: rename, recolor, edit, update

**Swap**:
The act of exchanging the Labels of two Shirts in one Closet. Only
Shirts sharing Pants may be swapped, which makes a Swap purely
cosmetic — it changes which Shirt you reach for on a given date and
cannot touch the Pants, the sweater, the shoes or the Fallback.
_Avoid_: reorder, move, shuffle, rearrange
