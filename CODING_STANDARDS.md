# Coding standards

Ruff owns formatting and lint. This file owns what's left.

A function is **private** when no other module reaches for it — nothing outside its own file imports it or calls it. Everything else is public.

## Rules

- **Private functions are prefixed with `_`** — the prefix is the only signal that a function can be changed or deleted without looking outside the file. When a function loses its last outside caller, rename it to match.
- **Public functions come first, private ones after** — a reader arriving at a module meets its interface before its machinery, and can stop at the first `_`.
- **A function is defined below the one that calls it** — read top to bottom and every name is explained after you have seen it used. This is what orders the private block.
