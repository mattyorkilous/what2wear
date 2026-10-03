# 06 — Closet page with due dates and Swap

**What to build:** The wearer sees both Closets, when each Shirt is
next due, and can Swap two Shirts that share Pants. `when` stops being
a command. See `.scratch/phone/spec.md`.

**Blocked by:** 04 — Day page actions.

**Status:** done

- [x] Both Closets grouped by Pants Row
- [x] Each Shirt shows its next due date, linking to that Day page
- [x] A "Swap with…" `<select>` on each Shirt lists only Shirts
      sharing its Pants, so a refused Swap is never offered
- [x] A Swap uses the notice flow and carries Colors with Labels
