# 02 — `when` searches the Shirt Rotation

**What to build:** The wearer can ask the inverse of the question the
tool already answers. Today it takes a date and names a Shirt;
`what2wear when office.shirt.white` takes a Shirt and names the date it
is next due — printed as the whole Outfit for that date, rendered
exactly as `what2wear --on <that date>` would render it, so the answer
carries the Pants, the shoes, the day type and the Outerwear rather
than being a bare date.

The Shirt is named the way `show-closet` prints it and `replace` takes
it, so a name is copied rather than invented, and the Closet is always
named because a Label alone is unique only within a Closet and a kind.

`when` takes no `--on`. It searches forward from today, today included,
so a Shirt due today answers today. The rule that earns the exception:
**a command takes `--on` when it acts *on* a date; `when` acts on a
Shirt and *produces* a date.** This sharpens ADR-0008's stated
carve-out — "a Label is not dated" — which covers `replace` and `swap`
but says nothing about a command whose entire output is a date. It is
recorded in the README rather than in an ADR, because it clarifies a
boundary ADR-0008 already drew rather than reversing one.

The search ignores the forecast, because it asks where the Shirt
Rotation puts a Shirt, which is knowable a year out while the forecast
reaches sixteen days. The **answer** honours the forecast, because it
goes through the renderer every other answer goes through. Search and
answer treating the weather differently is deliberate.

Core gains a third function on the read seam beside `answer` and
`get_due_shirt`:

```
get_due_date(state, day_type, shirt, today) -> date | None
```

It pairs with `get_due_shirt` by name and by shape — one asks a date
for its Shirt, the other asks a Shirt for its date — takes the Label
the way `reset(state, shirt, on)` does, and takes `today` as a
parameter rather than reading a clock, which is what keeps it pure. A
consequence worth knowing: core will answer from any date handed to it,
so `when`'s refusal of `--on` is a shell rule, not a core one.

`when` records nothing. No State is written and no confirmation line is
printed. It is the only interrogative on a command surface otherwise
made of imperatives, which is deliberate.

**Blocked by:** None — can start immediately.

**Status:** done

### The search

- [x] `get_due_date` returns today when the Shirt is due today
- [x] Each Shirt in each Closet returns a date whose due Shirt is that
      Shirt, with no earlier date of that kind carrying it
- [x] Days of the other kind are skipped — an office Shirt never
      answers with a Home Day
- [x] The office Closet's five Shirts and the home Closet's nine return
      five and nine distinct dates in Rotation order
- [x] A Day Type Override pushes the answer out: `stay-home` on the
      date that would have answered moves it to the next Office Day
- [x] A stretch of Day Type Overrides covering the horizon returns
      `None`
- [x] A Reset moves what `get_due_date` answers, and a Reset to that
      Shirt makes it answer the Reset's date
- [x] A Replace changes which Label answers — the new Label finds the
      Shirt, the old one errors
- [x] A Swap of two Shirts sharing Pants exchanges their two dates
- [x] An unknown Label raises `What2wearError`
- [x] Changing the Office Weekdays leaves the answer consistent with
      where the Rotation stands
- [x] The horizon is a year, as a module constant in core
- [x] No test asserts how many dates were walked or in what order

### The command

- [x] `when office.shirt.white` prints the found date's whole Outfit,
      matching what `--on <that date>` prints for that date
- [x] A Shirt due today prints today
- [x] `home.shirt.white` and `office.shirt.white` answer differently
- [x] A name whose kind is not `shirt` — a sweater, shoes, or
      `pants.blue` — is refused with a message saying `when` asks about
      Shirts
- [x] An unknown Label exits 2 on stderr
- [x] Exhausting the horizon prints a plain line on stdout at exit 0,
      naming the Closet, the year and the Label
- [x] `when` takes no `--on`: passing one is an argparse error
- [x] `when` writes no State file, on a fresh installation that had none
- [x] The found date's Outerwear hedges when it is past the forecast
      horizon, and resolves when a forecast is supplied for it

### Documentation

- [x] `CONTEXT.md` gains one sentence on **Shirt Rotation**: it reads
      either way — a date names the Shirt due on it, and a Shirt names
      the next date it is due. No new term.
- [x] The README's Interface section gains `when`, and the sentence
      recording why it takes no `--on`
- [x] No ADR
