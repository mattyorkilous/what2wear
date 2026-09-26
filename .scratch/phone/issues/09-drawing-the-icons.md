# 09 — Drawing the garment icons on the phone

Type: grilling
Status: open
Blocked by: none

## Question

The widget shows a drawn, coloured icon for each Garment (see
[What an emoji Outfit looks like](04-emoji-outfit.md)). Scriptable
can't display SVG. Where are the icons drawn?

- The server renders PNGs and the widget loads them (keeps the drawing
  in Python, but likely needs Pillow or a hand-rolled rasteriser on
  PythonAnywhere)
- The Scriptable script draws them with `DrawContext` paths (no server
  change; the shapes live in the widget's JS)
- SF Symbols tinted in Scriptable (`tshirt.fill` exists; pants and a
  sweater probably don't)

This bears on the JSON endpoint in
[The web shell on PythonAnywhere](08-the-web-shell.md): colours and
kinds, or image URLs.
