# 07 — Settings

Type: grilling
Status: resolved
Blocked by: 02

## Question

How does the Settings page fit the new look?

The Office Weekdays (exactly three) and the Cold Threshold in °F, as an
iOS-style grouped list: what controls, and whether a change saves at
once or on a Save button.

## Answer

Settled by grilling. The Settings page in look B:

- **Shape**: the "Settings" title under the Day / Closet / Settings
  segmented control, then two filled cards, each with a 22 pt section
  head: "Office Weekdays", then "Cold Threshold". Nothing else goes on
  the page — no widget URL, About or Holidays.
- **Office Weekdays**: one row of seven round day chips, M T W T F S S,
  Office days filled in the label colour, Home days outlined — the same
  letters and meaning as the Day page's week strip. Under the card a
  grey footnote: "Changing these keeps every Rotation where it is."
- **Cold Threshold**: an iOS-style stepper, − 50°F +, the value large,
  one whole degree per tap, clamped to 0–100°F. A stored decimal shows
  rounded, and Save writes the whole degree.
- **Saving**: each card is still its own POST form. A Save capsule
  appears only once its card has changed; for the Office Weekdays it is
  enabled only at exactly three, with a footnote counting down ("Pick 1
  more"). Without JS, the Save buttons always show and the server
  refuses as today.
- **The server enforces the limits too**: a Cold Threshold outside
  0–100 or not a whole number is refused with the usual notice, beside
  "exactly three" (now in `CONTEXT.md`). Where the check lives is for
  the spec.
- **Notices, on every page**: a small capsule toast at the top, under
  the segmented control, that fades after a few seconds; JS strips
  `?notice` from the URL so a reload doesn't show it again.
