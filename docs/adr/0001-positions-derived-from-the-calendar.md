# Rotation Positions are derived from the calendar, not stored

> Amended by [ADR-0005](./0005-what2wear-dresses-one-person-from-a-given-wardrobe.md),
> [ADR-0006](./0006-the-wardrobe-is-source-the-state-is-one-file-the-tool-owns.md)
> and [ADR-0008](./0008-every-command-acts-on-one-date.md), and
> [ADR-0011](./0011-holidays-are-given-home-days.md). The decision
> below is unchanged and the formula got shorter; the consequences were
> rewritten. What the amendments removed is noted against each.

A Position is computed on demand as a function of `(Anchor, weekly
pattern, Day Type Overrides, date)`:

```
position(date) = (anchor.position + days_of_that_type_between(anchor.date, date)) mod len(rotation)
```

Nothing is persisted that says "you are currently on shirt 3", and
nothing is ever consumed.

The obvious alternative was a stored cursor advanced each time you use
the app. We rejected it because looking ahead to a future date then
becomes a *simulation* that can drift from what the app will actually
say when that day arrives, whereas under derivation "what will I wear
on the 24th" is the same function called with a different date —
look-ahead is free rather than a second code path. It also means not
opening the app for a week can't desynchronise anything: you wore
clothes on those days, and the Rotation moves with the calendar whether
or not you were watching.

## Consequences

- **A Reset moves the Anchor, so it moves the whole Rotation.** It is
  not a recorded offset that applies from its own date forward; there
  is no offset term in the formula at all. Look-ahead is therefore
  valid until the next Reset, which matches how the feature is used.
- **The past is derivable, and is offered with a caveat.** Because a
  Reset re-Anchors, asking what you wore last March answers with a
  Position implied by today's Anchor rather than the one that was
  current then. No wear history is kept, so there is nothing that could
  make the old answer available. ADR-0008 replaces the original refusal
  with a note saying so; the derivation it describes is unchanged.
- **A mid-Week Reset can change that Week's Fallback.** Friday's office
  sweater is resolved by walking Monday and Wednesday to see what they
  spent, and a Wednesday Reset moves Monday's derived Shirt, so Friday
  can be answered from a Monday that didn't happen. Accepted: it needs
  a Reset, mid-Week, landing on different Pants, into a collision; it
  self-corrects the following Monday; and the alternatives are for
  Friday to forget a Monday that *did* happen, or to record what was
  actually worn, which is the stored history this whole design exists
  without.
- **Editing a Closet no longer rewrites anything, because a Closet
  cannot be edited.** Under ADR-0005 sizes are fixed in source, so no
  command can change a modulus. This replaces the original consequence,
  which accepted that adding a sixth office Shirt reshuffled every
  Position past and future.
- **Day Type Overrides are just recorded facts about dates.** Leave,
  working a Holiday, going in on a Saturday and staying home on a
  Wednesday are one concept, and future dates are as overridable as
  past ones. They are the only thing left that the derivation reads
  out of the State. Per ADR-0011 they are no longer the only thing it
  reads beyond the weekday pattern: a given calendar of Holidays sits
  beneath them.
- **This holds without exception.** The Home Outerwear alternation was once
  carved out of it (ADR-0002) and has since been brought back in — see
  ADR-0004. The other former exception, an authored Anchor Date
  overriding recorded Resets, is gone with the second author: per
  ADR-0006 the Anchor is now the only thing that says where a Rotation
  stands.
