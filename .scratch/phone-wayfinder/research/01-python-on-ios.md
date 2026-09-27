# Research: Python on iOS, free-signed

Answers `issues/01-python-on-ios.md`. Sources checked 2026-09-26. Claims
link to Apple, python.org, BeeWare or SideStore/AltStore pages. The
exceptions are marked **(unverified)** or **(community)**.

Repo facts it rests on: `requires-python = ">=3.14"`; runtime deps are
`holidays` 0.105 → `python-dateutil` → `six`, plus `platformdirs`
(used only in `cli.py`). `find .venv -name '*.so'` over site-packages
finds nothing, so every dependency is pure Python. The forecast is
`urllib.request.urlopen` in `src/what2wear/forecast.py`.

## Short answer

**Yes for the app. The widget is possible but should get data, not
Python.** A free personal team can embed CPython 3.14, run the core in
the app, and ship a WidgetKit extension that reads precomputed Outfits
from an App Group. The two real risks are TLS certificates for
`urllib` and App Group identifiers being rewritten if SideStore does the
re-signing. Both have known workarounds, and a prototype should check
them.

## 1. Embedding CPython 3.14

- iOS is an official CPython platform. It arrived in 3.13 via
  [PEP 730](https://peps.python.org/pep-0730/) (Final) and is **Tier 3**
  for `arm64-apple-ios` and `arm64-apple-ios-simulator`
  ([PEP 11](https://peps.python.org/pep-0011/)).
- Python can only run **embedded**: "The only way you can use Python on
  iOS is in embedded mode … embedding a Python interpreter using
  `libPython`" ([Using Python on iOS, 3.14](https://docs.python.org/3.14/using/ios.html)).
  That page gives the Xcode recipe: embed `Python.xcframework`, add the
  `install_python` Run Script build phase, and set `PYTHONHOME` and
  `PYTHONPATH`. A SwiftUI front end calls in through the C API. BeeWare's
  [USAGE.md](https://github.com/beeware/Python-Apple-support/blob/main/USAGE.md)
  shows a Swift init snippet and mentions PythonKit.
- **Where to get a 3.14 binary.** python.org publishes an "iOS
  XCframework" only for the **3.15** pre-releases. 3.14.x has none
  ([python.org iOS downloads](https://www.python.org/downloads/ios/)).
  For 3.14 you can either build from source
  ([Apple/iOS/README.md](https://github.com/python/cpython/tree/3.14/Apple/iOS/README.md))
  or use BeeWare's
  [Python-Apple-support `3.14-b11`](https://github.com/beeware/Python-Apple-support/releases/tag/3.14-b11)
  (2026-09-04). That release bundles **Python 3.14.7 and OpenSSL 3.5.8**
  and uses "the official PEP 730 code"
  ([README](https://github.com/beeware/Python-Apple-support)). Its
  minimum is iOS 13.
- **Stdlib limits that matter here.** There are no subprocesses, no
  multiprocessing and no stdin ("If an iOS app attempts to create a
  subprocess, the process … will either lock up, or crash"), and
  `curses`/`readline` are absent
  ([mobile availability](https://docs.python.org/3.14/library/intro.html#mobile-platforms)).
  The core uses none of these. File I/O, sockets and threads "behave as
  they would on any POSIX operating system" (same page).
- `sys.platform == "ios"` ([ios docs](https://docs.python.org/3.14/using/ios.html)).
  `platformdirs` 4.11.3 checks only `win32`, `darwin` and Android, so on
  iOS it would fall back to the XDG/Unix class. That affects only
  `cli.py`. The Swift side should pass the State path (the app's Documents
  directory or the App Group container) into the core.
- App Store rules (binary modules as frameworks, privacy manifests) are
  handled by the build script. They don't matter when sideloading.

## 2. Can the widget extension run Python?

- Nothing in the docs forbids it. No source documents it either. The
  CPython and BeeWare docs cover only the app target and never mention
  extensions **(unverified: would need a prototype)**.
- Apple's docs push against it. Widgets "can only access limited
  resources and a request may not have enough time to complete before
  the system halts the widget extension"
  ([Making network requests in a widget extension](https://developer.apple.com/documentation/widgetkit/making-network-requests-in-a-widget-extension)).
  Reloads are budgeted at "from 40 to 70 refreshes" a day for a widget
  the user views often
  ([Keeping a widget up to date](https://developer.apple.com/documentation/widgetkit/keeping-a-widget-up-to-date)).
  Starting an interpreter and the stdlib inside a memory-capped
  extension is the risky part. Apple doesn't publish the cap.
- **Recommendation: precompute.** When the app runs, the core computes
  the Outfit (or the next few days' Outfits from the Open-Meteo forecast)
  and writes a small JSON file to the App Group container. It then calls
  `WidgetCenter.shared.reloadTimelines(ofKind:)`. The same page says
  reloads while "the widget's containing app is in the foreground" don't
  count against the budget. The widget stays pure Swift and just renders
  emoji from that data.

## 3. WidgetKit and App Groups on a free personal team

- Apple's
  [supported capabilities (iOS)](https://developer.apple.com/help/account/reference/supported-capabilities-ios)
  table has an "Apple Developer" column, defined as free accounts that
  "can't distribute apps". It ticks **App groups**, Background modes,
  Data protection, Keychain sharing, HealthKit, HomeKit and a few
  others. It does **not** tick iCloud, Push, Siri or Associated domains.
  This was parsed from the page HTML.
- A WidgetKit extension needs no capability of its own. It is an
  extension target with its own App ID (see §4). Data sharing uses
  `UserDefaults(suiteName:)` or
  `containerURL(forSecurityApplicationGroupIdentifier:)` on a `group.`
  identifier
  ([Configuring app groups](https://developer.apple.com/documentation/xcode/configuring-app-groups)).

## 4. Free-provisioning limits and re-signing

From Apple's [membership comparison](https://developer.apple.com/support/compare-memberships/)
(personal team):

> You can register up to 10 App IDs, which expire after 7 days. You can
> register up to 3 devices, which expire after 7 days. You can install
> up to 3 apps per device. Provisioning profiles … will expire 7 days
> from issuance. You'll need to rebuild and reinstall your app to your
> device after expiration.

- The app plus its widget uses **2 App IDs**, because each extension
  needs its own ("depends on the number of app extensions each app
  contains", [AltStore: App IDs](https://faq.altstore.io/altstore-classic/app-ids)).
  That is well inside 10 a week, and it occupies 1 of the 3 app slots.

**Option A: Xcode on the Mac, weekly.** Plug in the phone (or pair it)
and press Run. This is exactly what Apple describes. It needs the Mac
once a week but no other tooling. Reinstalling over the same bundle ID
keeps the app's data, as an ordinary app update does **(unverified for
the expired-profile case; check in the prototype)**. This fits the "phone
works without the Mac" constraint only loosely: the Mac isn't needed day
to day, but it is needed weekly.

**Option B: SideStore on the phone.** It "will periodically 'refresh'
your apps in the background, to keep their normal 7-day development
period from expiring"
([SideStore FAQ](https://docs.sidestore.io/docs/faq)). A computer is
needed "only for initial install", and LocalDevVPN "is required to be
turned on any time you wish to install, update, or refresh apps"
([prerequisites](https://docs.sidestore.io/docs/installation/prerequisites)).
It needs iOS 15+. SideStore itself takes one of the 3 app slots ("SideStore
can only install 3 apps (including itself)", FAQ). You build an `.ipa` in
Xcode once and SideStore re-signs it with your Apple ID.

- **Catch for the widget:** SideStore issue
  [#1437](https://github.com/SideStore/SideStore/issues/1437) (closed
  2026-08) reports that a widget "fails to access the UserDefaults
  settings stored in my appgroup" when sideloaded, while it works from
  Xcode. **(community)** One app's fix
  ([lut-timetable PR #33](https://github.com/wzs39/lut-timetable/pull/33))
  says re-signing prefixes the group ID with the team ID. The fix reads
  the granted group from the code-signing entitlements at runtime instead
  of hard-coding `group.…`. Plan for that if Option B is chosen.

## 5. Open-Meteo and `holidays`

- **`holidays`**: it is pure Python (as are `python-dateutil` and `six`;
  no `.so` in the venv). Install it into the app's Python path with
  `pip install --target` ([ios docs, testbed section](https://docs.python.org/3.14/using/ios.html)).
  No framework conversion is needed.
- **Open-Meteo**: sockets work as on POSIX, and the BeeWare 3.14 package
  ships OpenSSL, so `urlopen("https://…")` can connect. **Risk:** CA
  certificates. The bundled OpenSSL has no system trust store to read.
  BeeWare
  [issue #119](https://github.com/beeware/Python-Apple-support/issues/119)
  shows `CERTIFICATE_VERIFY_FAILED` with `cafile`/`capath` = `None` on
  its macOS build, and iOS is likely the same **(unverified on iOS)**.
  Two cheap fixes: vendor `certifi` (pure Python) and pass
  `ssl.create_default_context(cafile=certifi.where())` to `urlopen`, or
  fetch the forecast in Swift (`URLSession`) and hand the JSON to the
  core. Only `forecast.py` is affected.

## What the prototype should prove

1. The BeeWare 3.14-b11 XCframework plus the core run in a SwiftUI app
   signed by a personal team, on a device.
2. `urlopen` reaches `api.open-meteo.com` over HTTPS (with or without
   certifi).
3. The app writes JSON to the App Group and the widget renders it,
   installed first via Xcode and then via SideStore.
4. Data survives the weekly reinstall.
