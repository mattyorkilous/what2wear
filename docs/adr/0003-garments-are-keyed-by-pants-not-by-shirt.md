# Sweaters, shoes and jackets are keyed by pants, not by Shirt

Each Closet carries one Pants Row per pants colour — a sweater, shoes, and either a jacket or a Fallback — instead of authoring those garments onto every Shirt. With three pants colours and nine home Shirts, the pants-keyed shape is three rows to maintain rather than nine, and it cannot drift into contradicting itself the way nine hand-written copies can. The price is that it manufactures the collision Fallbacks exist to solve: per-Shirt authoring would never have had one.

## Consequences

- **A sweater collision is exactly two office Shirts in a Week sharing pants.** That is the whole reason the Fallback column exists, and why the office rule is a Week-scoped walk rather than a per-day lookup.
- **Office sweaters must stay one-to-one with office shoes.** A Fallback names another row's sweater and brings that row's shoes along, so a Closet where two rows share a sweater has no answer for which shoes to wear. The config boundary rejects one. Home shoes are deliberately not one-to-one — blue and tan both give black — which is safe only because home has no no-repeat rule.
- **Two different pairs of trousers of the same colour cannot be told apart** in one Closet, because the colour is the key. Accepted: name them differently or treat them as one.
- **Editing a row restyles every Shirt with those pants at once.** That is the point, and it is also the failure mode — there is no way to make one Shirt an exception without giving it its own pants colour.
