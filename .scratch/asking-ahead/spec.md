# Asking Ahead

Status: ready-for-agent

Governed by ADR-0001 and ADR-0008. Adds no ADR of its own; the one rule
this spec establishes about `--on` is recorded under Implementation
Decisions and in the README's Interface section.

## Problem Statement

The tool exists to answer ahead, and the one thing you have to type to
ask is the thing you don't know. You know you want Wednesday. You don't
know Wednesday's date, so asking what you'll wear on Wednesday means
leaving the tool, finding a calendar, and coming back with
`--on 2026-09-23`. The same friction sits on every dated command: `go-in
--on <the date of the Saturday I'm going in>`, `reset lblue --on <the
date of my next Office Day>`. ADR-0008 made `--on` the single way any
invocation names its date, which concentrated the whole problem into one
flag rather than spreading it — and left that flag speaking only ISO.

Separately, the tool answers one direction of one question. Given a
date, it names the Shirt. It has no way to answer the inverse: given a
Shirt, when do I next wear it. `show-closet` lists every Shirt you own
and marks the one each Closet is due to give you, which makes the
question obvious and still leaves you walking `--on` forward a day at a
time to answer it. The Position formula derives a date's Shirt in
closed form; the wearer reads it backwards by hand.

## Solution

`--on` learns words. `tomorrow`, `yesterday`, and any weekday name —
`wed`, `wednesday`, `Wednesday` all land on the soonest date with that
weekday, today included. ISO dates keep working, and because `--on` is
declared once on a shared parent parser, every dated command gets the
words at the same time: `go-in --on sat`, `reset lblue --on fri`,
`stay-home --on tomorrow`.

A new command answers the other direction. `when office.shirt.white`
searches its Closet's Shirt Rotation forward from today and prints the
next date that Shirt comes round — as a whole day, rendered exactly as
`what2wear --on <that date>` would render it, so the answer is the
Outfit and not just a date on its own.

## User Stories

### Saying which date I mean

1. As someone planning my week, I want `--on tomorrow`, so that asking
   about tomorrow doesn't require knowing tomorrow's date.
2. As someone planning my week, I want `--on wednesday`, so that I can
   name the day the way I think about it rather than the way a calendar
   files it.
3. As someone who types quickly, I want `--on wed` to mean the same
   thing as `--on wednesday`, so that I'm not made to spell it out.
4. As someone who capitalises out of habit, I want `--on Wednesday` to
   work, so that a shift key doesn't cost me an error.
5. As someone asking on a Wednesday, I want `--on wed` to mean today,
   so that naming the day I'm standing on doesn't silently skip a week.
6. As someone checking what I wore, I want `--on yesterday`, so that the
   past date ADR-0008 made answerable is as easy to name as a future
   one.
7. As someone who already knows the date, I want `--on 2026-09-23` to
   keep working, so that nothing I've learned stops working.
8. As someone recording a change of plan, I want `go-in --on sat`, so
   that the words work on the commands that record and not only on the
   one that asks.
9. As someone setting a Rotation right, I want `reset lblue --on fri`,
   so that ADR-0008's own motivating case — anchoring for the next time
   I go in, from a day I'm not going in — stops needing a calendar.
10. As someone who mistypes, I want an unrecognised word refused with a
    message naming what `--on` accepts, so that I can fix it from the
    error rather than from the README.
11. As someone reading `--help`, I want the words listed there, so that
    I find out they exist without being told.

### Asking when I next wear something

12. As someone with a favourite Shirt, I want to ask when I next wear
    it, so that I stop walking `--on` forward a day at a time to find
    out.
13. As someone reading `show-closet`, I want to copy a Garment's name
    straight into `when`, so that I don't have to remember a second
    spelling for the same Shirt.
14. As someone asking about a Shirt, I want the answer to be the whole
    day and not just a date, so that I get the Pants, the shoes and the
    Outerwear in the same breath.
15. As someone asking about a Shirt, I want to be told whether that date
    is an Office Day or a Home Day, so that the answer is
    self-explaining.
16. As someone asking on the day I'm already wearing it, I want to be
    told today, so that the answer can be trusted on the day it matters.
17. As someone who owns a `white` Shirt in both Closets, I want to say
    which Closet I mean, so that the answer is about the Shirt I was
    thinking of.
18. As someone who names a Shirt that Closet doesn't have, I want an
    error saying so, so that a typo doesn't get answered as though it
    were a question.
