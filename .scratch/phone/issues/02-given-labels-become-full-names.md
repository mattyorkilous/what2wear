# 02 — Given Labels become full names

**What to build:** The given Wardrobe's Labels are the full names the
wearer would say — "Light Blue", not `lblue` — without the kind. The
live State file, whose `labels` is empty, reads them unchanged, so no
conversion is needed. See `.scratch/phone/spec.md`.

**Blocked by:** 01 — Outfits carry Garments with a told Color.

**Status:** ready-for-agent

- [ ] Every given Label is a full name with no `.` in it
- [ ] One Label per Closet and kind still holds
- [ ] Tests that name given Labels are swept to the full names; the
      suite is green
- [ ] A State file with `"labels": {}` answers with the full names
- [ ] CONTEXT.md **Label** becomes "what a Garment is called, in words
      you'd say (Light Blue)", no longer "the whole of what the tool
      prints", with `color` dropped from its _Avoid_
