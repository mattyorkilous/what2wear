# 01 — Replace by where a Garment hangs

**What to build:** Replace takes the key a Garment is filed under in
the State — where it hangs, such as `office.shirt.0` — instead of a
Label-spelled garment string. The Closet page passes the key from its
URL straight through, so the wearer sees the same form, confirmation
and refusals as before, and the trip from key to Label and back is
gone. See `.scratch/replace-by-key/spec.md`.

**Blocked by:** None — can start immediately.

**Status:** done

- [x] Replace takes the State, the key, the new Label, the Color and an
      optional stripe Color, and records the Label and Colors under
      that key.
- [x] A key nothing hangs at is refused with a What2wearError saying
      so, and nothing is recorded.
- [x] A Label containing `.` is still refused.
- [x] A Label held by another Garment of the same Closet and kind is
      still refused; the Garment's own current Label, and the same
      Label in another kind or Closet, are accepted.
- [x] The two refusals only a typed Label could reach ("no … is called
      …", "nothing is called …") are deleted, with the lookup by Label.
- [x] The Closet page's Replace route passes its key to Replace without
      building a garment string; it still 404s an unknown key and still
      names the Garment by its current Label in the confirmation.
- [x] Reset and Swap are unchanged and still take Labels.
- [x] The core Replace tests call Replace with keys, cover the new
      unknown-key refusal, and drop the two Label-spelling refusal
      tests; the other core tests that call Replace switch to keys.
- [x] The web Closet page Replace tests pass unchanged.
- [x] ADR-0010 gains a consequence that Replace takes the key now that
      the phone's Closet page is its only caller; ADR-0009 gains a
      one-line amendment note that the recording functions take what
      the interface hands over, which for Replace is the key.
- [x] Tests, ruff and ty pass.
