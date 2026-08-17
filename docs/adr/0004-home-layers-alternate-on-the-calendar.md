# Home Layers alternate on the calendar, not on cold days

Every Home Day is a jacket day or a sweater day, decided by a Home Layer Rotation of length 2 that advances on *every* Home Day. Temperature decides only whether the Layer is worn, never which one it is. This supersedes ADR-0002, which flipped the alternation once per *cold* Home Day and therefore had to store a cursor: which past days were cold is not knowable from configuration the way the calendar is, so the flip could not be reconstructed. Advancing on all Home Days makes it a plain function of `(anchor, day count, recorded Resets)` like every other Position, and ADR-0001 now holds with no exception anywhere in the system.

## Consequences

- **A warm day spends its turn.** Cold, mild, cold gives jacket, nothing, jacket — the same kind of Layer either side of the gap. This is the price of the change and it was accepted knowingly: the old rule bought the other behaviour with a stored cursor, a second append-only log, and a permanent exception to ADR-0001.
- **The Layer log is gone.** Recorded decisions are one append-only file again, holding Day Type Overrides and Resets.
- **The alternation advances on days the tool isn't opened**, reversing ADR-0002's accepted limitation. You can no longer get the same kind of Layer twice running after a gap, and the "behaviour after a stretch with no recorded Layer" case ceases to exist.
- **Layers are knowable past the forecast horizon.** Their identity was always derivable — the office sweater from the Week walk, and now the home Layer from its Rotation — so a distant date names the garment and hedges only the condition, rather than reporting the Layer unknown.
- **The Home Layer Rotation is Reset independently** of the Home Shirt Rotation, so a recorded Reset now has to name which Rotation it shifts.
- The home Anchor Date gains the Layer worn on it, alongside the Shirt.
