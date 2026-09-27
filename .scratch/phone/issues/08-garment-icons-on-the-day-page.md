# 08 — Garment icons on the Day page

**What to build:** The Day page draws each Garment as an icon in its
Color, followed by its full name ("Light Blue Shirt"), the look picked
in the emoji prototype (variant E). The path data is the one source of
shapes the widget will also draw from. See `.scratch/phone/spec.md`.

**Blocked by:** 03 — Today's Day page on PythonAnywhere.

**Status:** ready-for-agent

- [ ] Each kind (shirt, pants, sweater, jacket, shoes) has a `shape`
      and a `detail` path in a 32×32 box, using only `M`, `L`, `Q`, `Z`
- [ ] A striped Garment adds a `pattern` path: vertical rectangles
      inside the torso (about x 8–24, y 13–28), filled with the stripe
      Color
- [ ] No dashes: the shirt placket is short segments
- [ ] Drawn as inline SVG in three layers: fill shape, fill pattern,
      stroke detail
- [ ] Outerwear worn only if it's cold is dimmed