19. As someone who names a sweater or a pair of shoes, I want to be told
    `when` asks about Shirts, so that I learn the command's scope from
    the command.
20. As someone who has recorded a long stretch of Day Type Overrides, I
    want to be told plainly that the Shirt isn't worn in the next year,
    so that the tool answers rather than hangs or invents a date.
21. As someone asking about a Shirt whose next date is cold, I want the
    Outerwear named, so that the answer is as complete as any other.
22. As someone asking about a Shirt whose next date is past the forecast
    horizon, I want the Outerwear named with the cold/warm condition
    left open, so that it hedges the same way every other distant date
    does.
23. As someone asking twice in a row, I want the same answer both times,
    so that `when` is as deterministic as everything else here.

### Not being surprised

24. As someone who has read ADR-0008, I want a reason `when` takes no
    `--on`, so that the exception looks like a rule rather than an
    oversight.
25. As someone who notices the search ignores the forecast while the
    answer honours it, I want that written down, so that it reads as a
    decision rather than an inconsistency.
26. As someone who records a Day Type Override after asking, I want
    `when` to give a different answer next time, so that it reflects
    what I've told the tool rather than a cached one.
27. As someone who Resets a Rotation, I want `when` to follow, so that
    the two views of the same Rotation never disagree.
28. As someone who replaces a Garment's Label, I want `when` to take the
    new Label and not the old one, so that a Label is a Label
    everywhere.
29. As someone who Swaps two Shirts sharing Pants, I want `when` to
    answer for the Labels as they stand now, so that a cosmetic reorder
    shows up where I'd expect it to.

### Keeping the tool the shape it is

30. As someone who runs `when`, I want nothing recorded, so that asking
    a question never changes an answer.
31. As a reader of the codebase, I want `when` to reuse the renderer
    every other answer uses, so that one output format doesn't drift
    into two.
32. As a reader of the codebase, I want the search to live on the core
    read seam, so that the CLI stays the disposable renderer it was
    built to be.

## Implementation Decisions

### The rule `--on` now follows

A command takes `--on` when it acts *on* a date. `when` acts on a Shirt
and *produces* a date, so it takes none. This supersedes ADR-0008's
stated carve-out — "a Label is not dated" — which covers `replace` and
`swap` but says nothing about a command whose entire output is a date.
The new rule subsumes the old one and is recorded here and in the
README rather than in an ADR: it clarifies a boundary ADR-0008 already
drew rather than reversing one.

### Date words

- `--on` accepts three things: an ISO date as today, `tomorrow`,
  `yesterday`, and a weekday name.
- A weekday name is matched on its first three letters against the
  existing `WEEKDAYS` tuple, lowercased, so `wed`, `Wed`, `wednesday`
  and `Wednesday` all resolve. This reuses the vocabulary
  `set-office-weekdays` already has rather than introducing a second
  table, and deliberately does not consult `calendar.day_name`, which
  is locale-dependent.
- A weekday names the **soonest** date with that weekday, today
  included. On a Wednesday, `--on wed` is today.
- There is no `today`: a bare invocation already means today, so the
  word would be a second spelling of the default. `--on today` is
  therefore an error, which is an asymmetry with `tomorrow` accepted
  knowingly.
- No `next wednesday`, `last friday`, `in 3 days` or month/day forms.
  Anything a single word can't say is said with an ISO date.
- The words are parsed where `--on` is declared, on the shared parent
  parser, so every dated command gains them at once and none gains them
  separately. The parser already receives `today`; the date parser is
  bound to it.
- `--on`'s metavar changes from `YYYY-MM-DD` to `DATE`, with the
  accepted words named in its help text.
- An unrecognised value keeps the existing failure: an argparse type
  error, exit 2, with a message naming what is accepted.
- ADR-0008's ordering caveat is unchanged — a subcommand's own default
  still overwrites an `--on` given ahead of it, so `what2wear --on
  tomorrow go-in` still records today.

### `when`

- `what2wear when office.shirt.white`. One positional, the same dotted
  Garment name `replace` takes and `show-closet` prints in its last
  column, so a name is copied rather than invented.
- **Shirts only.** A name whose kind is not `shirt` — `office.sweater.
  beige`, `home.shoes.black`, `pants.blue` — is refused with a message
  saying `when` asks about Shirts. Sweaters, shoes and jackets follow
  from Pants during Resolution rather than being picked by a Rotation,
  so "when do I next wear them" is a different question with a
  different shape, and is out of scope here.
