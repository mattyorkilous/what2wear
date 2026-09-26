# 07 — What becomes of the CLI

Type: grilling
Status: open
Blocked by: none

## Question

The web shell replaces `cli.py` as the interface (ADR-0009: the parser,
chooser and renderers are traded). Should `cli.py` and its tests be
deleted, or kept as a local tool for administering the State? If they
are deleted, which tests move to the web shell, and which were really
core tests that only ran through the CLI?
