# 05 — Settings page

**What to build:** The wearer sees and changes the Office Weekdays and
the Cold Threshold on one page. See `.scratch/phone/spec.md`.

**Blocked by:** 04 — Day page actions.

**Status:** ready-for-agent

- [ ] Seven weekday checkboxes, the current three ticked
- [ ] Anything but exactly three is refused with the core message
- [ ] A note that changing them re-anchors every Rotation, so no
      Position moves
- [ ] Cold Threshold as `<input type="number" step="any">` in °F,
      pre-filled
- [ ] Writes use the notice flow, `recorded` vs `already` included