- The Closet is always named, because a Label alone is unique only
  within a Closet and a kind: `office.shirt.white` and
  `home.shirt.white` are two different Shirts.
- **No `--on`.** The search runs forward from today, today included.
- **The search ignores the forecast.** It asks where the Shirt
  Rotation puts a Shirt, which is knowable a year out; the forecast
  reaches sixteen days. A search that consulted the weather would give
  a different answer depending on when it was asked, which is the
  property the derived-Position design exists to avoid.
- **The answer honours the forecast.** Once the date is found, the
  shell renders it through `answer` and the existing renderer, so the
  found date prints its Outerwear, or no Outerwear, or the `if it's
  cold` hedge, exactly as `what2wear --on <that date>` would. Search and
  answer treating the weather differently is deliberate and is the
  reason it is written down.
- **Horizon: a year**, as a module constant in core. In the ordinary
  case it is unreachable — the Office Weekdays are always exactly
  three, so both kinds of day recur every week, and five office Shirts
  over three Office Days or nine home Shirts over four Home Days both
  come round inside three weeks. Only a deliberate stretch of Day Type
  Overrides can exhaust it.
- **Exhausting the horizon is not an error.** It prints a plain line on
  stdout at exit 0 — `no office day in the next year wears white` —
  because the question was well formed and the answer is true. Exit 2
  stays for naming something the Wardrobe doesn't have.
- **`when` records nothing.** No State is written and no confirmation
  line is printed.

### The core seam

The read seam gains a third function beside `answer` and
`get_due_shirt`:

```
get_due_date(state, day_type, shirt, today) -> date | None
```

It pairs with `get_due_shirt` by name and by shape — one asks a date
for its Shirt, the other asks a Shirt for its date. It takes the Label
the way `reset(state, shirt, on)` does, walks dates from `today`
forward skipping days of the other kind, and returns the first date
whose due Shirt carries that Label, or `None` at the horizon. An
unknown Label raises the error `_get_shirt_position` already raises.

`today` is a parameter rather than a clock read, which is what keeps
the function on the pure seam. A consequence worth naming: core will
answer from any date handed to it, so `when`'s refusal of `--on` is a
shell rule, not a core one.

### The shell

`when` is a third shape of command. It is not display-only — it renders
a `Response` — and it is not record-then-answer, since it records
nothing. `run` therefore chooses the date it hands to `answer` rather
than always using `args.on`, and short-circuits to the plain
not-found line when the search returns nothing.

### `CONTEXT.md`

One sentence is appended to **Shirt Rotation**: that it reads either
way — a date names the Shirt due on it, and a Shirt names the next date
it is due. No new term. The date words add nothing: a word for a date
is a spelling, not a concept, and `CONTEXT.md` is a glossary about the
wearer's clothes rather than about the tool's surface.

## Testing Decisions

### What makes a good test here

Unchanged from the existing suite: drive a seam, assert on what comes
back, never on how it got there. Core tests build an in-memory `State`
from `get_default_state(today)` with an explicit `today`; nothing is
mocked, no files are touched, no clock is read outside the shell's own
tests. A `when` test must not assert how many dates were walked or in
what order.

### Seams

Zero new seams. The date words are shell-only and have no core
counterpart, so they are tested through `cli.run` — the existing shell
seam, already driven end-to-end by `tests/test_cli.py`. `_parse_date`
is not tested directly; nothing in the suite reaches into shell
privates. `get_due_date` is a new function on the existing core read
seam, driven the way every other core test drives it.

### Coverage

**Date words, through `cli.run`:**

- `--on tomorrow` and `--on yesterday` print the expected date, and
  `yesterday` still carries the past-date note.
- Every weekday form resolves: `wed`, `Wed`, `wednesday`, `WEDNESDAY`.
- A weekday word from each of the seven days lands on a date with that
  weekday, at most six days out.
- Asking for today's own weekday returns today, not seven days on.
- `--on today` is refused, pinning the deliberate asymmetry so it isn't
  "fixed" later.
- A word that is not a date and not a weekday is refused at exit 2.
- The words work on a recording command — `go-in --on sat` records the
  Saturday, confirmed by the confirmation line naming that date.
