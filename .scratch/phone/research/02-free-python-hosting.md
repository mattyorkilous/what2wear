# Research: free hosting for the Python core

Answers `issues/02-free-python-hosting.md`. Sources checked 2026-09-26; every
claim links to the host's own docs, pricing page or blog.

Constraint reminders from the repo: `pyproject.toml` says
`requires-python = ">=3.14"`; the forecast fetch is a synchronous
`urllib.request.urlopen` in `src/what2wear/forecast.py`; the State is one JSON
file written atomically.

## Summary table

| Host | Card on file? | Persistent State | Reaches api.open-meteo.com | Sleep / cold start | Expiry / renewal | Python |
|---|---|---|---|---|---|---|
| **PythonAnywhere free** | No | Yes, 512 MiB real disk | Yes, on the allowlist | None documented (always-on WSGI worker) | Web app expires after **1 month** unless you log in and extend it | Up to **3.13** (no 3.14) |
| **Cloudflare Python Workers (free)** | Not required for Free plan (not stated on pricing page, see note) | Not a filesystem. Durable Objects (SQLite, 5 GB) or KV (1 GB) | Yes, via `workers.fetch` (not `urllib`) | Isolates, ~1 s cold start with packages | None | **3.14** (Pyodide 314.0.6) |
| **Render free** | No | **No.** Filesystem wiped on restart, redeploy, spin-down; no disks on free | Yes, no allowlist documented | Spins down after 15 min idle; ~1 min to wake | None; 750 instance-h/month | Any from 3.7.3, default **3.14.3** |
| Fly.io | **Yes**, except during trial | Volumes, $0.15/GB-month | Yes | Configurable | Trial is 2 VM-hours or 7 days, then stops | Any (container) |
| Google Cloud Run | **Yes** (billing account) | No. In-memory FS; needs GCS/Firestore | Yes | Scale to zero | None | Any (container) |
| Oracle Always Free | **Yes** | Yes, 200 GB block storage | Yes | None (full VM) | Idle VMs reclaimed | Any (you install it) |
| Koyeb | n/a | n/a | n/a | n/a | n/a | No free compute tier is listed; the only free offering is Postgres |

## Candidates in detail

### 1. PythonAnywhere free ("Beginner")

