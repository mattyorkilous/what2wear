# 10 — Full names and colours for Labels

Type: grilling
Status: resolved
Blocked by: none

## Question

The widget prints "Light Blue Shirt", not `lblue`, and fills each icon
with the Garment's colour (see
[What an emoji Outfit looks like](04-emoji-outfit.md)). A Label is free
text that `replace` can change to anything, and CONTEXT.md calls the
Label "the whole of what the tool prints at you". So:

- Where do a Label's full name and colour come from: a given table in
  the source, something told and stored in the State (e.g. `replace`
  takes a colour), or the Labels themselves becoming full names?
- What shows for a Label the table doesn't know: a neutral icon and the
  Label as written?
- Does CONTEXT.md's Label entry change?
- A pattern is a Label's too: per
  [Drawing the garment icons on the phone](09-drawing-the-icons.md), an
  icon is a `fill` plus an optional `pattern` with a `pattern_fill`
  (today only `striped`: vertical bars). Where does that come from?

## Answer

**The Label becomes the full name, and each Garment gains a told
Color, stored in the State.** Settled by grilling on 2026-09-27.

- **Label = full name**, as typed, without the kind: "Light Blue"; the
  page and widget append it ("Light Blue Shirt"). Nothing is derived.
  With the CLI gone nobody types `office.shirt.lblue`, so a short word
  buys nothing. One Label per Closet and kind still holds.
- **Color in the State:** a `colors` map keyed like `labels`, plus an
  optional stripe Color for a striped Garment (it becomes `pattern` /
  `pattern_fill` in
  [Drawing the garment icons on the phone](09-drawing-the-icons.md)).
  The given Wardrobe in `wardrobe.py` supplies each Garment's starting
  Color beside its starting Label (the prototype's `FILL` table is that
  data). Every Garment always has a Color, so there's no unknown-Label
  grey.
- **Replace** takes a Label and a Color (and an optional stripe Color).
  The form: a name box pre-filled with the Label, an
  `<input type="color">` pre-filled with the Color, and a "Striped"
  checkbox with a second color input, ignored when unchecked. No JS.
- **Swap** exchanges Colors (and stripe Colors) along with Labels: a
  Label and its Colors always travel together.
- **No `.` in a Label:** `replace_` refuses one with a message, since
  a Garment is addressed as `office.shirt.<label>` and split on the
  last dot.
- **Existing Labels** (`lblue` …) are converted once, with Colors from
  the prototype's table, when the State moves; see
  [Moving and backing up the State](11-moving-and-backing-up-the-state.md).
  No short-Label compatibility.
- **Spelling:** `color` everywhere new (term, State key, form fields,
  JSON).
- **For the spec (not done here):**
  - CONTEXT.md: **Label** becomes "what a Garment is called, in words
    you'd say (Light Blue)"; it's no longer "the whole of what the tool
    prints". Drop `color` from its _Avoid_. New term **Color**: "the
    color a Garment is drawn in, told with its Label", with an optional
    stripe Color. Cross-link the two.
  - A new ADR, "Garments carry a told Color": it changes the State and
    reverses "the Label is the whole of what the tool prints".
