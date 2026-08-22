# Office Weekdays and the Cold Threshold are told, not given

Which weekdays are Office Days, and the temperature below which
Outerwear is worn, move out of source and into the State, each settable
by its own command. They had been given, and the spec listed them under
Out of Scope with the note that a change to either was commit-worthy.

This does not weaken ADR-0005. Neither is part of the Wardrobe. A
Wardrobe is Closets, Shirts, Pants and the rows that dress them —
things with a Pants Row, things a Replace can rename. Office Weekdays
is a fact about the wearer's employment and the Cold Threshold is a
fact about their tolerance for cold; they lived in the same source
module as the Closets because they happened to be constants, not
because they were the same kind of thing. What this decision actually
amends is ADR-0006's "the Labels, the three Anchors and the Day Type
Overrides, and nothing else": the State also holds told facts about the
wearer that are not about clothes.

## Consequences

- **Office Weekdays must name exactly three weekdays.** The count is
  structure and stays a source change; only which three is told. The
  arithmetic is why. With five office Shirts and nine home Shirts, a
  Shirt returns to the same weekday after `5 / gcd(5, k)` and
  `9 / gcd(9, 7 - k)` weeks for `k` Office Days a week. At `k = 5` the
  same office Shirt lands on every Monday forever; at `k = 1` or
  `k = 4` the home cycle collapses from nine weeks to three; and at
  `k >= 4` the office no-repeat rule is not merely degraded but void,
  because three sweaters cannot cover four days. `k = 2` is
  arithmetically sound and is refused anyway — a wearer who genuinely
  goes in twice a week has the same standing as a sixth office Shirt,
  which ADR-0005 already made a commit.
- **Setting Office Weekdays re-anchors all three Rotations.** Positions
  count days of a kind between the Anchor and the date, so
  reclassifying the past would move every Rotation by an arbitrary
  amount — the thing a Replace and a Swap are carefully built not to
  do. The command therefore reads today's three Positions under the old
  Office Weekdays, then writes the new ones together with all three
  Anchors moved to today at those Positions. The rejected alternative
  was storing Office Weekdays with an effective-from date and deriving
  Positions over a piecewise timeline, which puts history back in the
  file ADR-0006 exists to keep free of it.
- **A mid-Week change can move that Week's Fallback.** The office walk
  resolves the Week's earlier days under the new Office Weekdays, so
  the sweater Friday falls back to can differ from what it would have
  been. This is the same consequence ADR-0001 already accepts for a
  mid-Week Reset, and is asserted by a test for the same reason.
- **Weekends may be named.** Nothing in the arithmetic distinguishes
  Saturday, and refusing it would invent a rule the domain does not
  have. `CONTEXT.md`'s "Weekends are Home Days" becomes a default
  rather than a fact.
- **The Cold Threshold carries none of this.** It moves no Position: a
  warm Home Day already spends its turn. It is a plain State field with
  a command, and needs no re-anchoring.
- **A validation returns to the tool.** ADR-0005 removed the config
  boundary on the grounds that validating a stranger's Wardrobe bought
  a user who cannot exist. The exactly-three refusal is not that
  boundary coming back: it checks one value the wearer typed a moment
  ago, at the moment they typed it, and is corrected by restating the
  command. No schema, no file, no validation on the answering path.
- **The given module is no longer only the Wardrobe.** It holds the
  Wardrobe's given shape and the starting values the State overlays —
  the Labels, the Anchors, the Office Weekdays and the Cold Threshold.
  It is renamed to say so.
