# Holidays

Status: ready-for-agent

Governed by ADR-0001, ADR-0005 and ADR-0007. Adds ADR-0011, recording
that Holidays are given, that they sit between the Office Weekdays and
the Day Type Overrides, and that they are the second thing — after the
Overrides — the derivation reads beyond the weekday pattern.

## Problem Statement

Every public holiday that lands on an Office Weekday is, as far as the
tool is concerned, an Office Day. The wearer is at home, and the tool
hands them an office Shirt, spends an office Position on a day nobody
went in, and resolves that Week's office sweaters as though they did.
The only remedy is to remember, ahead of time or after the fact, to run
`stay-home --on <the date>` for each one — Labor Day, Thanksgiving and
the Friday after it, Christmas — every year. Forgetting doesn't just
make one answer wrong: the Office Shirt Rotation advances on a day it
shouldn't have and the Home Shirt Rotation doesn't advance on a day it
should have, so every answer after it is off by one until a Reset.

The tool already knows the weekday pattern without being told. Public
holidays are just as knowable, and they are the same for every year the
wearer keeps their job.

## Solution

US federal holidays, plus the Friday after Thanksgiving, are Home Days
unless a Day Type Override says otherwise. When a holiday falls on a
weekend, the observed weekday — Friday for a Saturday, Monday for a
Sunday — is the Home Day, because that is the day off.

Nothing needs to be typed. `what2wear --on 2026-11-26` answers from the
Home Closet; `when office.shirt.white` skips straight over Thanksgiving
week's Thursday and Friday; the office sweater walk treats the holiday
as the Home Day it is. A wearer who does go in on a holiday says so with
`go-in`, exactly as they would for a Saturday.

## User Stories

### Holidays at home

1. As an office worker, I want a federal holiday on an Office Weekday
   to be a Home Day without my saying so, so that I'm not handed an
   office Shirt on a day I'm at home.
2. As an office worker, I want the Friday after Thanksgiving to be a
   Home Day, so that the day my employer gives me off is treated as one.
3. As an office worker, I want July 4 on a Saturday to make Friday
   July 3 a Home Day, so that the observed day off is the one that
   counts.
4. As an office worker, I want a holiday on a Sunday to make the
   following Monday a Home Day, so that the observed Monday is the one
   that counts.
5. As someone planning ahead, I want next year's holidays already
   known, so that `--on` a date months out is right without my
   recording anything.
6. As someone asking about the past, I want past holidays to have been
   Home Days, so that the past-date answer is consistent with the
   derivation.

### Rotations stay honest

7. As a wearer, I want a holiday not to advance the Office Shirt
   Rotation, so that the office Shirt I'd have worn that day is the one
   I wear next time I go in.
8. As a wearer, I want a holiday to advance the Home Shirt Rotation, so
   that the day I spent at home spent a home Shirt.
9. As a wearer, I want a holiday to take its turn in the Home Outerwear
   Rotation, so that it moves on the same Home Days the Home Shirt
   Rotation does.
10. As a wearer in a holiday Week, I want the office sweater walk to
    skip the holiday, so that the Fallback isn't triggered by a sweater
    I didn't wear.
11. As someone asking `when`, I want the search to step over holidays,
    so that the date it names is a day I'll actually be in that Closet.

### Overriding them

12. As someone who works a holiday, I want `go-in --on <holiday>` to make
    it an Office Day, so that holidays are defaults and not rules.
13. As someone who worked a holiday, I want that record kept, so that
    recording it isn't silently dropped as redundant.
14. As someone who runs `stay-home` on a holiday, I want nothing
    recorded, so that the State doesn't accumulate facts the tool
    already knows.
15. As someone whose employer skips a federal holiday — Columbus Day,
    Veterans Day — I want `go-in` to be how I say so, so that one
    mechanism covers every exception.
16. As someone who already recorded `stay-home` on past holidays, I want
    those records to keep working, so that nothing I told the tool
    before this change becomes wrong.

### Upgrading

17. As the wearer upgrading, I want to be told that today's Shirts may
    move once, so that a changed answer the morning after the upgrade
    isn't a surprise.
18. As the wearer upgrading, I want a single `reset` per Closet to put
    things right, so that there is no migration to run.
19. As the wearer upgrading, I want my State file to read unchanged, so
    that nothing I've told the tool is lost.

### Keeping the tool the shape it is

20. As a reader of the codebase, I want the holidays to come from a
    maintained library rather than date arithmetic written here, so that
    the Easter-style edge cases of moving holidays are someone else's.
21. As a reader of the codebase, I want holidays to enter the day-type
    derivation in exactly one place, so that `answer`, `when`,
    `record_override` and the Position count all agree.
22. As a reader of the codebase, I want the Position count to keep its
    whole-week shortcut, so that `when`'s year-long search stays fast.

## Implementation Decisions

### Where Holidays sit

A date's kind is decided in three layers, each overriding the one below:

1. The **Office Weekdays** — Office if the weekday is one of them.
2. **Holidays** — Home, whatever the weekday.
3. **Day Type Overrides** — whatever was recorded.

The existing weekday-only function stays weekday-only. A new function
gives the default kind (layers 1 and 2), and the existing day-type
function falls through to it rather than to the weekday pattern.

### Which Holidays

- The `holidays` package, `US` calendar, no subdivision, with its
  default `observed=True`. That is the eleven federal holidays and their
  observed weekdays.
- Plus the day after each Thanksgiving, found by name from the same
  calendar rather than computed separately.
