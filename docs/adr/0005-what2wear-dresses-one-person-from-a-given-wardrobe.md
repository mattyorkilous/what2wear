# what2wear dresses one person from a given Wardrobe

The Wardrobe is a fact about the person the tool dresses, not an input:
its Closets, their sizes, which Pants each Shirt is welded to and which
sweater, shoes and jacket follow from each pair of Pants are all given
and unchangeable at runtime. The rejected alternative is what the tool
did first — a hand-authored YAML file anyone could point at their own
clothes.

We rejected it because the rules only mean anything against this
Wardrobe's shape. The office no-repeat rule needs office sweaters
one-to-one with office shoes and a Fallback that is another row's
sweater; the Rotations only feel varied because 5 and 9 are coprime
with 3 Office Days and 4 Home Days a week; the Home Outerwear Rotation's 2
is only interesting because the home Closet is odd-sized. A stranger's
closet satisfying the schema and none of that would produce confident
nonsense, and no amount of validation catches it. So the generality was
buying a user who cannot exist, at the cost of a config boundary, a
schema, and a second author for facts the tool also writes.

## Consequences

- **Garments cannot be added or removed, only replaced.** A sixth
  office Shirt is a source change and a commit. Accepted readily: in
  practice a Wardrobe changes by replacement, not by growth, and a
  Replace covers that exactly. In exchange, closet size is immutable at
  runtime, so no command can reshuffle a Rotation — which retires the
  worst consequence ADR-0001 had to accept.
- **Pairings cannot change either.** Which sweater follows which Pants
  is structure, and re-pairing is a source change. A Swap looks like a
  re-pairing and is not: it is restricted to Shirts sharing Pants, so
  it exchanges two Labels and provably nothing else.
- **The anonymization in `.scratch/config-location/01` is deliberately
  undone.** That ticket moved a real person's closet out of the repo
  because the repo shipped a tool a stranger might configure. This ADR
  retires that reading, so the real Labels ship as the given Wardrobe's
  starting Labels and `example.yaml` is deleted. The repository is
  private, and the alternative was thirty Replace commands on first run
  to get back to where you started.
- **No config boundary survives.** Duplicate Shirt names, unmapped
  Pants, a Fallback that is no other row's sweater, office sweaters not
  one-to-one with shoes, an Anchor on the wrong kind of day: all of it
  becomes a property of source that a test asserts once, rather than a
  validation run on every invocation. `pydantic` leaves the project.
