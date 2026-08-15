# 02 — Sweaters, shoes, and the office Week Fallback

**What to build:** Outfits become complete — Shirt, pants, shoes, and the sweater that goes with them. Sweaters, jackets and shoes are authored keyed by pants rather than by Shirt, so each Closet carries a three-row mapping instead of one row per Shirt.

On top of that sits the office rule: within a Monday-start Week, no sweater and no pair of shoes may repeat. A collision is always two office Shirts in the same Week sharing pants, and when one happens the second Shirt takes its Fallback sweater instead. Because office shoes are a bijection with office sweaters, the shoes follow the sweater automatically and the no-repeat guarantee for footwear comes for free.

Home has no no-repeat rule, and its shoe mapping is deliberately not a bijection.

**Blocked by:** 01 — Rotation for any date

**Status:** ready-for-agent

- [ ] Sweaters, jackets and shoes resolve from pants, per Closet, with three rows each
- [ ] Office sweaters never repeat within a Monday-start Week
- [ ] Office shoes never repeat within a Monday-start Week, as a consequence of the sweater rule rather than a separate check
- [ ] When two office Shirts in a Week share pants, the later one takes its Fallback sweater
- [ ] A Fallback moves the shoes along with the sweater
- [ ] A Week containing four or more Office Days returns the primary sweater and marks the Response as containing an unavoidable repeat, rather than failing
- [ ] Home Outfits resolve sweater and shoes from pants with no no-repeat rule applied
- [ ] All five office Week shapes are asserted — the three that resolve cleanly and the two that require a Fallback
- [ ] Friday Aug 21 2026 resolves to the black Shirt, tan pants, grey sweater and white shoes, and Monday Aug 24 starts a fresh Week with lblue taking grey cleanly
- [ ] Tests assert only on the resolved Outfit, never on how a Week was walked
