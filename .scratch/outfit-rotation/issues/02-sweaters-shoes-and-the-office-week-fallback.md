# 02 — Sweaters, shoes, and the office Week Fallback

**What to build:** Outfits become complete — Shirt, pants, shoes, and the sweater that goes with them. Sweaters, jackets and shoes are authored keyed by pants rather than by Shirt, so each Closet carries a three-row mapping instead of one row per Shirt.

On top of that sits the office rule: within a Monday-start Week, no sweater and no pair of shoes may repeat. A collision is always two office Shirts in the same Week sharing pants, and when one happens the second Shirt takes its Fallback sweater instead. Because office shoes are a bijection with office sweaters, the shoes follow the sweater automatically and the no-repeat guarantee for footwear comes for free.

Home has no no-repeat rule, and its shoe mapping is deliberately not a bijection.

**Blocked by:** 01 — Rotation for any date

**Status:** ready-for-agent

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

- [ ] Sweaters, jackets and shoes resolve from pants, per Closet, with three rows each, as authored under "The mappings" below
- [ ] Every pants colour worn in a Closet has a row, and a Fallback naming a sweater that is no other row's primary is rejected at the config boundary
- [ ] Office sweaters never repeat within a Monday-start Week
- [ ] Office shoes never repeat within a Monday-start Week, as a consequence of the sweater rule rather than a separate check
- [ ] When two office Shirts in a Week share pants, the later one takes its Fallback sweater
- [ ] A Fallback moves the shoes along with the sweater
- [ ] A Week containing four or more Office Days returns the primary sweater and marks the Response as containing an unavoidable repeat, rather than failing
- [ ] Home Outfits resolve sweater and shoes from pants with no no-repeat rule applied
- [ ] All five office Week shapes are asserted — the three that resolve cleanly and the two that require a Fallback
- [ ] Friday Aug 21 2026 resolves to the black Shirt, tan pants, grey sweater and white shoes, and Monday Aug 24 starts a fresh Week with lblue taking grey cleanly
- [ ] Tests assert only on the resolved Outfit, never on how a Week was walked

## Comments

### Mappings needed before this is buildable — 2026-08-15

The ticket describes the shape of the mapping but not its contents.
Six of the eighteen values are pinned by the worked calendar in the
spec; the rest have to be authored.

**Already fixed by the Aug 17–21 2026 sequence (office):**

| Pants | Sweater | Shoes | Fallback |
| ----- | ------- | ----- | -------- |
| blue  | ?       | ?     | ?        |
| tan   | black   | black | grey     |
| black | grey    | white | ?        |

tan's Fallback is `grey` because Friday Aug 21 (black shirt, tan
pants) resolves to the grey sweater and white shoes after Monday
Aug 17 (dblue, tan pants) took black — and the shoes move from black
to white alongside it.

**Still needed:**

1. Office blue pants — primary sweater and shoes.
2. Office Fallback sweaters for blue pants and black pants.
3. Home closet, all three rows — sweater, jacket and shoes for blue,
   tan and black pants. Two pants colours must share a pair of shoes,
   since the home shoe mapping is deliberately not a bijection.

**Two structural questions the names alone don't settle:**

4. Is a Fallback always another pants row's primary sweater, or may it
   be a fourth sweater outside the three rows? With 5 office Shirts
   and 3 Office Days there are exactly two Week shapes needing a
   Fallback: one where blue pants repeat, one where tan pants repeat.
   In the blue-repeat Week the blue and tan primaries are both already
   worn, so blue's Fallback can only be `grey` if Fallbacks must come
   from the three rows. If Fallbacks are extra sweaters, each needs
   its own shoes authored as well.
5. Are office shoes keyed by pants (three rows, and a Fallback borrows
   the donor row's shoes) or keyed by sweater? Both produce white
   shoes on Aug 21. Story 33 says pants-keyed, so three shoe rows is
   the default reading, but it only reconciles with "shoes follow the
   sweater" under answer 4-A above.

**Assumed unless corrected:**

- The Outfit carries a sweater unconditionally at this stage; the
  temperature gate arrives in 05.
- Home jackets are authored now but unused until 06.

### Answered — 2026-08-15

All eighteen values are now authored in "The mappings" above, and both
structural questions are settled:

1. Office blue pants: `beige` sweater, `brown` shoes.
2. Office blue falls back to `grey`, and therefore to white shoes.
   Office black never falls back — `lblue` is the only office Shirt
   with black pants, so only one office Outfit in five uses that row
   and it cannot collide. The row is authored without a Fallback
   rather than with an unreachable one.
3. Home rows: blue → `yellow` sweater, `brown` jacket, black shoes;
   tan → `blue` sweater, `black` jacket, black shoes; black → `beige`
   sweater, `black` jacket, white shoes. Blue and tan share black
   shoes, which is the deliberate non-bijection.
4. A Fallback can never be a fourth sweater — it is always another
   row's primary. This is what lets pants-keyed shoes follow the
   Fallback, and it is checkable at the config boundary.
5. Office shoes are keyed by pants. A Fallback resolves its shoes
   through the row whose primary sweater it names.

The two assumptions above stand: the Outfit carries a sweater
unconditionally at this stage, and home jackets are authored now but
not consulted until 06.

