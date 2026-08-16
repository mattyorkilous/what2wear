# 02 — Sweaters, shoes, and the office Week Fallback

**What to build:** Outfits become complete — Shirt, pants, shoes, and the sweater that goes with them. Sweaters, jackets and shoes are authored keyed by pants rather than by Shirt, so each Closet carries a three-row mapping instead of one row per Shirt.

On top of that sits the office rule: within a Monday-start Week, no sweater and no pair of shoes may repeat. A collision is always two office Shirts in the same Week sharing pants, and when one happens the second Shirt takes its Fallback sweater instead. Because office shoes are a bijection with office sweaters, the shoes follow the sweater automatically and the no-repeat guarantee for footwear comes for free.

Home has no no-repeat rule, and its shoe mapping is deliberately not a bijection.

**Blocked by:** 01 — Rotation for any date

**Status:** done

## The mappings

Authored values, three rows per Closet. These belong in
`what2wear.yaml` alongside the Closets; the config boundary grows to
parse and validate them.

**Office** — a Fallback is always another row's primary sweater, so
the Fallback's shoes are the donor row's shoes:

| Pants | Sweater | Shoes | Fallback     |
| ----- | ------- | ----- | ------------ |
| blue  | beige   | brown | grey (black) |
| tan   | black   | black | grey (black) |
| black | grey    | white | none         |

The black row needs no Fallback because `lblue` is the only office
Shirt with black pants, so that row can never collide. The two Week
shapes that do collide are blue-repeat (`striped`, `dblue`, `white`)
and tan-repeat (`dblue`, `white`, `black`); neither contains a
black-pants Shirt, which is why `grey` is always free when a Fallback
reaches for it.

**Home** — no Fallback column, and blue and tan deliberately share
black shoes:

| Pants | Sweater | Jacket | Shoes |
| ----- | ------- | ------ | ----- |
| blue  | yellow  | brown  | black |
| tan   | blue    | black  | black |
| black | beige   | black  | white |

A suggested YAML shape, keyed by pants under each Closet:

```yaml
office:
  pants:
    blue: { sweater: beige, shoes: brown, fallback: grey }
    tan: { sweater: black, shoes: black, fallback: grey }
    black: { sweater: grey, shoes: white }
home:
  pants:
    blue: { sweater: yellow, jacket: brown, shoes: black }
    tan: { sweater: blue, jacket: black, shoes: black }
    black: { sweater: beige, jacket: black, shoes: white }
```

- [x] Sweaters, jackets and shoes resolve from pants, per Closet, with three rows each, as authored under "The mappings" below
- [x] Every pants colour worn in a Closet has a row, and a Fallback naming a sweater that is no other row's primary is rejected at the config boundary
- [x] Office sweaters never repeat within a Monday-start Week
- [x] Office shoes never repeat within a Monday-start Week, as a consequence of the sweater rule rather than a separate check
- [x] When two office Shirts in a Week share pants, the later one takes its Fallback sweater
- [x] A Fallback moves the shoes along with the sweater
- [x] A Week containing four or more Office Days returns the primary sweater and marks the Response as containing an unavoidable repeat, rather than failing
- [x] Home Outfits resolve sweater and shoes from pants with no no-repeat rule applied
- [x] All five office Week shapes are asserted — the three that resolve cleanly and the two that require a Fallback
- [x] Friday Aug 21 2026 resolves to the black Shirt, tan pants, grey sweater and white shoes, and Monday Aug 24 starts a fresh Week with lblue taking grey cleanly
- [x] Tests assert only on the resolved Outfit, never on how a Week was walked
