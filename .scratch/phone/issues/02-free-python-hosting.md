# 02 — Free hosting for the Python core

Type: research
Status: resolved
Blocked by: none

## Question

Which $0 hosts can run a small Python 3.14 HTTP app that keeps one
persistent JSON file (the State), survives restarts without losing it,
and can call `api.open-meteo.com`?

For each candidate (e.g. PythonAnywhere free, Render, Fly.io,
Cloudflare Python Workers, Google Cloud Run free tier), cover:
- persistent storage
- outbound-network allowlists
- sleep and cold-start latency
- whether it expires or needs manual renewal
- the Python version it runs

Research: research/02-free-python-hosting.md

## Answer

The shortlist, best first. Detail and sources are in
`research/02-free-python-hosting.md`.

1. **PythonAnywhere free.** No card; a real persistent disk; Open-Meteo
   is on its allowlist, so the State file and `urlopen` work unchanged.
   Two costs: it tops out at **Python 3.13**, and an unused web app
   expires after **1 month** unless you click to renew it. The core has
   one 3.14-only line: the unparenthesised
   `except HTTPException, OSError, ...` in `forecast.py` (PEP 758).
   Adding parentheses runs it on 3.13.
2. **Cloudflare Python Workers (Free).** Python 3.14, no expiry, about
   1 s cold start. The State would move to a SQLite Durable Object, and
   `urllib` would become `workers.fetch`. Two risks: the Free tier's
   10 ms CPU per request, and whether `holidays` loads under Pyodide.
3. **Render free.** Its disk is wiped when it sleeps, so it only works
   with an outside store; option 2 beats it.

Ruled out: Fly.io, Cloud Run and Oracle all need a card; Koyeb has no
free compute.
