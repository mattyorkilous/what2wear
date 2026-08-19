# what2wear

Tells you what to wear today, and what you'll wear on a future day, by walking a fixed set of shirts in a repeating order that is aware of whether you're going into the office and how cold it is.

## Language

### Clothing

**Shirt**:
The authored unit of a Closet, and the only garment a human writes down. A Shirt carries the pants welded to it and nothing else — its sweater, its shoes and its jacket all follow from those pants.
_Avoid_: look, outfit, combination, top

**Wardrobe**:
Both Closets together with the weekday pattern that says which of them a date draws from — everything a human authors, in one file. There is exactly one per installation, it lives as `config.yaml` where the platform keeps a user's config, and the tool reads it and never writes it. "Config" names the platform's directory and the file in it; the thing written there is a Wardrobe.
_Avoid_: settings, profile, closet file

**Closet**:
An ordered list of Shirts for one setting, together with the Pants Rows that dress them. There are exactly two, the Office Closet and the Home Closet, and they are independently sized.
_Avoid_: collection, drawer

**Pants Row**:
What one Closet pairs with one colour of pants — the sweater and shoes that follow from it, plus the jacket or the Fallback, depending on the Closet. The same colour names different garments in the two Closets.
_Avoid_: mapping, entry, pairing, combination

**Layer**:
A sweater or a jacket, worn over a Shirt when the day is cold enough. The Office Closet has sweaters only; the Home Closet has both, and which of the two a Home Day calls for comes from the Home Layer Rotation, not from the weather. Temperature decides only _whether_ the Layer is worn, so a warm Home Day spends its turn wearing nothing.
_Avoid_: outerwear, overlayer, coat

**Outfit**:
The fully resolved set of garments for one date — a Shirt, its pants, its shoes, and any Layer. An Outfit is always derived and never authored.
_Avoid_: look, combination, ensemble

### Calendar

**Office Day**:
A date on which you go into the office, and therefore draw from the Office Closet.
_Avoid_: in-office day, commute day

**Home Day**:
A date on which you do not go into the office, and therefore draw from the Home Closet. Weekends are Home Days.
_Avoid_: WFH day, remote day, day off

Every date is exactly one of an Office Day or a Home Day. There is no third, unclassified kind of day.

**Week**:
A Monday-start calendar week. It exists in this domain only as the scope within which office sweaters may not repeat.
_Avoid_: work week, rotation week, sprint

### Sequencing

**Rotation**:
The repeating traversal of an ordered list, in order, wrapping at the end. A Rotation advances only on days of its own kind — Office Days do not move a home Rotation, or vice versa. There are three: a Shirt Rotation per Closet, and the Home Layer Rotation.
_Avoid_: cycle, schedule, queue

**Shirt Rotation**:
The Rotation over one Closet's Shirts. Where a Closet is in scope and Layers are not, "Rotation" unqualified means this one.
_Avoid_: closet rotation, main rotation

**Home Layer Rotation**:
The Rotation over the two kinds of home Layer, sweater and jacket, that decides which kind a Home Day calls for. It advances on the same Home Days as the Home Shirt Rotation but counts separately, so a Reset to one leaves the other where it was. The Office Closet has no equivalent — office Layers follow from pants alone.
_Avoid_: parity, cursor, flip, toggle

**Position**:
Where a Rotation stands on a given date — the index of the Shirt worn that date. A Position is always derived from the calendar, never stored and never consumed; asking about a future date uses the same derivation as asking about today.
_Avoid_: cursor, pointer, index

**Resolution**:
The per-date step that turns a Shirt into an Outfit by settling its sweater, its shoes and its Layer. Distinct from Rotation: Rotation picks the Shirt, Resolution decides everything else about the day.
_Avoid_: selection, calculation, assembly

**Fallback**:
The alternate sweater a Pants Row offers during Resolution when its own sweater has already been worn that Week. Always another row's sweater, so the shoes come across with it.
_Avoid_: secondary, backup, alternate, substitute

### Recorded decisions

**Day Type Override**:
A record that a specific date is an Office Day or a Home Day regardless of the weekly pattern. Holidays, leave, going in on a Saturday and staying home on a Wednesday are all the same thing.
_Avoid_: exception, holiday, PTO, absence

**Reset**:
A record that shifts one named Rotation's Position from a given date forward, permanently. Used when the Shirt you were given isn't the one you want, or when the Home Layer Rotation has fallen out of step with what you actually wore.
_Avoid_: skip, reroll, shuffle, override

**Anchor Date**:
The date on which a Closet's Rotations sit at Position 0. All Positions are counted from it, and a Reset dated before it no longer counts — re-authoring an Anchor Date is the last word on where its Rotations stand. Each Closet has one, given as a date plus the Shirt worn on it; the home Anchor Date additionally names the Layer worn, because the Home Layer Rotation counts from the same date.
_Avoid_: epoch, start date, origin
