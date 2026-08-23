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

**Status:** done

- [x] A bare invocation still answers for today
- [~] ~~`--on <date>` answers for that date and can be combined with a subcommand that takes no date of its own~~ -- struck, see Comments; `--on` answers for that date and is refused alongside every subcommand
- [x] `stay-home`, `go-in` and `reset` do exactly what their flags did, including the optional date and the optional Shirt Label
- [x] Every existing exit code and error message is preserved
- [x] The core is not touched — this ticket is confined to the shell
- [x] The existing CLI tests are re-pointed at the new surface with no case dropped
- [x] The README's interface section describes the commands that exist rather than the ones that are planned

## Comments

**Combining `--on` with a subcommand was not intended.** The second
acceptance criterion above says `--on <date>` "can be combined with a
subcommand that takes no date of its own". Implementing it that way
gave `reset` a date it never had, because `handle` resolves and records
against one date: `--on <date> reset` recorded a Reset dated forward
rather than resetting today, and reached the recording path with a past
date that the question path refuses. That is a behavior change, which
the ticket's own opening forbids -- "Nothing about what the tool
answers changes. This is a prefactor."

`--on` is now refused alongside every subcommand, so it means what it
always meant: the date a bare invocation asks about. The criterion is
struck rather than met.

Note for later tickets: the combination reads as forward-looking to the
two seams, where `answer(state, on, weather)` and `apply(state,
command, today)` take their own dates and `--on` would steer only the
answer. It was rejected there too -- `--on <date> replace ...` is
confusing, and every command is either about its own date or about
today.

**One error message did change.** The clash above used to be argparse's
own -- `argument --stay-home: not allowed with argument --on` -- because
`--on` and the recording flags shared a mutually exclusive group. A
group cannot span a subparser, so the rule is now stated in the shell
and reads `--on cannot be combined with stay-home`. Same exit code,
same usage line, different wording; it is the one message this ticket
alters, and "every existing exit code and error message is preserved"
is ticked with that exception noted.

Refusing it only works with `--on` in front. `what2wear stay-home --on
<date>` is argparse's `unrecognized arguments: --on`, because a root
flag has to precede the subcommand. Same exit code either way, and a
test pins both orders.
