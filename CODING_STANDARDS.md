# Coding standards

Ruff owns formatting and lint. This file owns what's left.

A function is **private** when no other module reaches for it — nothing outside its own file imports it or calls it. Everything else is public.

## Naming

- **A function is named for the action it performs** — a verb, not a noun. `_dated`, `_recorded` and `_repeat_note` read as accessors for something the module is already holding; `_build_date_parser`, `_record` and `_note_repeat` say what happens when you call them.
- **The verb says what comes back** — `_declare_date_flag` sounds like a function kept for its effect, when what it does is hand you a parser. Pick the verb so the return value is expected before the signature confirms it.
- **`build_` constructs, `get_` derives** — `build_` makes something out of nothing and needs no arguments to do it: `_build_parser`, `_build_date_parser`. When the result comes *from* what the function was handed, it is `get_`: `_get_command(args, on)`.
- **One word means one thing per file** — argparse's `dest="command"` sat twenty lines from the domain's `Command`, and the reader had to hold both. Where the colliding name is dead, delete it rather than rename it.

## Rules

- **Private functions are prefixed with `_`** — the prefix is the only signal that a function can be changed or deleted without looking outside the file. When a function loses its last outside caller, rename it to match.
- **Public functions come first, private ones after** — a reader arriving at a module meets its interface before its machinery, and can stop at the first `_`.
- **A function is defined below the one that calls it** — read top to bottom and every name is explained after you have seen it used. This is what orders the private block.
- **Siblings are defined in call order** — where the rules above leave a choice, the functions a parent calls appear in the order the parent calls them, so the file reads in the order the work happens.
- **No loops** — reach for a comprehension, `functools`, or `itertools`. A loop is a place where a name changes meaning halfway down the body; the alternatives don't have one. The one exception is below.
- **American spellings in prose** — `color`, `behavior`, `anonymize`. This covers comments, docstrings, error messages and documentation. Garment Labels are exempt: they are the wearer's word for their own clothes, so a Label reading `grey` stays `grey`.
- **I/O at the edges, the pure part in view** — reads and writes live in the shell function, not inside a helper whose name promises a value. `run` reads the State, applies the command, writes, and answers, and each step is visible at the point it happens.
- **Comments don't restate the code** — a why worth keeping goes in the docstring, where it is attached to the thing it explains. Most comments are a sentence the code already said.
- **Data is immutable** — prefer an immutable structure over a mutable one every time there is a choice, and never rebind a name to a different object. If the thing has changed, it gets a new name.

## The reduce exception

Reduce and accumulate patterns are the only ones that earn a loop, because the alternative is worse to read. When you write one, the step is a single pure function and the loop is dead simple:

```python
data = data()

for x in xs:
    data = update(data, x)
```

The rebinding of `data` here is the shape of the pattern, not an exception to the rule above — `update` returns a new value and mutates nothing. Anything more than this belongs inside `update`.
