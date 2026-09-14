# Labels are filed by where a Garment hangs, not by what it was called

The State file keys each Label by the Garment's place in its Closet —
`office.shirt.0`, `pants.1` — rather than by the Label the Garment
shipped with. This retires both the Slot and the Address as domain
terms, leaving the Garment and its Label.

The problem this solves is that the key and the typed name were the
same shape. A Slot was the dotted path of the shipped Label,
`office.shirt.white`; an Address was the same prefix with the Label
today, `office.shirt.ecru`. Before any Replace the two were spelled
identically, so a reader of either the file or the code had to hold
both concepts and know which one was in front of them. Four terms
described what is really two things — where a Garment hangs, and what
it is called now.

## Consequences

- **[ADR-0006](./0006-the-wardrobe-is-source-the-state-is-one-file-the-tool-owns.md)'s
  rule now holds by construction.** "Nothing may be keyed by a Label"
  was previously true only of the *current* Label: the key was still
  spelled with the given one, so the rule was kept by the given
  Wardrobe never changing rather than by the key's shape. A counted
  key cannot be a Label at all.
- **Two rows wearing one Garment still share one key.** Home shoes are
  black with blue pants and black with tan, and that is one pair worn
  twice, not two pairs — `replace home.shoes.black oxblood` changes
  both, as it always did. `get_garments` numbers the distinct Garments
  of a kind, so the second row lands on the position the first already
  has. Numbering by row instead would have quietly split the pair.
- **The wearer sees no change.** `show-closet` prints the same lines it
  did before — a Garment's Closet, what it is, and its Label today. The
  key appears nowhere but the file.
- **"Address" went with the Slot.** It had earned its own entry by
  contrast: half its definition said how it differed from a Slot. With
  nothing left to contrast against, what remained was a spelling rule,
  so it folded into the Garment entry and `replace_` takes a `garment`.
  The refusals read better for it — `no office shirt is called 'puce'`
  where the old one said `nothing is addressed 'office.shirt.puce'`,
  and a string with no closet and kind in it still gets the blunter
  `nothing is called 'white'`.
- **The file got less readable, on purpose.** `"office.shirt.0":
  "ecru"` says less to a person opening it than `"office.shirt.white":
  "ecru"` did. Nobody is expected to open it, and the typed name it
  stopped resembling was the whole cost of resembling one.
- **A file written before this reads through a shim.** `_parse_state`
  maps a key spelled with the given Label onto the position it now
  hangs at, so an existing State keeps its Replaces. It is marked to
  be dropped once no file predates it.
- **Adding a Garment to the middle of a Closet now moves keys.**
  Appending is safe; inserting shifts every position after it, and the
  Labels filed under them go with it. The Wardrobe is given and does
  not change while the tool runs, so this is a repo edit to make
  carefully, not a runtime hazard.
