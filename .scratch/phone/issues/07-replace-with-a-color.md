# 07 — Replace with a Color

**What to build:** The wearer taps a Garment on the Closet page and
gives it a new Label and Color, optionally striped. See
`.scratch/phone/spec.md`.

**Blocked by:** 02 — Given Labels become full names; 06 — Closet page
with due dates and Swap.

**Status:** ready-for-agent

- [ ] `replace_(state, garment, label, color, stripe_color=None)`
      records the Color with the Label
- [ ] A Label containing `.` is refused with a message
- [ ] A Label held by another Garment of the same kind in that Closet
      is still refused
- [ ] The form: a name box pre-filled with the Label, an
      `<input type="color">` pre-filled with the Color, and a "Striped"
      checkbox with a second color input, ignored when unchecked; no JS
- [ ] Uses the notice flow; a refusal re-shows the form with the message