- **Storage:** "512MB of private file storage" on a real, persistent disk
  ([pricing](https://www.pythonanywhere.com/pricing/),
  [free-account features](https://help.pythonanywhere.com/pages/FreeAccountsFeatures/)).
  A JSON file with atomic `os.replace` works as it does on the Mac.
- **Outbound network:** free accounts get "restricted outbound Internet
  access", limited to an HTTP(S) allowlist
  ([pricing](https://www.pythonanywhere.com/pricing/)). The
  [allowlist](https://www.pythonanywhere.com/whitelist/) includes both
  `.open-meteo.com` and `api.open-meteo.com`, so `urlopen` works unchanged.
- **Sleep / cold start:** there is "1 web app with 1 web worker"
  ([features](https://help.pythonanywhere.com/pages/FreeAccountsFeatures/)).
  The docs describe no idle spin-down.
- **Expiry:** "Unused web apps will expire after 1 month, rather than 3
  months" (since 2026-01-15, [blog 221](https://blog.pythonanywhere.com/221/);
  also "1 month expiry" on the
  [features page](https://help.pythonanywhere.com/pages/FreeAccountsFeatures/)).
  You extend it with the "Run until 1 month from today" button on the Web tab.
  Staff explain its purpose in the
  [forum](https://www.pythonanywhere.com/forums/topic/36620/), which is a
  secondary source. Plan on a monthly manual renewal. The same change moved
  scheduled tasks and MySQL to the paid tier and ended direct support for
  free accounts ([blog 221](https://blog.pythonanywhere.com/221/)).
- **Python:** the newest image, "innit", has "Python versions 3.11, 3.12 and
  3.13" ([blog 219](https://blog.pythonanywhere.com/219/),
  [versions](https://help.pythonanywhere.com/pages/PythonVersions/)). There is
  **no 3.14**, so running here means lowering `requires-python` to 3.13 and
  avoiding 3.14-only features. That is a check to do against the codebase.
- **Card:** none. You sign up with an email address.

### 2. Cloudflare Python Workers (Workers Free)

- **Storage:** there is no writable persistent filesystem, so the State has to
  go to a binding:
  - **Durable Objects (SQLite-backed):** the only kind on Free, with
    "5 GB (total)" storage and 100,000 row writes/day
    ([DO pricing](https://developers.cloudflare.com/durable-objects/platform/pricing/)).
    It has one writer and strong consistency, which fits "one writer of the
    State".
  - **KV:** 1 GB and 1,000 writes/day on Free
    ([KV pricing](https://developers.cloudflare.com/kv/platform/pricing/)).
    It is eventually consistent, so reading straight after a write can
    return stale data.
- **Outbound network:** there is no allowlist. Outbound requests go through
  `from workers import fetch`, which is async and must run inside a handler
  ([Python Workers docs](https://developers.cloudflare.com/workers/languages/python/)).
  `threading` and `multiprocessing` "are not functional"
  ([stdlib](https://developers.cloudflare.com/workers/languages/python/stdlib/)),
  and the docs never say `urllib.request` works. Cloudflare's GA post says it
  routes `httpx` and similar clients through JS fetch
  ([blog](https://blog.cloudflare.com/python-workers-ga/)). **Result:**
  `forecast.py`'s `urlopen` and the file-based State store both need
  Worker-specific replacements. These are adapter changes, not a port of the
  core.
- **Packages:** "pure and PyEmscripten Python packages on PyPI" are supported
  ([packages](https://developers.cloudflare.com/workers/languages/python/packages/)).
  `holidays` and `platformdirs` are pure Python, so they should load.
  `platformdirs` would go unused. Nobody has tested this yet.
- **Sleep / cold start:** memory snapshots bring cold start with
  fastapi+httpx+pydantic to about 1.0 s
  ([Cloudflare blog](https://blog.cloudflare.com/python-workers-advancements/),
  the vendor's own benchmark). Workers don't "sleep" in the Render sense.
- **Limits:** 100,000 requests/day and **10 ms CPU per invocation** on Free
  ([Workers pricing](https://developers.cloudflare.com/workers/platform/pricing/)).
  10 ms is tight for Python, so a prototype needs to measure a real request.
- **Expiry:** none documented.
- **Python:** "Python workers now use Python 3.14 by default" for
  compatibility date ≥ 2026-09-08 (Pyodide 314.0.6,
  [changelog](https://developers.cloudflare.com/changelog/post/2026-09-08-python-workers-314/)).
- **Card:** the Workers pricing page doesn't say the Free plan needs one. I
  found no first-party statement either way, so this is unverified. In
  practice, signup works without a card.

### 3. Render free web service

- **Storage:** none that lasts. Filesystem changes "are lost on redeploy,
  restart, or spin-down", and Free services can't attach persistent disks
  ([free docs](https://render.com/docs/free)). The State would have to live
  somewhere else, for example a Cloudflare DO/KV reached over HTTP. That makes
  Render worse than Cloudflare on its own.
- **Outbound:** no allowlist is documented.
- **Sleep:** it spins down after "15 minutes without receiving any inbound
  traffic" and takes about one minute to come back
  ([free docs](https://render.com/docs/free)). A phone or widget request after
  idle would wait about a minute.
- **Expiry:** none. There are 750 free instance-hours per workspace per month,
  and going over suspends Free services until next month
  ([free docs](https://render.com/docs/free)).
- **Python:** "any released version from 3.7.3 onward", default 3.14.3
  ([python-version](https://render.com/docs/python-version)).
- **Card:** not needed for Free services. Without one, overage suspends
  services instead of billing ([free docs](https://render.com/docs/free);
  Render's own [article](https://render.com/articles/platforms-with-a-real-free-tier-for-developers-in-2026)).

### Excluded: needs a card or has no free compute

- **Fly.io:** "All organizations (except for Linked Organizations) require a
  credit card on file" ([pricing](https://docs.fly.io/about/pricing/)). The
  cardless trial lasts "2 hours of machine runtime or 7 days of access,
  whichever comes first", and after that apps stop
  ([free trial](https://docs.fly.io/about/free-trial/)). Volumes cost
  $0.15/GB-month. **Not $0.**
- **Google Cloud Run:** the free tier gives 2M requests/month, but "A Google
  Cloud billing account is required", and signup needs "a credit card or
  other payment method"
  ([free features](https://docs.cloud.google.com/free/docs/free-cloud-features)).
  The container FS is "an in-memory file system" and data "doesn't persist
  when the instance stops"
  ([container contract](https://docs.cloud.google.com/run/docs/container-contract)),
  so the State would need GCS (5 GB, US regions only) or Firestore. **Card
  required.**
- **Oracle Cloud Always Free:** gives you a full VM (A1, 2 OCPU/12 GB) and
  200 GB block storage, but "most users need a mobile phone number and a
  credit card to create an account"
  ([free tier](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier.htm)).
  Idle instances are reclaimed when CPU, network and memory all stay below 20%
  for 7 days
  ([Always Free resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm)),
  and a tiny personal app would fall below that. **Card required, and it gets
  reclaimed.**
- **Koyeb:** the [pricing page](https://www.koyeb.com/pricing) lists no free
  web-service compute. The only free item is a Postgres database.

## Ranked shortlist

1. **PythonAnywhere free:** the only host where the core runs almost as it is
   (real disk, open-meteo allowlisted, no sleep, no card). The costs are
   dropping to **Python 3.13** and **renewing by hand every month**. If a
   renewal is missed, the app stops but the files stay on disk.
2. **Cloudflare Python Workers + a SQLite Durable Object:** Python 3.14, no
   sleep, no expiry, no card. It needs two new adapters (async `fetch`
   instead of `urlopen`; DO storage instead of the JSON file). There are two
   risks to prototype: the 10 ms CPU limit, and whether `holidays` loads
   under Pyodide.
3. **Render free:** Python 3.14 and no card, but the filesystem doesn't
   persist and waking takes about 1 minute. It only works when paired with
   an external store, so it is dominated by #2.

Fly.io, Cloud Run and Oracle all fail the no-card rule. Koyeb has no free
compute.

## Open questions for later tickets

- Does the core use anything 3.14-only? That decides whether PythonAnywhere
  is viable without code changes.
- Can a Python Worker's request (parse the date, load `holidays`, choose the
  Outfit, fetch the forecast) stay inside 10 ms of CPU on Free?
