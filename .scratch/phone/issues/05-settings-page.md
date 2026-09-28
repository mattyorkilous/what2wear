# 05 — Settings page

**What to build:** The wearer sees and changes the Office Weekdays and
the Cold Threshold on one page. See `.scratch/phone/spec.md`.

**Blocked by:** 04 — Day page actions.

**Status:** done

- [x] Seven weekday checkboxes, the current three ticked
- [x] Anything but exactly three is refused with the core message
- [x] A note that changing them re-anchors every Rotation, so no
      Position moves
- [x] Cold Threshold as `<input type="number" step="any">` in °F,
      pre-filled
- [x] Writes use the notice flow, `recorded` vs `already` included
