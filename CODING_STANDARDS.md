# Coding standards

Ruff owns formatting and lint. This file owns what's left.

A function is **private** when no other module reaches for it — nothing outside its own file imports it or calls it. Everything else is public.

## Rules

- **Private functions are prefixed with `_`** — the prefix is the only signal that a function can be changed or deleted without looking outside the file. When a function loses its last outside caller, rename it to match.
- **Public functions come first, private ones after** — a reader arriving at a module meets its interface before its machinery, and can stop at the first `_`.
- **A function is defined below the one that calls it** — read top to bottom and every name is explained after you have seen it used. This is what orders the private block.
- **Siblings are defined in call order** — where the rules above leave a choice, the functions a parent calls appear in the order the parent calls them, so the file reads in the order the work happens.
- **No loops** — reach for a comprehension, `functools`, or `itertools`. A loop is a place where a name changes meaning halfway down the body; the alternatives don't have one. The one exception is below.
- **Data is immutable** — prefer an immutable structure over a mutable one every time there is a choice, and never rebind a name to a different object. If the thing has changed, it gets a new name.

## The reduce exception

Reduce and accumulate patterns are the only ones that earn a loop, because the alternative is worse to read. When you write one, the step is a single pure function and the loop is dead simple:

```python
data = data()

for x in xs:
    data = update(data, x)
```

The rebinding of `data` here is the shape of the pattern, not an exception to the rule above — `update` returns a new value and mutates nothing. Anything more than this belongs inside `update`.
