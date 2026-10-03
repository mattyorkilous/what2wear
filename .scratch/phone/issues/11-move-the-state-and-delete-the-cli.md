# 11 — Move the State and delete the CLI

**What to build:** The wearer's existing State moves to PythonAnywhere,
is checked against the Mac, and the CLI is deleted so the web app is
the one writer. See `.scratch/phone/spec.md`.

**Blocked by:** 02 — Given Labels become full names; 04 — Day page
actions; 05 — Settings page; 06 — Closet page with due dates and Swap;
07 — Replace with a Color.

**Status:** done

- [x] `state.json` uploaded in the Files tab to the WSGI file's
      `state_path`
- [x] Today's Day page matches `what2wear` on the Mac; from then on the
      Mac CLI isn't used
- [x] Deleted: the CLI module, its tests, the `[project.scripts]`
      entry, `platformdirs`, and the CLI's per-file ruff ignores
- [x] CONTEXT.md no longer mentions `show-closet` or the
      `office.shirt.ecru` wording
- [x] README covers deploy (`git pull`, `uv sync`, Reload), monthly
      renewal with a `state.json` download as backup, and restore by
      upload
- [x] The deletion is committed and deployed
