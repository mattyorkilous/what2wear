# 01 — Outfits carry Garments with a told Color

**What to build:** An Outfit names each of its garments as a Garment
carrying its Label, its Color and an optional stripe Color, instead of
a bare Label. Every given Garment has a starting Color beside its
starting Label (from the emoji prototype's `FILL` table), and the State
gains a `colors` map keyed like `labels`, written only where it differs
from the given. A Swap exchanges Colors with Labels. The CLI still
prints Labels exactly as before. This is the prefactor the web shell
builds on. See `.scratch/phone/spec.md`.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] `Garment(label, color, stripe_color=None)`; `Outfit.shirt`,
      `.pants`, `.shoes` are Garments and `.sweater`/`.jacket` are
      `Garment | None`
- [ ] `answer` looks up the Color where it looks up the Label; the
      given `Shirt`/`PantsRow`/`Closet` structure is untouched
- [ ] Colors are `#rrggbb` strings; every given Garment has one, the
      striped Shirt also a stripe Color
- [ ] `colors` round-trips through the store, only changed entries are
      written, and a file without `colors` reads with the given Colors
- [ ] `swap` exchanges the two Shirts' `colors` entries with their
      `labels` entries
- [ ] Existing assertions move mechanically from `outfit.<kind> == "…"`
      to `outfit.<kind>.label == "…"`; the suite, ruff and ty are green
- [ ] New ADR "Garments carry a told Color" (the State gains `colors`;
      reverses "the Label is the whole of what the tool prints")
- [ ] CONTEXT.md gains **Color** (told with its Label, optional stripe
      Color), cross-linked with Label; Garment's "its Label is the only
      thing about it that can change" becomes "its Label and Color"
