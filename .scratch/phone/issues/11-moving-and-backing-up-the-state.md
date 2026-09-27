# 11 — Moving and backing up the State

Type: grilling
Status: open
Blocked by: none

## Question

The State moves from the Mac's `platformdirs` location to a path on
PythonAnywhere's disk (see
[The web shell on PythonAnywhere](08-the-web-shell.md)). How does
the existing `state.json` get there, and in what order relative to
the CLI's deletion (the last step, per
[What becomes of the CLI](07-what-becomes-of-the-cli.md))? And now
that the only copy lives on a free host that expires if you don't
renew it each month, how is it backed up: a download by hand, a
scheduled task (if the free plan has one), a git commit, or not at
all?

The move also converts the Labels once: each short Label (`lblue`)
becomes its full name ("Light Blue") and gains its Color, per
[Full names and colours for Labels](10-full-names-and-colours.md).
How, and where the conversion lives (a one-off script, or at first
read on the server)?
