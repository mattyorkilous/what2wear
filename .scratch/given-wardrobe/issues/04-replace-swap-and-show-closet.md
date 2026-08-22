# 04 — Replace, swap and show-closet

**What to build:** The wearer can change what they own without editing
anything. Clothes wear out and get replaced, and until now that meant
hand-editing YAML — and because every garment was keyed by its color,
that edit risked moving a Rotation.

`replace` gives a Garment a new Label. Nothing distinguishes a genuine
replacement from a corrected name: no Garment's history is kept, so a new
sweater in the same Pants Row and a fixed spelling for the old one are
the same event. Because nothing is keyed by a Label, a Replace cannot
disturb a Rotation.

Garment identity decides how far a Replace reaches. Within one Closet a
Label names exactly one Garment, so the home shoes two Pants Rows both
call for are one pair and change once. Across the two Closets the same
Label names two different Garments. Pants are the exception that crosses:
there is one set of trousers and both Closets wear it, so replacing Pants
changes both.

`swap` exchanges two Shirts' Labels within one Closet, and only for
Shirts sharing Pants. That restriction is what makes a Swap provably
cosmetic — it changes which Shirt you reach for on a date and cannot
touch the Pants, the sweater, the shoes or the Fallback.

`show-closet` ships in the same slice because the other two are unusable
without it: a Garment is addressed by a dotted target and there is no
longer a file to open and read the targets out of.

**Blocked by:** 03 — One State file and the two seams

**Status:** ready-for-agent

- [ ] Labels live in the State; the Labels in source are only the starting values used when no State file exists
- [ ] `replace <target> <label>` gives a Garment a new Label and changes no Position anywhere
- [ ] A Garment is addressed by a dotted target naming its Closet, its kind and its current Label, with Pants addressed without a Closet
- [ ] Replacing a home Garment that two Pants Rows both call for changes it once, for both
- [ ] Replacing Pants changes them in both Closets
- [ ] A Label that already names another Garment of the same kind in that Closet is refused, so the output stays something the wearer can act on
- [ ] The same Label naming different Garments in the two Closets stays legal
- [ ] `swap <closet> <label> <label>` exchanges two Shirts' Labels
- [ ] Two Shirts with different Pants are refused, as is a Label absent from that Closet
- [ ] After a Swap, no resolved Outfit for any date differs except in which Shirt is named
- [ ] `show-closet` prints both Closets with Shirts in Rotation order
- [ ] The listing shows each Shirt's Pants in its own column, so legal Swaps are visible by scanning rather than discovered as an error
- [ ] The listing prints the dotted target for each Garment, so one can be copied rather than guessed
- [ ] The README describes the commands rather than a config file
