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

**Status:** done

- [x] Labels live in the State; the Labels in source are only the starting values used when no State file exists
- [x] `replace <target> <label>` gives a Garment a new Label and changes no Position anywhere
- [x] A Garment is addressed by a dotted target naming its Closet, its kind and its current Label, with Pants addressed without a Closet
- [x] Replacing a home Garment that two Pants Rows both call for changes it once, for both
- [x] Replacing Pants changes them in both Closets
- [x] A Label that already names another Garment of the same kind in that Closet is refused, so the output stays something the wearer can act on
- [x] The same Label naming different Garments in the two Closets stays legal
- [x] `swap <closet> <label> <label>` exchanges two Shirts' Labels
- [x] Two Shirts with different Pants are refused, as is a Label absent from that Closet
- [x] After a Swap, no resolved Outfit for any date differs except in which Shirt is named
- [x] `show-closet` prints both Closets with Shirts in Rotation order
- [x] The listing shows each Shirt's Pants in its own column, so legal Swaps are visible by scanning rather than discovered as an error
- [x] The listing prints the dotted target for each Garment, so one can be copied rather than guessed
- [x] The README describes the commands rather than a config file

## Comments

**A Garment's identity is the Label it shipped with.** The State's
`labels` maps a Garment to what it is called now, and the key is the
dotted address of the Label in `wardrobe.py` -- `office.shirt.white`,
`pants.blue`. That key never moves, so nothing in the State is keyed
by a Label in the sense ADR-0006 forbids: `office.sweater.beige` goes
on naming the same sweater after it is replaced by `navy`. Every
string in `wardrobe.py` is therefore a Garment and not a statement of
what it is called, which is why `Shirt.label` became `Shirt.garment`.

**A full map rather than a sparse overlay.** The spec says the State
holds "a Label per Garment", so `get_default_state` seeds every one
and resolution is a plain lookup. `_parse_state` merges the file over
the given Labels, so a file written before a Garment existed -- the
jackets 06 adds -- still reads.

**`DEFAULT_OFFICE` and `DEFAULT_HOME` became `CLOSETS`.** With the
Labels moved into the State the Closets are not defaults of anything:
they are shape, and shape never moves. One mapping keyed by DayType
also gives `cli.py` the Closets it needs for `show-closet` without
reaching into `core`'s private `_CLOSETS`. It is defined below the
Closet literals it names rather than above them, because a module
constant cannot forward-reference; the ordering rule holds for
everything the interpreter defers.

**Duplicate Labels are checked by address, not by scan.** A Garment's
current address is `prefix.label`, so "another Garment of the same
kind in that Closet already has this Label" is one dictionary lookup
against the same map the target is resolved through. Restating the
Label a Garment already has is a no-op rather than a refusal, in
keeping with every other command being idempotent by restatement.

**`show-closet` renders in the shell and answers nothing.** It is the
one invocation that is about no date, so `run` prints and returns
before `apply`. The listing is four columns -- kind, Label, Pants,
address -- for every Garment, so the shared home shoes appear once per
Pants Row with the same address both times, which is what says they
are one pair. Pants are listed once, under neither Closet.

**"recorded" now follows the write rather than the command.** Review
found `replace pants.blue blue` printing `recorded pants.blue is now
blue` while writing nothing, which `stay-home` on a Home Day had been
doing since 03. `run` hands `_render` the command only when the State
it got back differs, so a restatement stays the no-op it is and says
so by saying nothing. `test_either_side_of_the_command_names_the_same
_date` gained a State file per form, because the second form was
restating what the first had recorded.

**An Outfit holds Garments until the last step.** The office Week walk
resolves in Garments -- `taken` and the Fallback's donor row both
compare identities -- so the `Response`s it accumulates carry Garments
in their `Outfit` and `answer` names them once at the end. Known: one
type means two things across three private functions. The alternative
is a second Outfit-shaped type for the walk, which is more code than
the confusion is worth while both functions are private and `answer`
is their only caller.

**Two tests that failed on four days in seven were fixed in passing.**
`test_the_date_defaults_to_today` and
`test_the_directory_arrives_with_the_first_record` recorded
`stay-home` for today, which records nothing when today is already a
Home Day. They now say whichever of the two today is not. Unrelated to
this ticket, but the suite has to pass on a Saturday.
