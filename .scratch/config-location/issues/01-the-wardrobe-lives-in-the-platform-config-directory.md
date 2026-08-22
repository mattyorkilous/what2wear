# 01 — The Wardrobe lives in the platform config directory

**What to build:** A tool that keeps your Wardrobe and its decision log where your operating system keeps a user's config, instead of in whatever directory you happen to be standing in — and that no longer carries anybody's real closet in the repo.

Fresh install, nothing configured: running `what2wear` names the exact path it looked at, says no Wardrobe is there yet, and points at the repo's `example.yaml` to copy. You author a Wardrobe at that path and the tool works. Recorded decisions land beside it. There is no flag, no environment variable and no working-directory fallback to point it anywhere else — the location is a property of the installation, not of an invocation.

The one seam that reads the platform directory is a `run` entry point, called by `__main__` and by the console script; `main` takes the directory as an argument. That is what lets the tests drive a temporary directory without an environment variable, and it is why `main` stops importing `os` altogether.

The Wardrobe currently committed at `what2wear.yaml` is a real person's closet. It becomes an anonymized `example.yaml`, and `tests/wardrobe.py` — which mirrors it — is rewritten to match the fiction. The test pinning the two together survives, re-pointed at `example.yaml`: an in-memory fixture checked against a file the config boundary really parses is worth keeping.

Nothing creates a directory. `main` reads the Wardrobe before it appends any decision, so a successful read has already proved the directory exists.

An `init` command is deliberately out of scope. Creating a Wardrobe for the user is the future in-app route, not a flag on a CLI that is itself disposable.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [x] `cli.py` has no module-level path constants and does not import `os`
- [x] `run` is the only caller of `platformdirs`; `__main__.py` and the `what2wear` console script both point at it
- [x] `main` takes the config directory as a keyword argument and reads nothing ambient to find it
- [x] The Wardrobe is read from `config.yaml` in the user config directory, and decisions are appended to `decisions.jsonl` beside it
- [x] No `--config` flag, no `--dir` flag, no environment variables, no working-directory default
- [x] A missing Wardrobe is reported distinctly from a malformed one: `config.py` raises a `ConfigError` subclass for absence, and the shell owns the first-run wording
- [x] The first-run message names the full path it looked at and points at `example.yaml`; exit code stays 2
- [x] A malformed Wardrobe still reports its parse error, not the first-run message
- [x] Nothing in the tool creates a directory
- [x] `what2wear.yaml` is gone, replaced by an anonymized `example.yaml`
- [x] `tests/wardrobe.py` holds the same fictional Wardrobe, and the test pinning fixture to file is re-pointed at `example.yaml`
- [x] `.gitignore` no longer needs to exclude a decision log, because nothing writes to the repo
- [x] Tests drive a temporary directory by argument; the environment-variable and flag-precedence tests are gone rather than ported
- [x] `platformdirs` is a declared dependency
- [x] `CONTEXT.md` defines **Wardrobe**, and `wardrobe` is removed from Closet's `_Avoid_` list
- [x] README's Configuration section describes the new location and the first-run behavior
- [x] One-off, outside the repo: the current `what2wear.yaml` is copied to the user config path, and the path is reported back