- `reset <label> --on fri` moves the Anchor to the coming Friday.

**The search, through `get_due_date`:**

- A Shirt due today returns today.
- Each Shirt in each Closet returns a date whose due Shirt is that
  Shirt, and no earlier date of that kind has it.
- Days of the other kind are skipped: an office Shirt never answers
  with a Home Day.
- The office Closet's five Shirts and the home Closet's nine return
  five and nine distinct dates in Rotation order.
- A Day Type Override pushes the answer out — recording `stay-home`
  over the date that would have answered moves it to the next Office
  Day.
- A stretch of Overrides covering the horizon returns `None`.
- A Reset moves what `get_due_date` answers, and a Reset to that Shirt
  makes it answer the Reset's date.
- A Replace changes which Label answers; the new Label finds the Shirt
  and the old one errors.
- A Swap of two Shirts sharing Pants exchanges the two dates.
- An unknown Label raises `What2wearError`.
- Changing the Office Weekdays leaves the answer consistent with where
  the Rotation stands, since every Anchor moves with the change.

**`when`, through `cli.run`:**

- The output is the found date's whole Outfit, matching what
  `--on <that date>` prints for the same date.
- A Shirt due today prints today.
- `home.shirt.white` and `office.shirt.white` answer differently.
- A non-Shirt name — a sweater, shoes, Pants — is refused with a
  message naming Shirts.
- An unknown Label exits 2 on stderr.
- Exhausting the horizon prints the plain line on stdout at exit 0.
- `when` takes no `--on`: passing one is an argparse error.
- Running `when` writes no State file, on a fresh installation that had
  none.
- The found date's Outerwear hedges when it is past the forecast
  horizon, and resolves when a forecast is supplied for it.

### Prior art

`tests/test_cli.py` for both shell halves — `test_a_malformed_date_is_
rejected` for the refusal path, `test_a_future_date_prints_that_date`
for the date-echo assertion, and its existing `_today()` and `_next()`
helpers for computing expected dates without reading a clock twice.
`tests/test_office_weekdays.py` is the prior art for driving
`get_due_shirt` directly and is the closest model for a new
`tests/test_when.py`. `tests/test_resets.py`, `test_replace.py` and
`test_swap.py` are the models for the "does this command move what
`when` says" cases.

## Out of Scope

- **`when` for anything but a Shirt.** Sweaters, shoes, jackets and
  Pants are settled by Resolution from the Pants a Shirt is welded to,
  not picked by a Rotation, so asking when you next wear one is a
  question about a set of Shirts rather than about a Position. Refused
  with a message rather than partially supported.
- **A bare Label without a Closet.** `when white` would have to pick
  between two Shirts or answer about both; naming the Closet is one
  word and removes the question.
- **`when` for the Home Outerwear Rotation.** "When is my next jacket
  day" is a reasonable question and a different command; the Rotation
  it walks has no Labels to name it by.
- **`when` taking `--on`.** Searching forward from a date other than
  today is speculative; the rule above says why it is refused rather
  than merely absent.
- **A weather-aware search.** "When do I next actually wear the brown
  jacket" would depend on when it was asked and could only ever answer
  sixteen days out.
- **Listing every upcoming date.** `when` gives the first. A second
  and third are a different command with a different shape.
- **Date expressions beyond a single word.** `next wednesday`, `last
  friday`, `in 3 days`, `sep 23`, `+7`.
- **Full weekday names from the locale.** The three-letter prefix match
  is English, as `set-office-weekdays` already is.
- **`--on today`.** Covered by the bare invocation.
- **Any change to how a Position is derived.** Both features are
  readers; neither moves an Anchor or touches the formula.

## Further Notes

- Neither feature changes the State file, its schema or its contents. A
  State written before this lands reads identically after.
- The two features are independent and can land in either order. The
  date words are the smaller change and touch only the parser; `when`
  touches core, the shell, `CONTEXT.md` and the README.
- `when` is the only interrogative command on a surface otherwise made
  of imperatives — `go-in`, `reset`, `replace`, `swap`, `show-closet`.
  That is deliberate: it is the only command that asks rather than
  tells.
- The README's Interface section gains both, and the sentence recording
  why `when` takes no `--on`.
- The CLI remains deliberately disposable, to be replaced by something
  usable from a phone. `when`'s search living in core rather than in
  the shell is what makes it survive that replacement.
