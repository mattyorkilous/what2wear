# what2wear

Tells you what to wear today, and what you'll wear on a future day, by walking a fixed set of shirts in a repeating order that is aware of whether you're going into the office and how cold it is.

## Language

### Clothing

**Shirt**:
The authored unit of a Closet, and the only garment a human writes down. A Shirt carries the pants welded to it, its preferred sweater, and — in the Home Closet — its jacket.
_Avoid_: look, outfit, combination, top

**Closet**:
An ordered list of Shirts for one setting. There are exactly two, the Office Closet and the Home Closet, and they are independently sized.
_Avoid_: wardrobe, collection, drawer

**Layer**:
A sweater or a jacket, worn over a Shirt when the day is cold enough. The Office Closet has sweaters only; the Home Closet has both.
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
The repeating traversal of a single Closet, in order, wrapping at the end. Each Closet has its own Rotation, and a Rotation advances only on days of its own kind — Office Days do not move the Home Rotation, or vice versa.
_Avoid_: cycle, schedule, queue

**Position**:
Where a Rotation stands on a given date — the index of the Shirt worn that date. A Position is always derived from the calendar, never stored and never consumed; asking about a future date uses the same derivation as asking about today.
_Avoid_: cursor, pointer, index

**Resolution**:
The per-date step that turns a Shirt into an Outfit by settling its sweater, its shoes and its Layer. Distinct from Rotation: Rotation picks the Shirt, Resolution decides everything else about the day.
_Avoid_: selection, calculation, assembly

**Fallback**:
The alternate sweater a Shirt takes during Resolution when its preferred sweater has already been worn that Week.
_Avoid_: secondary, backup, alternate, substitute

### Recorded decisions

**Day Type Override**:
A record that a specific date is an Office Day or a Home Day regardless of the weekly pattern. Holidays, leave, going in on a Saturday and staying home on a Wednesday are all the same thing.
_Avoid_: exception, holiday, PTO, absence

**Reset**:
A record that shifts a Rotation's Position from a given date forward, permanently. Used when the Shirt you were given isn't the one you want.
_Avoid_: skip, reroll, shuffle, override

**Anchor Date**:
The date on which every Rotation sits at Position 0. All Positions are counted from it.
_Avoid_: epoch, start date, origin
