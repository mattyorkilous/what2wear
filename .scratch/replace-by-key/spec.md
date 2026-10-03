# Replace by where a Garment hangs

Status: done

Governed by ADR-0006, ADR-0009, ADR-0010 and ADR-0012. Amends ADR-0010
with a consequence recording that Replace takes the key, and ADR-0009
with a note that the phone page hands over the key rather than a value
the wearer typed. Adds no ADR and no domain term.

## Problem Statement

The CLI is gone, and the Closet page is now the only way a wearer
Replaces a Garment. That page already knows exactly which Garment it is
editing: where it hangs is in the URL (`office.shirt.0`), the one
address that stays put while the wearer retypes its Label. But the
recording function behind it still has the interface the CLI needed,
where the wearer typed the Garment's Closet, kind and current Label.
So the web shell reads the State to find the Garment's current Label,
spells a Label-shaped string out of it, and hands that over; Replace
splits the string apart again and scans every Label in that Closet and
kind to find the key it started from.

Nothing the wearer sees is wrong today. The cost is to the reader and
to the next change: Replace's interface is wider than its job, it
carries two refusals ("no office shirt is called 'puce'", "nothing is
called 'White'") that the phone can never trigger, and the trip from
key to Label and back is a place for a bug to hide — a Label containing
the wrong character, or two Garments briefly sharing a Label, is
exactly what that lookup would trip over.

## Solution

Replace takes where the Garment hangs, the same key the State files its
Label and Color under, and the Closet page passes the key from its URL
straight through. The wearer sees no change: the same form, the same
confirmation, the same refusals for a Label that won't do.

## User Stories

1. As a wearer, I want to Replace a Garment from its Closet page and see its new Label everywhere, so that the tool calls my clothes what I call them.
2. As a wearer, I want to Replace a Garment's Color with its Label, so that it is drawn as it looks.
3. As a wearer, I want to give a striped Garment a stripe Color, so that its icon shows its stripes.
4. As a wearer, I want to untick striped and have the stripe Color dropped, so that a plain Garment is drawn plain.
5. As a wearer, I want restating a Garment's current Label and Color to say "Already", so that I know nothing was written.
6. As a wearer, I want a Label containing `.` refused with the form shown again and my input kept, so that I can fix it without retyping.
7. As a wearer, I want a Label another Garment of the same Closet and kind already has refused, so that two Shirts never share a name in one Closet.
8. As a wearer, I want the same Label allowed for a Garment of a different kind or in the other Closet, so that an office sweater and office shoes can both be Black.
9. As a wearer, I want giving a Garment its own current Label with a new Color accepted, so that I can recolor without renaming.
10. As a wearer, I want the Home shoes worn with two pairs of Pants to change together when I Replace them, so that one pair of shoes stays one Garment.
11. As a wearer, I want a Replace to leave every Rotation where it was, so that renaming a Shirt never changes what I wear on any date.
12. As a wearer, I want a Closet page URL naming nowhere a Garment hangs to be a plain 404, so that a mistyped link doesn't pretend to work.
13. As a wearer, I want a Replace I made before this change to still read the same from the State, so that nothing I told the tool is lost.
14. As the tool's maintainer, I want Replace to take the key the State is filed under, so that its interface matches what its only caller holds.
15. As the tool's maintainer, I want Replace to refuse a key nothing hangs at, so that a bad call can never write a made-up Garment into the State file.
16. As the tool's maintainer, I want the refusals that only a typed Label could reach deleted, so that every refusal left is one a caller can actually hit.
17. As the tool's maintainer, I want Reset and Swap left on Labels, so that the forms that post Labels keep working unchanged.
18. As a future reader, I want ADR-0010 and ADR-0009 to say why Replace takes the key, so that a later review doesn't put the Label spelling back.

## Implementation Decisions

- **Replace's interface becomes `replace_(state, key, label, color,
  stripe_color=None)`.** `key` is a plain string in the spelling the
  State already uses for `labels` and `colors` (`office.shirt.0`,
  `pants.1`). No typed key is introduced: nothing else would use one,
  and the State already documents the spelling.
- **Replace refuses an unknown key** with a What2wearError saying
  nothing hangs there. The web route 404s first, but Replace is public
  and without the check a bad key would be silently added to the State
  and written to the file.
- **The remaining refusals stay, in this order:** a Label containing
  `.`; then a Label already held by another Garment whose key shares
  this key's Closet and kind (everything before the last `.`). The
  Garment's own current Label is not a clash.
- **The Label-spelled lookup goes.** The two refusals for a typed
  Label that names nothing ("no office shirt is called …", "nothing is
  called …") are deleted with it.
- **The Closet page's Replace route passes the key from its URL
  straight to Replace.** It no longer works out the Garment's scope and
  current Label to build a garment string. It still 404s an unknown key
  before calling, and still uses the current Label to name the Garment
  in its confirmation ("the Office White Shirt replaced with …").
- **Reset and Swap keep taking Labels.** Their forms post Labels and
  their refusals speak in Labels.
- **Key spelling elsewhere is untouched.** The other places that build
  a key are one-line format strings whose meaning is visible where they
  sit; wrapping them in a helper would move complexity rather than
  concentrate it.
- **No State schema change.** The file is keyed exactly as before, so
  no migration and no shim.
- **Docs:** ADR-0010 gains a consequence that Replace takes the key now
  that the phone's Closet page is its only caller. ADR-0009 gains a
  one-line amendment note that the recording functions take what the
  interface hands over, which for Replace is the key from the URL.
  CONTEXT.md does not change.

## Testing Decisions

- A good test drives the change through an existing seam and checks
  what the wearer or the State would see — the recorded Label and
  Color, the refusal message, the page's response — never which
  private function was called.
- **Core recording seam (primary).** The Replace tests are rewritten
  to call Replace with keys. They cover: a new Label and Color
  recorded; a stripe Color recorded and dropped; a `.` refused; a
  Label held by another Garment of the same Closet and kind refused; a
  same Label in another kind or Closet accepted; a Garment's own Label
  with a new Color accepted; the shared Home shoes changing for both
  rows; a Replace moving no Rotation; and the new refusal for a key
  nothing hangs at. The two tests for Label-spelling refusals are
  deleted.
- **Other core tests that call Replace** (outerwear, store round-trip,
  asking when a Shirt is due) switch their calls to keys and are
  otherwise unchanged.
- **Web shell seam (regression).** The existing Closet page Replace
  tests, driven through the Flask test client, already post to the
  Garment's key and stay as they are: prefilled form, recorded Label
  and Colors, unticked striped, "Already", refusal re-shows the form,
  bad Color is a 400, unknown key is a 404.
- Prior art: the existing Replace and Swap tests for the core seam;
  the Closet page tests in the web suite for the shell.

## Out of Scope

- Moving Reset or Swap onto keys.
- Key build/split helpers in the Wardrobe module, or a typed key.
- Resolution carrying keys instead of given names, and retiring the
  given-name-to-key map (candidate 3 of the 2026-10-03 architecture
  review; touches ADR-0012).
- A Closet query in core that the Closet page renders (candidate 2 of
  the same review).

## Further Notes

Came out of the 2026-10-03 architecture review, where this was the top
recommendation: the last CLI-shaped interface on the recording seam
after the CLI was deleted. It is mostly deletion, and it makes both
out-of-scope candidates easier if they are picked up later.
