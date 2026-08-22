# Sweaters, shoes and jackets are keyed by Pants, not by Shirt

> Amended by [ADR-0005](./0005-what2wear-dresses-one-person-from-a-given-wardrobe.md).
> The decision is unchanged; the consequences that described a config
> boundary rejecting bad Closets now describe properties of source, and
> a wrong claim about the two Closets sharing color names is corrected.

Each Closet carries one Pants Row per pair of Pants — a sweater, shoes,
and either a jacket or a Fallback — instead of authoring those garments
onto every Shirt. With three pairs of Pants and nine home Shirts, the
Pants-keyed shape is three rows to maintain rather than nine, and it
cannot drift into contradicting itself the way nine hand-written copies
can. The price is that it manufactures the collision Fallbacks exist to
solve: per-Shirt authoring would never have had one.

## Consequences

- **The Pants are shared between the Closets; the rows are not.** There
  is one set of trousers and both Closets wear it, so replacing a pair
  changes both. What is *worn with* them differs entirely — the office
  row and the home row for the same Pants name different sweaters,
  different shoes and, at home only, a jacket. This corrects the
  original claim that the two Closets merely reused color names.
- **A sweater collision is exactly two office Shirts in a Week sharing
  Pants.** That is the whole reason the Fallback column exists, and why
  the office rule is a Week-scoped walk rather than a per-day lookup.
- **Office sweaters must stay one-to-one with office shoes.** A
  Fallback names another row's sweater and brings that row's shoes
  along, so a Closet where two rows share a sweater has no answer for
  which shoes to wear. Under ADR-0005 this is a property of source that
  a test asserts once, not a validation run at load. Home shoes are
  deliberately not one-to-one — two pairs of Pants give the same shoes
  — which is safe only because home has no no-repeat rule.
- **A Fallback points at a Garment, not at a Label.** It always did in
  spirit; now that Labels move it has to in fact, which is what stops a
  Replace from breaking the wiring and removes the check that a
  Fallback names some other row's sweater.
- **Editing a row restyles every Shirt with those Pants at once.** That
  is the point, and it is also the failure mode — there is no way to
  make one Shirt an exception without giving it its own Pants. Under
  ADR-0005 such an edit is a source change, so the blast radius is seen
  at the time it is made rather than discovered at runtime.