- The set is **given**, not told, per ADR-0005: it is a fact about the
  one wearer the tool dresses, and a change to it is a commit. There is
  no command to add or remove a Holiday, and nothing about Holidays is
  written to the State.
- Observed dates are the library's, which are the federal rule. They do
  not follow custom Office Weekdays: a Saturday holiday observes on
  Friday even if Friday is not an Office Weekday, which is harmless
  because Friday is then already a Home Day.
- `holidays` becomes a runtime dependency. It replaces rule code that
  would otherwise live here, which is the trade the wearer prefers.

### The Position count

The count of days of a kind between an Anchor and a date keeps its
whole-weeks arithmetic, which reads only the weekday pattern, and then
corrects for the dates that differ from it. That correction today runs
over the recorded Overrides; it now runs over the Overrides **and** the
Holidays in the range, comparing each date's actual kind against its
weekday-only kind. A date that is both a Holiday and an Override is
counted once. A Holiday on a day the weekday pattern already makes a
Home Day contributes nothing, so the observed library's duplicate entry
for a weekend holiday is harmless.

The rejected alternative was to drop the shortcut and ask every date its
kind. It deletes the correction function but makes each Position cost a
walk from the Anchor, and `when` asks for up to 365 Positions.

### `record_override`

Its pruning compares against the default kind — weekday and Holiday —
rather than the weekday pattern alone. So `go-in` on a Holiday is kept,
and `stay-home` on a Holiday is dropped as already known. Existing
`stay-home` records on past Holidays become redundant but stay in the
State until the next `record_override` prunes them; they change no
answer either way.

### No re-anchoring

Introducing Holidays reclassifies every past Holiday between the current
Anchors and today, so today's Positions move once when this ships. This
arrives as code, not as a command, so ADR-0007's re-anchor-inside-the-
command approach has no place to run. Accepted: there is one wearer, it
happens once, and `reset` exists for exactly this. The README's upgrade
note says to check today's Shirts and Reset if they moved.

### `CONTEXT.md`

- New term **Holiday** under Calendar: a date the tool knows to be a
  Home Day without being told — the US federal holidays on their
  observed dates, and the Friday after Thanksgiving. Given, not told.
  A Day Type Override outranks it.
- **Home Day** gains that Holidays are Home Days unless overridden.
- **Office Day** gains that a Holiday is not one unless overridden.
- **Day Type Override** drops `holiday` from its _Avoid_ list, and its
  example list changes from "Holidays, leave, …" to "Leave, working a
  Holiday, …".

### ADR-0011

Holidays are given and sit between the Office Weekdays and the Day Type
Overrides. Amends ADR-0001's consequence that Overrides are "the only
thing left that the derivation reads out of the State" — still true of
the State, but the derivation now also reads a given calendar. Records
the one-time Position shift and why no migration was written.

## Testing Decisions

### What makes a good test here

Unchanged: drive a seam, assert on what comes back. Build an in-memory
`State` from `get_default_state(today)`; nothing mocked, no files, no
clock. Assert on day types, Shirts and dates — never on which holidays
the library returned or how the count was corrected.

### Seams

Zero new seams. Everything is observable through the existing core read
seam — `answer`, `get_due_shirt`, `get_due_date` — and `record_override`
on the recording seam. `tests/test_office_weekdays.py` is the model.

### Coverage

- Labor Day, Thanksgiving and the Friday after it answer as Home Days.
- A Saturday July 4 makes Friday July 3 a Home Day; a Sunday holiday
  makes Monday one.
- An Office Weekday that is not a Holiday still answers as an Office
  Day in a Holiday Week.
- The office Shirt due the day after a Holiday is the one that would
  have been due on the Holiday.
- The home Shirt on a Holiday is the next one in the Home Shirt
  Rotation, and the day after moves on from it.
- A Holiday takes a Home Outerwear Rotation turn.
- The office sweater walk in a Holiday Week does not see the Holiday.
- `go-in` on a Holiday makes it an Office Day, and the Rotations count
  it as one.
- `stay-home` on a Holiday leaves `overrides` empty.
- `get_due_date` never answers an office Shirt with a Holiday.
- A Position far past many Holidays equals the count of stepping
  through each date — the shortcut and the walk agree over a span of a
  few years.

### Existing tests that move

Labor Day, 2026-09-07, sits inside `tests/test_worked_calendar.py` and
`tests/test_resolution.py`. Their expectations on and after that date
are Office Day assumptions and change. Update them to the new truth
rather than overriding Labor Day back to an Office Day in the fixture —
the worked calendar should show what the tool actually says.

### Prior art

`tests/test_office_weekdays.py` for driving `answer` and `get_due_shirt`
across a changed calendar; `tests/test_worked_calendar.py` for a
day-by-day expected table.

## Out of Scope

- **Naming the Holiday in the output.** The answer says Home Day; it
  doesn't say why.
- **A command to add or remove Holidays.** Given, per ADR-0005.
  Exceptions are Overrides.
- **Other countries, states or employer calendars** beyond the Friday
  after Thanksgiving.
- **Christmas Eve, New Year's Eve** and other common non-federal days
  off. A commit if the wearer starts getting them.
- **A migration** to hold today's Positions still across the upgrade.
- **Pruning existing redundant Overrides on load.** They are pruned the
  next time anything is recorded.

## Further Notes

- The State file's schema and contents are unchanged.
- The README's Interface section gains a sentence saying Holidays are
  Home Days by default and `go-in` overrides one, and an upgrade note
  about the one-time Reset.
