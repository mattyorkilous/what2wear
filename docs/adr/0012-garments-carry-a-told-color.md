# Garments carry a told Color

Each Garment has a Color, a `#rrggbb` string, and a striped one a
stripe Color too. The given Wardrobe supplies a starting Color beside
each starting Label, and the State gains a `colors` map keyed exactly
like `labels`, by where the Garment hangs (ADR-0010), written only
where it differs from the given. An `Outfit` now names each of its
garments as a `Garment` carrying its Label and Colors, not a bare
Label.

This reverses the Label being "the whole of what the tool prints at
you". The phone draws each Garment as an icon filled with its Color, so
the Color has to come from somewhere. Deriving it from the Label would
only work for Labels a table knows, and a Label is free text; told
alongside the Label, it is right for any Garment, and a Garment is
never drawn in a guessed grey.

## Consequences

- **A Label and its Color travel together.** A Swap exchanges the two
  Shirts' `colors` entries along with their `labels` entries, so a
  Shirt never ends up drawn in another's Color.
- **A file without `colors` reads as the given Colors**, as a file
  without `labels` reads as the given Labels, so the live State needs
  no migration.
- **`answer` looks the Color up where it looks up the Label.** The
  given structure — `Shirt`, `PantsRow`, `Closet` — is untouched: it
  is given and holds no told data. The walk that resolves a Week
  carries the given Garment, and the told one replaces it at the end.
- **The CLI prints what it always has.** It reads `.label` and ignores
  the Color, which only the phone draws.
