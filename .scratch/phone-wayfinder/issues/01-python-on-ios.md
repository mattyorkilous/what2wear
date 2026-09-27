# 01 — Python on iOS, free-signed

Type: research
Status: resolved
Blocked by: none

## Question

Can a free-provisioned iOS app (a personal team, no paid Apple
Developer Program) embed CPython 3.14 via PEP 730 or BeeWare's
Python-Apple-support and run the what2wear core, with a SwiftUI
front end?

- Can a widget extension run Python, or must the app precompute
  Outfits and hand them to the widget as data?
- Can a free personal team use WidgetKit and the App Group that data
  handoff needs?
- What are the free-provisioning limits (7-day expiry, number of apps,
  capabilities), and what does re-signing take: Xcode on the Mac
  weekly, or SideStore/AltStore refreshing on the phone?
- Can the app reach Open-Meteo and use the `holidays` package (pure
  Python)?

Research: research/01-python-on-ios.md

## Answer

Yes. A free personal team can ship a SwiftUI app that embeds CPython
3.14 and runs the core unchanged. Detail, sources and a 4-point
prototype checklist are in `research/01-python-on-ios.md`.

- **Getting Python:** use BeeWare's Python-Apple-support `3.14-b11`
  (Python 3.14.7). python.org's iOS builds are 3.15 pre-releases only.
  iOS is PEP 730 Tier 3: embedded only, no subprocesses.
- **The widget doesn't run Python.** The app computes Outfits, writes
  JSON to an App Group and calls `WidgetCenter.reloadTimelines`. The
  widget gets 40–70 refreshes a day, and reloads while the app is in
  the foreground don't count.
- **Free-team limits:** App Groups are allowed. The app plus its widget
  use 2 of the 10 App IDs and 1 of the 3 app slots per device. Signing
  expires every 7 days.
- **Re-signing:** Xcode on the Mac weekly, or SideStore on the phone.
  SideStore needs a computer once, a VPN toggle to refresh, and takes
  another app slot. Its re-signing renames the App Group, so read the
  group ID from the entitlements at runtime (SideStore issue #1437).
- **Dependencies:** `holidays` and its dependencies are pure Python and
  vendor with `pip --target`. HTTPS may lack CA certificates, so either
  vendor `certifi` or fetch the forecast in Swift. `platformdirs` has no
  iOS case, so Swift passes the State path in.
