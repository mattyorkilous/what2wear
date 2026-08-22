# 02 — The CLI becomes subcommands

**What to build:** The same tool, said differently. Every command the
CLI already has moves from a flag to a subcommand, and a bare invocation
still means today. `--on` stays a root flag rather than becoming a verb,
because it modifies the default question instead of asking a new one.

Nothing about what the tool answers changes. This is a prefactor: three
later tickets add commands — `replace`, `swap`, `show-closet`,
`reset-outerwear` — and two of those take positional arguments that a
mutually exclusive flag group cannot express without contorting. Making
the shape right while the behavior is still settled keeps that shape out
of the ticket that also rewrites the core.

The command surface after this ticket:

```
what2wear                            today
what2wear --on <date>                a future date
what2wear stay-home [date]
what2wear go-in [date]
what2wear reset [label]
```

**Blocked by:** 01 — The Wardrobe becomes given source (which deletes a
CLI branch this ticket would otherwise carry across)

**Status:** ready-for-agent

- [ ] A bare invocation still answers for today
- [ ] `--on <date>` answers for that date and can be combined with a subcommand that takes no date of its own
- [ ] `stay-home`, `go-in` and `reset` do exactly what their flags did, including the optional date and the optional Shirt Label
- [ ] Every existing exit code and error message is preserved
- [ ] The core is not touched — this ticket is confined to the shell
- [ ] The existing CLI tests are re-pointed at the new surface with no case dropped
- [ ] The README's interface section describes the commands that exist rather than the ones that are planned
