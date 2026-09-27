# 07 — What becomes of the CLI

Type: grilling
Status: resolved
Blocked by: none

## Question

The web shell replaces `cli.py` as the interface (ADR-0009: the parser,
chooser and renderers are traded). Should `cli.py` and its tests be
deleted, or kept as a local tool for administering the State? If they
are deleted, which tests move to the web shell, and which were really
core tests that only ran through the CLI?

The web pages reuse the CLI's confirmation and error strings (see
[Pages and forms for each command](06-pages-and-forms.md)), so wherever
those live after this decision, the web shell must be able to reach
them.

## Answer

**Delete the CLI; the web shell takes its strings, and nothing from
`test_cli.py` is ported.** Settled by grilling on 2026-09-27.

- **Delete** `cli.py`, `tests/test_cli.py`, the `what2wear` entry under
  `[project.scripts]`, and the `platformdirs` dependency. Keeping it as
  an admin tool, even in PythonAnywhere's bash console against the
  hosted file, would be a second writer and an escape hatch that no
  command needs, since every command has a page. Git history keeps it.
- **Strings:** the web shell module owns the confirmation lines
  (ADR-0009: describing what was typed is the shell's job), reworded as
  it needs. That includes `_render_weekdays`, the `, if it's cold`
  hedge, the past-date note and the unavoidable-repeat note. There is
  no shared `messages` module. The refusal messages already live in
  `core` and don't move. The date words (`tomorrow`, weekday names)
  and `when`'s shirt-name parsing are dropped: the date picker and the
  Closet page replace them.
- **Tests:** none of `test_cli.py` was a core test in disguise; core
  behaviour is already covered by `test_when.py`, `test_replace.py`
  and the rest. The spec lists these shell behaviours as the web
  shell's test checklist, to be written fresh against the web app:
  - a fresh install answers and writes nothing
  - the State is written only when it changes
  - `recorded` vs `already` in the notice
  - the past-date note
  - the unavoidable-repeat note
  - the outerwear hedge while the forecast is unknown
  - a clear message for an unreadable State
- **When:** the deletion is the last step of the change that brings in
  the web shell, after the State has moved to PythonAnywhere.
- CONTEXT.md mentions `show-closet` once (under Label). Reword it when
  the CLI goes.
