# Research: widgets and apps without a native build

Answers `issues/03-widgets-without-a-native-app.md`. Sources checked
2026-09-26 against the vendors' own docs, App Store listings, release
notes and source repos. The Python-version checks in this note were run
against this repo's `src/` on the Mac.

Constraints from the repo: `requires-python = ">=3.14"`; `core.py` is
pure. It takes the forecast as a `weather` mapping argument and does no
I/O. Only `forecast.py` (`urllib.request.urlopen`) and `store.py` (a
JSON file) touch the outside world. Runtime deps are `holidays` (pure
Python, depends only on `python-dateutil`,
[PyPI JSON](https://pypi.org/pypi/holidays/json)) and `platformdirs`
(CLI only).

## Short answer

| Option | Cost | Shows the Outfit on Home/Lock Screen | Covers every command | Runs the Python core |
|---|---|---|---|---|
| **Scriptable widget** | Free (tips-only IAP) | **Yes**: text/emoji, Home and Lock Screen, refreshed on iOS's schedule | Not a good fit (JS UI via alerts/tables) | No (JavaScript). It only reads JSON that something else produced |
| **Shortcuts widget** | Free (built in) | **No.** It is a grid of buttons that run shortcuts. It shows no data | Could, as a menu of shortcuts calling an API | No |
| **Home-screen web app (PWA)** | Free | **No widget API.** Web Push and an icon badge only | **Yes**: an ordinary web UI | **Yes, locally**, via Pyodide 314 (CPython 3.14.2) in the page |
| **Pythonista 3** | **$9.99** | **No** on current iOS (its widget was a legacy Today extension, removed in iOS 18) | Yes, via its `ui` module | Python **3.10** only. This repo does not parse on 3.10 |
| **a-Shell** | Free | No widget of its own | CLI in a terminal, as today | Python **3.13**. This repo needs a small 3.13 backport (tested: 342/342 pass) |

Summary: nothing without a native build does both jobs. The strongest
combination is a **Pyodide PWA for the commands plus a Scriptable
widget** for the glance. The widget needs a JSON URL or file to read,
so it depends on where the State lives (ticket 02/05).

## 1. Scriptable

- **Price:** "Free", with "in-app purchases" that are tips ($0.99–$4.99).
  Latest version **1.7.19, 30 Sep 2024**, requires iOS 15.5+
  ([App Store](https://apps.apple.com/us/app/scriptable/id1405459188)).
  It has not been updated in two years. That is a maintenance risk,
  but I found no report that it breaks.
- **Fetch JSON:** `Request.loadJSON()`: "The response is expected to be a
  valid JSON string and is parsed into an object". It supports custom
  `headers`, so one bearer token works
  ([Request docs](https://docs.scriptable.app/request/)).
- **Render emoji text:** `ListWidget.addText()` "Adds a text element to
  the widget" ([ListWidget docs](https://docs.scriptable.app/listwidget/)).
  Emoji are plain Unicode text, so they render with no extra work.
- **Sizes:** `config.widgetFamily` is one of `small`, `medium`, `large`,
  `extraLarge`, `accessoryRectangular`, `accessoryInline`,
  `accessoryCircular`. Accessory widgets "can appear on the Lock Screen"
  ([config docs](https://docs.scriptable.app/config/)). Lock Screen
  widgets need iOS 16+ ([ListWidget docs](https://docs.scriptable.app/listwidget/)).
- **Refresh:** `refreshAfterDate` is only a floor. "The widget will not
  be refreshed before the date have been reached". "The refresh rate
  of a widget is partly up to iOS/iPadOS … a widget may not refresh if
  the device is low on battery or the user is rarely looking at the
  widget" ([ListWidget docs](https://docs.scriptable.app/listwidget/)).
  Apple's WidgetKit budget for a frequently viewed widget is "from 40 to
  70 refreshes" a day, which is "roughly … every 15 to 60 minutes"
  ([Keeping a widget up to date](https://developer.apple.com/documentation/widgetkit/keeping-a-widget-up-to-date)).
  That is ample for an outfit that changes once a day. Just after
  midnight the widget can show yesterday's Outfit for up to about an
  hour. Setting `refreshAfterDate` to local midnight narrows the gap.
- **Tap action:** `ListWidget.url`: "The URL will be opened when the
  widget is tapped" ([ListWidget docs](https://docs.scriptable.app/listwidget/)).
  Tapping can open the PWA.
- **Local files instead of a URL:** `FileManager.iCloud()` and
  `bookmarkedPath()` reach files "outside Scriptables documents
  directory". A bookmark used outside the app must be made with the
  "Create File Bookmark" Shortcuts action
  ([FileManager docs](https://docs.scriptable.app/filemanager/)). A
  widget can therefore read a JSON file that a-Shell writes to iCloud
  Drive. See §5.

## 2. Apple Shortcuts widgets

- The Shortcuts widget is a launcher. Apple documents only "tap a
  shortcut", and while it runs "the widget button displays a progress
  indicator". "If a shortcut has an action that can't be completed in
  the widget, the Shortcuts app automatically opens"
  ([Apple Support](https://support.apple.com/guide/shortcuts/run-shortcuts-from-the-home-screen-widget-apd029b36d05/ios)).
  Nothing in the guide describes the widget showing a shortcut's output.
  **It cannot show the day's Outfit.**
- A shortcut can fetch the Outfit when tapped and show it as a result or
  notification. That is a button, not a glance.
- Shortcuts is useful as glue. A "Time of Day" personal automation
  ([Apple Support: event triggers](https://support.apple.com/guide/shortcuts/apd932ff833f/ios))
  can run an a-Shell command each morning (§5). Scriptable also ships
  Shortcuts actions.

## 3. Home-screen web app (PWA)

- **Commands:** yes. It is an ordinary web UI, so every command,
  including the forms (`replace`, `swap`, `set-office-weekdays`), is just
  HTML. On iOS 26, "any site" added to the Home Screen opens as a web app
  with no manifest required
  ([WebKit: Safari 26.0](https://webkit.org/blog/17333/webkit-features-in-safari-26-0/),
  [WWDC25 post](https://webkit.org/blog/16993/news-from-wwdc25-web-technology-coming-this-fall-in-safari-26-beta/)).
- **Widget story: none.** Home-screen web apps get Web Push and the
  Badging API (iOS 16.4+) and no widget API
  ([WebKit: Web Push](https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/),
  [WebKit: Badging](https://webkit.org/blog/14112/badging-for-home-screen-web-apps/)).
  A morning push could carry the Outfit, but only with a server that
  knows the State and holds push keys.
- **Keep the core in Python, on the phone:** Pyodide **314.0.7
  (14 Sep 2026) ships CPython 3.14.2**
  ([changelog](https://pyodide.org/en/stable/project/changelog.html)), so
  the 3.14 source runs unchanged. `micropip` installs pure-Python wheels
  from PyPI ([loading packages](https://pyodide.org/en/stable/usage/loading-packages.html)),
  and `holidays` and `python-dateutil` are both `py3-none-any`.
  - `urlopen` will not work, because the browser has "no raw socket
    access" ([pyodide.http](https://pyodide.org/en/stable/usage/api/python-api/http.html)).
    Because `core.answer()` takes the forecast as an argument, the page
    can fetch Open-Meteo itself (JS `fetch` or `pyfetch`) and pass the
    mapping in. Open-Meteo returns `access-control-allow-origin: *`
    (checked with curl on 2026-09-26), so a static page can call it
    directly.
  - The State can live in IndexedDB through Pyodide's IDBFS, which needs
    `FS.syncfs()` ([FAQ](https://pyodide.org/en/stable/usage/faq.html)),
    or in `localStorage` as one JSON string.
  - **Durability:** WebKit's 7-day deletion of script-writable storage
    does not hit home-screen apps. They "have their own counter of days
    of use … We do not expect the first-party in such a web application
    to have its website data deleted"
    ([WebKit 2020](https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/)).
    Standalone web apps get the same quota as the browser origin
    ([WebKit storage policy](https://webkit.org/blog/14403/updates-to-storage-policy/)).
    The State then lives only on the phone, so it still needs an
    export/backup button.
  - Hosting a static page is $0 (e.g. GitHub Pages). The phone works
    without the Mac and offline after first load, once the Pyodide
    assets are cached.
- **Catch:** local State in the PWA is invisible to Scriptable, which
  cannot read another app's IndexedDB. A widget would need the State
  hosted (ticket 02), or the PWA would have to push a small "today's
  Outfit" JSON somewhere Scriptable can fetch.

## 4. Pythonista 3

- **$9.99**, latest **3.4 (27 Apr 2023)**, ships **Python 3.10**
  ([App Store](https://apps.apple.com/us/app/pythonista-3/id1085978097),
  [What's new in 3.4](https://omz-software.com/pythonista/docs-3.4/py3/ios/new.html)).
  3.4 added running scripts "as actions in Apple's Shortcuts app,
  without launching the app".
- **This repo does not run on 3.10.** Under Python 3.10's grammar,
  `model.py` fails to parse (`type` alias statements, 3.12+) and so does
  `forecast.py` (unparenthesised `except A, B:`, PEP 758, 3.14). The
  code also relies on 3.14 deferred annotations. A 3.10 backport would
  be a real rewrite of syntax across the package.
- **Widget:** Pythonista's widget is the Today-view app extension
  ([appex docs](https://omz-software.com/pythonista/docs/ios/appex.html)).
  Apple's iOS 18 release notes say "Legacy Today View extensions are
  removed in iOS 18" (116246167,
  [iOS & iPadOS 18 release notes](https://developer.apple.com/documentation/ios-ipados-release-notes/ios-ipados-18-release-notes)).
  **So on a current iPhone Pythonista has no widget.**
- Verdict: paid, stale, wrong Python, no widget. Ruled out.

## 5. a-Shell

- **Free**, actively maintained (2.2.2, released about 5 days before
  2026-09-26), iOS 14+. It ships **Python 3.13**
  ([App Store](https://apps.apple.com/us/app/a-shell/id1473805438)).
  The `holzschu/cpython` fork has branches up to `3.13`, none for 3.14
  ([GitHub](https://github.com/holzschu/a-shell)). `pip install` works
  "only if they are pure Python" ([README](https://github.com/holzschu/a-shell)),
  which covers `holidays`, `python-dateutil` and `platformdirs`.
- **Running this repo on 3.13 (tested):** two changes are enough.
  Parenthesise the one `except` in `forecast.py`, and add
  `from __future__ import annotations` to each module. With those, the
  CLI runs and **all 342 tests pass on CPython 3.13.12**. `urlopen`
  works there because it is real CPython with sockets. The cost is
  giving up two 3.14 features the repo currently uses.
- **Shortcuts:** "Execute Command … takes a list of commands and executes
  them in order". It runs in a lightweight extension where it can and
  otherwise opens the app ([README](https://github.com/holzschu/a-shell)).
  The CLI can therefore sit behind Shortcuts.
- **Widget:** a-Shell has none of its own. It can drive one indirectly:
  a daily Shortcuts automation runs `what2wear --json` (a new command)
  in a-Shell, writes the result to iCloud Drive, and a Scriptable widget
  reads that file through a Shortcuts-made bookmark (§1).
  **Unverified:** whether a-Shell's Execute Command completes from an
  automation while the phone is locked. That needs a prototype.
- Its UI is still a terminal, so it replaces the CLI rather than
  improving on it. Forms and `show-closet` stay typed commands.

## What this means for ticket 05

1. **Pyodide PWA + hosted "today" JSON + Scriptable widget.** The core
   stays on Python 3.14 unchanged. Every command gets a real UI and
   runs offline. The widget needs something hosted for Scriptable to
   fetch, even if the State itself is local.
2. **Hosted core (ticket 02) + PWA or Shortcuts front end + Scriptable
   widget.** One secret token in both. This is the simplest widget
   path, but the phone then needs the network for everything.
3. **a-Shell + Shortcuts automation + Scriptable reading an iCloud
   file.** Fully local and $0, with no hosting at all. The costs are a
   3.13 backport, a terminal UI, and a background-run question that
   still needs a prototype.

Pythonista and the Shortcuts widget are out: the first on price,
Python version and widget, the second because it cannot display data.
