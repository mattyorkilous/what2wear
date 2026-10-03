# 09 — Widget JSON endpoint

**What to build:** A JSON answer for one date that the widget can draw
from, carrying the same icon data as the Day page. See the contract in
`.scratch/phone/spec.md`.

**Blocked by:** 08 — Garment icons on the Day page.

**Status:** done

- [x] `GET /<token>/day/YYYY-MM-DD.json` returns `date`, `day` and
      `outfit`, items in widget order (Shirt, Pants, any Outerwear,
      shoes)
- [x] Each item has `garment`, `label` and `icon` (`shape`, `fill`,
      `detail`, plus `pattern`/`pattern_fill` only when striped)
- [x] `if_cold: true` only when the forecast is unknown
- [x] An unreadable State is `{"error": "…"}` with a 500
- [x] `no-store`, and a wrong token is a 404
