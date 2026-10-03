# 11 — Moving and backing up the State

Type: grilling
Status: resolved
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

## Answer

**Upload by hand, check against the Mac, then delete the CLI; back up
by hand at each monthly renewal.** Settled by grilling on 2026-09-27.

- **Label conversion: none needed.** The live `state.json` has
  `"labels": {}`: the store writes only Labels that differ from the
  given ones (`store.py` `_get_document`), and none has ever been
  replaced. So the given Wardrobe in `wardrobe.py` changes to full
  names plus Colors (from the prototype's `FILL` table), and the
  existing file reads as "Light Blue" and the rest unchanged. There's
  no script and no conversion at first read. If a Label is replaced
  before the move, it gets retyped once on the Replace form.
- **Getting it there:** upload `state.json` through PythonAnywhere's
  Files tab to the `state_path` the WSGI file gives `web.app(...)`.
- **Order:**
  1. Deploy the web shell with the CLI still in the repo.
  2. Upload `state.json`.
  3. Check that today's Day page matches `what2wear` on the Mac.
  4. From then on, the Mac CLI isn't used (one writer).
  5. Commit and deploy the CLI deletion
     ([What becomes of the CLI](07-what-becomes-of-the-cli.md)).

  The Mac file stays where it is as a frozen copy. Step 3 is the guard
  against a wrong path, which would otherwise silently serve a fresh
  default State. There's no server-side refusal to start without the
  file.
- **Backup:** download `state.json` from the Files tab at each monthly
  renewal. You're logged in then anyway, and the free plan has no
  scheduled tasks. There's no download endpoint and no git commit. The
  most you can lose is a month of overrides and replacements.
- **Restore:** upload the backup in the Files tab. There's no page for
  it.
