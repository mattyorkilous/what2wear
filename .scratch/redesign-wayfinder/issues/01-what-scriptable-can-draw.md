# 01 — What Scriptable can draw

Type: research
Status: resolved
Blocked by: none

## Question

What can a Scriptable small widget actually draw and lay out, so that
the garment art and the widget's new look stay within it?

- `DrawContext`: which path operations, fills (gradients?), strokes,
  shadows and transparency it supports; whether it can clip; how
  `respectScreenScale` and image size interact.
- `ListWidget` / `WidgetStack`: padding, spacing, alignment, fonts
  (sizes, weights, rounded SF), `minimumScaleFactor`, background
  gradients, and the small widget's real size in points on current
  iPhones.
- Whether a server-rendered PNG (`Image.fromData` from a fetch) is a
  sound fallback for art `DrawContext` can't draw.

Today's widget is `widget.js`; its icons come from
`src/what2wear/icons.py`.

## Answer

Findings on the `research/what-scriptable-can-draw` branch, at
`.scratch/redesign-wayfinder/research/01-what-scriptable-can-draw.md`.

- **DrawContext has no gradients, clipping, shadows, dashes, joins or
  transforms.** It has solid fills and strokes with alpha, quad and
  cubic curves (so the path parser can add `C`), rounded rects,
  ellipses, and drawing images and text. Emoji-style depth comes from
  translucent highlight/shade shapes and an offset dark copy drawn
  first. `Color.dynamic` doesn't resolve inside it.
- **Gradients only as backgrounds** (`LinearGradient` on the widget or
  a stack), so a rounded gradient tile behind each icon is possible.
  Shadows only on text.
- **Small widget: design for 158 pt** (12–16 and Pros); range 141–170.
  Apple says 16 pt margins (11 pt tight), text at least 11 pt, avoid
  sparse layouts.
- **Today's detail stroke renders ~0.75 pt** (32-unit box at 20 pt), so
  icons are drawn too small for their strokes.
- **Fonts:** `Font.semiboldRoundedSystemFont(n)` etc. (no plain rounded);
  SF Symbols via `SFSymbol.named`.
- **Alignment:** stacks align only top/centre/bottom and ignore text
  alignment, so columns line up through fixed-size icon stacks and
  fixed spacers. A small widget has one tap target.
- **Server-rendered PNG works** (`Request.loadImage`) but needs a Python
  rasteriser, a cached second fetch, and loses dark-mode adaptation.
  Keep the art in DrawContext; use a PNG only if the art truly needs
  gradients or blur.

## Comments

- Research in progress by a `/research` subagent; findings land on the
  `research/what-scriptable-can-draw` branch at
  `.scratch/redesign-wayfinder/research/01-what-scriptable-can-draw.md`.
