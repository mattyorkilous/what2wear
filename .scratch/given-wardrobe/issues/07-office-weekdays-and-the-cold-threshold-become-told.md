# 07 — Office Weekdays and the Cold Threshold become told

**What to build:** The two facts that were given but are not about
clothes move into the State and gain a command each. Which three
weekdays are Office Days, and the temperature below which Outerwear is
worn, stop being source constants and start being things the wearer
says.

Per ADR-0007 this is not a crack in ADR-0005. The Wardrobe stays given
and absolute; neither of these was ever the Wardrobe. What is amended
is ADR-0006's "the Labels, the three Anchors and the Day Type
Overrides, and nothing else".

Office Weekdays must name **exactly three** weekdays. Only which three
is told — that there are three is structure and stays a source change,
for the reasons ADR-0007 records: at four or more the office no-repeat
rule is void rather than degraded, and at one or four the home cycle
collapses from nine weeks to three. Any weekday may be named, weekends
included.

The hard part is that changing Office Weekdays reclassifies the past,
so the count between an Anchor and today changes and every Rotation
moves by an arbitrary amount. The command therefore reads all three
Positions for today under the **old** Office Weekdays, then writes the
new ones together with all three Anchors moved to today at those
Positions. Nothing jumps, and the State keeps no history of what the
Office Weekdays used to be.

The Cold Threshold carries none of that. It moves no Position — a warm
Home Day already spends its turn — so it is a plain State field with a
command over it.

Both follow ticket 06's pattern for arriving in the State file: the
value in source becomes the starting value, and a State written before
this ticket reads as that starting value with nothing to migrate.

The command surface this adds:

```
what2wear office-weekdays              show the current three
what2wear office-weekdays mon wed fri  set them, and re-anchor
what2wear cold-threshold               show it
what2wear cold-threshold 55            set it
```

**Blocked by:** 06 — Home Outerwear alternation

Blocked on 06 rather than 05 because the re-anchor has to move all
three Anchors, and the Home Outerwear Anchor does not exist until 06.
Landing this first would leave a two-Anchor re-anchor for 06 to
remember to widen.

**Status:** ready-for-agent

- [ ] Office Weekdays and the Cold Threshold live in the State; the values in source are only the starting values used when no State file exists, and a State written before this ticket reads as them
- [ ] `office-weekdays mon wed fri` sets them and a later invocation answers from the new pattern
- [ ] Exactly three weekdays are required; any other count is refused with a message saying the count is a source change
- [ ] A repeated weekday names fewer than three days and is refused the same way
- [ ] Weekday names are accepted case-insensitively as three-letter abbreviations
- [ ] Any weekday may be named, weekends included
- [ ] Setting Office Weekdays moves all three Anchors to today at the Positions today held under the previous Office Weekdays, so no date's Shirt or Outerwear changes as a result of the change alone
- [ ] Restating the current Office Weekdays changes no answer for any date
- [ ] The output says that the Rotations were re-anchored, rather than leaving it to be noticed
- [ ] A mid-Week change resolving that Week's earlier Office Days under the new pattern, and therefore possibly moving that Week's Fallback, is asserted directly — ADR-0007 accepts it knowingly and the test is what stops it being "fixed"
- [ ] Day Type Overrides already recorded are left alone, including those now made redundant by the new pattern
- [ ] A fourth Office Day in a Week is still reachable by `go-in` and still flags an unavoidable repeat — the exactly-three rule does not retire that machinery
- [ ] `cold-threshold 55` sets it and a later invocation uses it to decide whether Outerwear is worn
- [ ] The Cold Threshold moves no Position: a Home Day that becomes warm under a new threshold still spends its Home Outerwear Rotation turn
- [ ] `office-weekdays` and `cold-threshold` with no argument print the current value and change nothing
- [ ] There is no generic setter command and no grouping of the two in the State file — they are two named facts alongside the Labels, the Anchors and the Overrides
- [ ] `wardrobe.py` keeps its name and gains a docstring saying it holds the Wardrobe's given shape *and* the starting values the State overlays — the Labels, the Anchors, the Office Weekdays and the Cold Threshold. Renaming it was considered and rejected: almost every reference is to a Wardrobe thing, and `tests/test_wardrobe.py` genuinely does test the Wardrobe, so a rename would make one name honest and another name wrong
- [ ] The README describes both commands and the exactly-three rule
