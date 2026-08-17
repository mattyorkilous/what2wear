# Rotation Positions are derived from the calendar, not stored

A Position is computed on demand as a function of `(closet, weekly pattern, recorded decisions, date)` — roughly `(count of days of that type since the Anchor Date + recorded Reset offsets) mod len(closet)`. Nothing is persisted that says "you are currently on shirt 3", and nothing is ever consumed.

The obvious alternative was a stored cursor advanced each time you use the app. We rejected it because looking ahead to a future date then becomes a *simulation* that can drift from what the app will actually say when that day arrives, whereas under derivation "what will I wear on the 24th" is the same function called with a different date — look-ahead is free rather than a second code path. It also means not opening the app for a week can't desynchronise anything: you wore clothes on those days, and the Rotation moves with the calendar whether or not you were watching.

## Consequences

- **Editing a Closet rewrites history and the future.** Adding a sixth office shirt makes every Position `mod 6` instead of `mod 5`, changing what the app claims you wore last March and what you'll wear next month. Accepted deliberately: no wear history is kept, so there is nothing to protect. The alternative — versioning Closets so past dates stay stable — roughly doubles the complexity of the core to defend data we do not store.
- **A Reset shifts everything after it, permanently.** Look-ahead is therefore only valid until the next Reset, which matches how the feature is meant to be used.
- **Day Type Overrides are just recorded facts about dates.** Holidays, leave, going in on a Saturday and staying home on a Wednesday are one concept, and future dates are as overridable as past ones.
- **This holds without exception.** The Home Layer alternation was once carved out of it (ADR-0002) and has since been brought back in — see ADR-0004.
