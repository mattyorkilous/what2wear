# Research: What Scriptable can draw

This answers `issues/01-what-scriptable-can-draw.md`. Sources were
checked on 2026-10-10. Claims link to the Scriptable docs
(docs.scriptable.app, by Scriptable's author) or to Apple's Human
Interface Guidelines. Anything those pages don't state is marked
**(inference)** or **(community)**.

The repo facts it rests on: `widget.js` draws each icon in a 32×32
`DrawContext` with `respectScreenScale = true`. It fills a `shape`, then
an optional `pattern`, then strokes a `detail` at 1.2 pt in white at 67%.
It shows the result at `imageSize` 20×20 beside 13 pt `Font.systemFont`
text, with 12 pt headers and padding of 11/12. `src/what2wear/icons.py`
holds the paths, which use only `M`, `L`, `Q` and `Z`. Its docstring
says `DrawContext` "can't clip or dash, so stripes are rectangles". The
docs confirm this below.

## Short answer

**DrawContext is a flat-vector canvas: solid fills, solid strokes,
alpha, layered images and text. It has no gradients, no clipping, no
shadows, no dashes, and no line caps or joins.** The art should be
built from flat, layered, alpha-tinted shapes. That fits the emoji-like
look. Gradients exist only as a *widget or stack background*
(`LinearGradient`), and shadows exist only on *`WidgetText`*. A small
widget is 141–170 pt square, depending on the iPhone. Apple recommends
16 pt margins (11 pt for tight ones) and text of at least 11 pt. Scriptable
has a full set of rounded system fonts (`Font.boldRoundedSystemFont(n)`
and its siblings). A server-rendered PNG through `Request.loadImage()` or
`Image.fromData()` is a workable fallback. It adds a second network
dependency, so it needs a cache, and the docs don't name the supported
image formats.

## 1. DrawContext

Source: [DrawContext](https://docs.scriptable.app/drawcontext/).

**What it has (the complete API):**

| Area | Members |
|---|---|
| Canvas | `size`, `respectScreenScale` (default **false**), `opaque` (default **true**), `getImage()` |
| Colour state | `setFillColor(Color)`, `setStrokeColor(Color)`, `setLineWidth(n)` |
| Shapes | `fill`/`fillRect(rect)`, `fillEllipse(rect)`, `stroke`/`strokeRect(rect)`, `strokeEllipse(rect)` |
| Paths | `addPath(path)`, `fillPath()`, `strokePath()`. Both act on "the path that was added the latest" |
| Images | `drawImageInRect(image, rect)`, `drawImageAtPoint(image, point)` |
| Text | `drawText(text, point)`, `drawTextInRect(text, rect)`, `setFont(Font)`, `setTextColor(Color)`, `setTextAlignedLeft/Center/Right()` (`setFontSize` is deprecated) |

**What it lacks.** The page has no gradient fill, clip or mask call, no
shadow, no blend mode, no line cap or join, no dash pattern, and no
transform (translate, scale or rotate). Nothing in the API can produce
any of them.

**Path operations.** Source: [Path](https://docs.scriptable.app/path/).
The full list is `move`, `addLine`, `addCurve(point, control1, control2)`
(cubic), `addQuadCurve(point, control)`, `addRect`, `addEllipse`,
`addRoundedRect(rect, cornerWidth, cornerHeight)`, `addLines([Point])`,
`addRects([Rect])` and `closeSubpath`. In both curve methods the **end
point comes first**, which is why `widget.js` passes
`points[1], points[0]` for `Q`. Cubic curves (`C`), ellipses and rounded
rects are therefore available. Today's `M/L/Q/Z` parser could add `C`
cheaply if the new art wants it.

**Transparency.** `new Color(hex, alpha)` takes an alpha, and an alpha
argument wins over one written in the hex
([Color](https://docs.scriptable.app/color/)). Translucent fills and
strokes therefore work. Set `opaque = false` to keep the background
transparent, as `widget.js` already does. Note that `Color.dynamic(light,
dark)` is "not supported when used with `DrawContext`".

**Faking what's missing (inference):**
- *Shading or depth:* overlay a second path filled with a translucent
  white or black, such as a highlight on one side or a shadow band. This
  is the usual emoji technique and needs only fills with alpha.
- *Clipping:* there is no clip, so pattern shapes have to be cut to the
  outline geometrically, as the stripes already are. The other option is
  to draw the pattern in a separate `DrawContext` and composite it with
  `drawImageInRect`, which still doesn't clip.
- *Drop shadow:* draw the same shape in a translucent dark colour,
  offset by about 1 pt, before the real fill. It gives a hard shadow,
  not a blurred one.
- *Gradient inside a shape:* draw a few stepped bands of alpha fills.
  Only coarse banding is possible.

**`respectScreenScale` and image size.** With it on, the canvas is
multiplied by the screen scale: "a 200×200 canvas becomes 600×600 on a
screen with a scale of 3". With it off, images "can look blurry"
([DrawContext](https://docs.scriptable.app/drawcontext/)). The point
values for drawing stay the same. Only the backing pixels change. When
the image is shown, `WidgetImage.imageSize` sets its size in points, and
`resizable` defaults to true
([WidgetImage](https://docs.scriptable.app/widgetimage/)). Today's
32-unit canvas comes out at 96×96 px on a 3× phone and is shown at
20×20 pt (60 px), so the widget downsamples it. **(inference)** For the
sharpest lines, make the canvas size equal the display size in points,
or a simple multiple of it, and scale the stroke widths to match. A 1.2
unit line at 32 units shown at 20 pt is only about 0.75 pt on screen.

## 2. ListWidget / WidgetStack / WidgetText / WidgetImage

**ListWidget** ([docs](https://docs.scriptable.app/listwidget/)):
`backgroundColor`, `backgroundImage`, **`backgroundGradient:
LinearGradient`**, `spacing` (default 0), `url`, `refreshAfterDate`,
`setPadding(top, leading, bottom, trailing)` and `useDefaultPadding()`
(which discards `setPadding`). The content methods are `addText`,
`addDate`, `addImage`, `addSpacer(length | null)` and `addStack()`.
`addSpacer(null)` is flexible.

**WidgetStack** ([docs](https://docs.scriptable.app/widgetstack/)):
`backgroundColor`, `backgroundImage`, **`backgroundGradient`**,
`spacing`, `size` ("When a dimension is set to zero or less, the widget
will automatically decide a length for that dimension"), `cornerRadius`,
`borderWidth`, `borderColor`, `setPadding` and `useDefaultPadding`. It
lays out horizontally by default, with `layoutHorizontally()` and
`layoutVertically()` to choose. Cross-axis alignment comes from
`topAlignContent()` (the default), `centerAlignContent()` and
`bottomAlignContent()`. `url` works only in medium and large widgets, so
a small widget has a single tap target: `ListWidget.url`.

**Alignment: what's missing.** A stack has no leading, centre or
trailing alignment along its main axis, and no fixed column widths
beyond `size`. Text alignment methods "don't affect text inside stacks.
Use spacers there instead"
([WidgetText](https://docs.scriptable.app/widgettext/)). **(inference)**
To line up icons and labels, give every icon the same `imageSize` and
put it in a fixed-`size` stack. Use fixed `addSpacer(n)` between
columns and `addSpacer(null)` to push content to an edge. A row's
height follows its tallest child, so a fixed-`size` icon stack keeps
the rows even.

**WidgetText** ([docs](https://docs.scriptable.app/widgettext/)):
`text`, `textColor`, `font`, `textOpacity`, `lineLimit` (0 or less
means no limit), and `minimumScaleFactor`, which "sets the minimum
amount that text scales down to fit in the available space". It also
has **`shadowColor`, `shadowRadius` and `shadowOffset`**, which take
effect only when `shadowRadius > 0`. Its other members are `url`
(medium and large widgets only) and `left/center/rightAlignText()`.
Shadows exist for text, not for images or stacks.

**WidgetImage** ([docs](https://docs.scriptable.app/widgetimage/)):
`image`, `resizable` (default true), `imageSize` (null means full
size), `imageOpacity`, `cornerRadius`, `borderWidth`, `borderColor`,
`containerRelativeShape`, `tintColor` ("Changes the color of the image",
null keeps the original), `url`, `left/center/rightAlignImage()` and
`applyFittingContentMode()` / `applyFillingContentMode()`.

**LinearGradient** ([docs](https://docs.scriptable.app/lineargradient/)):
`colors: [Color]`, `locations: [number]` in the range 0–1 (the same
length as `colors`), and `startPoint` / `endPoint` in normalised 0–1
coordinates (both default to (0, 1)). The docs describe it only as
something "to be used in a widget". The only properties that take it
are `ListWidget.backgroundGradient` and `WidgetStack.backgroundGradient`.
**A gradient can't be used inside a DrawContext**, but a stack with a
gradient can sit behind an image, such as a rounded "tile" behind each
garment. That stack can have its own `cornerRadius`.

**Fonts** ([Font](https://docs.scriptable.app/font/)). Each of these
takes a size:
- `systemFont`, plus `ultraLight` / `thin` / `light` / `regular` /
  `medium` / `semibold` / `bold` / `heavy` / `black` + `SystemFont`, and
  `italicSystemFont`.
- **Rounded SF:** `ultraLightRoundedSystemFont` …
  `blackRoundedSystemFont`, nine weights in all. There is **no plain
  `Font.roundedSystemFont`**, so call a weighted name such as
  `Font.semiboldRoundedSystemFont(15)` or
  `Font.boldRoundedSystemFont(15)`.
- Monospaced, in the same nine weights:
  `…MonospacedSystemFont(size)`.
- Text styles without a size: `largeTitle`, `title1`–`3`, `headline`,
  `subheadline`, `body`, `callout`, `footnote`, `caption1`, `caption2`.
  The docs don't say whether they follow Dynamic Type.
- `new Font(name, size)` takes a named font. The same `Font` objects
  also work in `DrawContext.setFont`.

**Recommendation (inference):** use rounded fonts, which suit the emoji
feel and Apple's preference for the system font. Use
`semiboldRoundedSystemFont` for garment names, `boldRoundedSystemFont`
for the day header, and nothing under 11 pt (see §3).

**SF Symbols** ([SFSymbol](https://docs.scriptable.app/sfsymbol/)):
`SFSymbol.named(name)` returns null when the name doesn't exist. It has
`applyFont(Font)`, nine weight methods, and `.image` for use in a
`WidgetImage` or a `DrawContext`. This is useful for small glyphs such
as an office or home indicator, a warning sign or a snowflake for "if
cold", in place of emoji text.

**Appearance.** `Device.isUsingDarkAppearance()` is "not supported in
widgets" ([Device](https://docs.scriptable.app/device/)). Light and dark
backgrounds must come from `Color.dynamic`, which works on
`ListWidget`, stack and text colours but not inside `DrawContext`.

## 3. Small widget size and Apple's layout guidance

Source: [HIG: Widgets](https://developer.apple.com/design/human-interface-guidelines/widgets),
"Specifications" (last change log entry December 16, 2025), read from
the page's JSON (`developer.apple.com/tutorials/data/design/human-interface-guidelines/widgets.json`).

| Screen, portrait (pt) | Small (pt) | Medium (pt) | Models **(inference)**, matched by logical resolution |
|---|---|---|---|
| 430×932 | 170×170 | 364×170 | 14 Pro Max, 15 Plus, 15 Pro Max, 16 Plus |
| 428×926 | 170×170 | 364×170 | 12/13 Pro Max, 14 Plus |
| 414×896 | 169×169 | 360×169 | XR, XS Max, 11, 11 Pro Max |
| 414×736 | 159×159 | 348×157 | 6s/7/8 Plus |
| 393×852 | 158×158 | 338×158 | 14 Pro, 15, 15 Pro, 16 |
| 390×844 | 158×158 | 338×158 | 12, 12 Pro, 13, 13 Pro, 14 |
| 375×812 | 155×155 | 329×155 | X, XS, 11 Pro, 12/13 mini |
| 375×667 | 148×148 | 321×148 | SE (2nd/3rd gen), 6s/7/8 |
| 360×780 | 155×155 | 329×155 | unclear (12/13 mini render at 375×812) |
| 320×568 | 141×141 | 292×141 | SE (1st gen) |

The table has **no rows for 402×874 (16 Pro), 440×956 (16 Pro Max) or
later sizes**. **(inference)** Expect about 158–170 pt there. Design
for **158 pt**, the most common current size, and let flexible spacers
take up the extra space on 170 pt phones.

Apple's guidance, from the same page:
- **Margins:** "Use the standard margin width for widgets — 16 points
  for most widgets". When you need tighter margins, such as for content
  groupings, "setting margins of 11 points can work well". Today's
  `setPadding(11, 12, 11, 12)` uses the tight margin.
- **Text:** "display text using fonts at 11 points or larger".
- **Density:** "Sparse layouts can make the widget seem unnecessary,
  while overly dense layouts are less glanceable". "Avoid expanding a
  smaller widget's content to simply fill a larger area".
- **Fonts:** "Prefer using the system font, text styles, and SF
  Symbols".
- **Appearances:** Home Screen widgets can be light, dark, clear or
  tinted. "In a tinted appearance, the system desaturates the widget and
  its content". Clear adds translucency and Liquid Glass. Full-colour
  garment art will be desaturated in the tinted and clear modes.
  Scriptable doesn't expose a way to opt out **(inference: no such
  property in ListWidget or WidgetImage)**.

**Budget for a 158 pt small widget (inference):** with 16 pt margins
the content area is 126×126 pt, and with 11 pt margins it is 136×136 pt.
A header plus, say, four Garment rows at about
20–22 pt each, with 3–4 pt gaps, fill roughly 120 pt. Icons of 22–24 pt
and text of 13–15 pt therefore fit with room to spare. The empty space
today comes from 20 pt icons, 13 pt text and a trailing
`addSpacer()`, which pushes everything to the top.

## 4. Server-rendered PNG as a fallback

- [Request](https://docs.scriptable.app/request/) has `loadImage()`,
  which "Sends request and parses response as an image", and `load()`,
  which returns `Data`. Its `timeoutInterval` defaults to 60 s, and
  `widget.js` sets it to 10.
- [Image](https://docs.scriptable.app/image/): `Image.fromData(data)`
  and `Image.fromFile(path)` return null if the data can't be read.
  `size` is in pixels. The page **doesn't list supported formats**. It
  never says "PNG" and says nothing about SVG.
- [Data](https://docs.scriptable.app/data/) has `fromPNG(image)` and
  `fromJPEG(image)` for encoding, which suggests PNG is a native format
  **(inference)**. [FileManager](https://docs.scriptable.app/filemanager/)
  has `writeImage` and `readImage` for caching, but doesn't say what
  format it writes.
- **(inference)** There is no SVG decode, so the server would have to
  rasterise. The Python side would then need a renderer such as cairosvg
  or Pillow, which is a new dependency on PythonAnywhere.
- **Size limits (community):** Apple publishes no pixel limit, but
  developers report "Widget archival failed due to image being too
  large" for large images
  ([Apple forums](https://developer.apple.com/forums/thread/710745)) and
  a 30 MB widget memory limit
  ([Apple forums](https://developer.apple.com/forums/thread/842805)).
  Small icons at about 72×72 px, or one widget-sized PNG of about
  510×510 px, are far below both.

**Verdict:** this approach is technically sound, but it should be a
last resort. Every icon, or a whole pre-rendered widget, costs either a
second request or one image request alongside the JSON. It must be
cached next to `what2wear.json` so the offline fallback still shows
art, and its art loses tint or dark-mode adaptation unless the server
renders variants. Because DrawContext already has cubic curves,
ellipses, rounded rects, alpha and image compositing, the redrawn
emoji-style art should stay in DrawContext. The PNG route is worth it
only if the art truly needs gradients or blur.

## Supported vs not: at a glance

| Feature | DrawContext | Widget elements |
|---|---|---|
| Lines, quad/cubic Béziers, rects, rounded rects, ellipses | ✅ | — |
| Solid fill and stroke, line width | ✅ | — |
| Alpha (`new Color(hex, a)`) | ✅ | ✅ (`textOpacity`, `imageOpacity`) |
| Linear gradient | ❌ | ✅ `backgroundGradient` on ListWidget or WidgetStack only |
| Radial gradient | ❌ | ❌ |
| Clipping or masking | ❌ | Partial: `cornerRadius` and `containerRelativeShape` on images and stacks |
| Shadow | ❌ | ✅ WidgetText only (`shadowColor`, `shadowRadius`, `shadowOffset`) |
| Dash, line cap or join, transforms, blend modes | ❌ | — |
| Draw images or text into the canvas | ✅ | — |
| `Color.dynamic` (light/dark) | ❌ | ✅ |
| Rounded SF font | ✅ via `setFont` | ✅ `…RoundedSystemFont(size)`, 9 weights |
| SF Symbols | ✅ via `drawImageInRect(sym.image)` | ✅ `addImage(sym.image)` |
| Per-element tap URL in a small widget | — | ❌ (medium and large only) |
