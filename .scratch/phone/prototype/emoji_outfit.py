"""PROTOTYPE -- throwaway. Emoji renderings of one day's Outfit.

Four radically different widget renderings, each drawn against real
Outfits from the real State, laid out as iPhone widget-sized tiles.

    uv run python .scratch/phone/prototype/emoji_outfit.py

Writes emoji_outfit.html next to this file and opens it.
"""

import html
import subprocess
from datetime import date, timedelta
from pathlib import Path

from platformdirs import user_config_path

from what2wear.core import answer
from what2wear.model import DayType, Response
from what2wear.store import read_state

TODAY = date.today()
STATE = read_state(user_config_path("what2wear") / "state.json", TODAY)

# Colour words a Label might be -> the nearest coloured emoji. A Label
# is free text, so anything missing here falls back to the Label.
HEART = {
    "white": "🤍", "black": "🖤", "grey": "🩶", "brown": "🤎",
    "tan": "🤎", "beige": "🤎", "lblue": "🩵", "dblue": "💙",
    "blue": "💙", "yellow": "💛", "dgreen": "💚", "lgreen": "💚",
    "purple": "💜",
}
SQUARE = {
    "white": "⬜", "black": "⬛", "grey": "🩶", "brown": "🟫",
    "tan": "🟫", "beige": "🟨", "lblue": "🩵", "dblue": "🟦",
    "blue": "🟦", "yellow": "🟨", "dgreen": "🟩", "lgreen": "🟩",
    "purple": "🟪",
}
DAY = {DayType.OFFICE: "🏢", DayType.HOME: "🏠"}


def outerwear(r: Response) -> tuple[str, str] | None:
    o = r.outfit
    if o.sweater:
        return "🧶", o.sweater
    if o.jacket:
        return "🧥", o.jacket
    return None


def hedge(r: Response) -> str:
    return "❄️?" if r.cold is None else ""


# A -- emoji per garment, Label as text. Nothing is lost.
def variant_a(r: Response) -> str:
    o = r.outfit
    ow = outerwear(r)
    lines = [
        f"{DAY[r.day_type]} {r.on:%a %d}",
        f"👕 {o.shirt}",
        f"👖 {o.pants}",
        *([f"{ow[0]} {ow[1]} {hedge(r)}"] if ow else []),
        f"👞 {o.shoes}",
    ]
    return "\n".join(lines)


# B -- emoji per garment, colour as a heart. Pure emoji; a Label with no
# colour, or two Labels sharing one, falls back to text.
def colour(label: str, table: dict[str, str]) -> str:
    return table.get(label, label)


def variant_b(r: Response) -> str:
    o = r.outfit
    ow = outerwear(r)
    row = f"👕{colour(o.shirt, HEART)} 👖{colour(o.pants, HEART)}"
    row2 = f"👞{colour(o.shoes, HEART)}"
    if ow:
        row2 = f"{ow[0]}{colour(ow[1], HEART)}{hedge(r)} " + row2
    return f"{DAY[r.day_type]} {r.on:%a %d}\n{row}\n{row2}"


# C -- paper doll: a column of colour top to bottom, no garment emoji.
# The body's order says what each block is.
def variant_c(r: Response) -> str:
    o = r.outfit
    ow = outerwear(r)
    blocks = [
        *([colour(ow[1], SQUARE) + (" ❄️?" if r.cold is None else "")]
          if ow else []),
        colour(o.shirt, SQUARE),
        colour(o.pants, SQUARE),
        colour(o.shoes, SQUARE),
    ]
    return f"{DAY[r.day_type]}\n" + "\n".join(blocks)


# D -- one line, for the lock-screen inline slot.
def variant_d(r: Response) -> str:
    o = r.outfit
    ow = outerwear(r)
    extra = f" {ow[0]}{ow[1]}{hedge(r)}" if ow else ""
    return f"{DAY[r.day_type]} 👕{o.shirt} 👖{o.pants}{extra}"


# E -- emoji-style drawn icons in the garment's real colour, plus its
# full name. Unicode has one 👕, so the icons are drawn (SVG here; on
# the phone a server-rendered PNG, or Scriptable's DrawContext).
class Html(str):
    pass


FILL = {
    "white": "#f4f4f1", "black": "#26262a", "grey": "#8e8e93",
    "brown": "#6f4a2e", "tan": "#c9a878", "beige": "#e4d5b4",
    "lblue": "#9fc8ee", "dblue": "#23406e", "blue": "#3c67b4",
    "yellow": "#f2c84b", "dgreen": "#2e5e3b", "lgreen": "#a3d69c",
    "purple": "#7a4ea3", "ecru": "#efe6d0",
}
NAME = {
    "lblue": "Light Blue", "dblue": "Dark Blue", "lgreen": "Light Green",
    "dgreen": "Dark Green",
}
SHAPE = {
    "shirt": "M9 5 L4 8 L1 14 L6 16 L8 12 L8 29 L24 29 L24 12 L26 16 "
             "L31 14 L28 8 L23 5 L19 5 L16 9 L13 5 Z",
    "sweater": "M9 5 L3 9 L1 26 L6 26 L8 14 L8 29 L24 29 L24 14 L26 26 "
               "L31 26 L29 9 L23 5 Q16 10 9 5 Z",
    "jacket": "M9 4 L3 8 L1 27 L6 27 L8 14 L8 30 L24 30 L24 14 L26 27 "
              "L31 27 L29 8 L23 4 L19 4 L16 12 L13 4 Z",
    "pants": "M8 3 L24 3 L26 30 L19 30 L16 12 L13 30 L6 30 Z",
    "shoes": "M3 14 L11 14 Q14 19 20 19 L28 21 Q31 22 30 26 L3 26 Z",
}
EXTRA = {  # details drawn over the fill
    "shirt": '<path d="M16 9 L16 29" stroke-dasharray="1 3"/>',
    "sweater": '<path d="M8 27 L24 27 M1.5 23 L6.5 23 M25.5 23 L30.5 23"/>',
    "jacket": '<path d="M16 12 L16 30"/>',
    "pants": '<path d="M8 6 L24 6"/>',
    "shoes": '<path d="M3 23 L30 23"/>',
}


def icon(kind: str, label: str) -> str:
    fill = FILL.get(label, "#8e8e93")
    defs = ""
    if label == "striped":
        fill = "url(#stripes)"
        defs = ('<defs><pattern id="stripes" width="4" height="4" '
                'patternUnits="userSpaceOnUse"><rect width="4" height="4" '
                'fill="#f4f4f1"/><rect width="4" height="1.6" '
                'fill="#3c67b4"/></pattern></defs>')
    return (
        f'<svg viewBox="0 0 32 32" width="26" height="26">{defs}'
        f'<g stroke="#ffffffaa" stroke-width="1.2" stroke-linejoin="round" '
        f'fill="none"><path d="{SHAPE[kind]}" fill="{fill}"/>'
        f'{EXTRA[kind]}</g></svg>'
    )


def full_name(kind: str, label: str) -> str:
    return f"{NAME.get(label, label.title())} {kind.title()}"


def variant_e(r: Response) -> Html:
    o = r.outfit
    rows = [("shirt", o.shirt, ""), ("pants", o.pants, "")]
    for kind in ("sweater", "jacket"):
        label = getattr(o, kind)
        if label:
            rows.append((kind, label, " dim" if r.cold is None else ""))
    rows.append(("shoes", o.shoes, ""))
    day = "🏢 Office" if r.day_type is DayType.OFFICE else "🏠 Home"
    body = "".join(
        f'<div class="row{dim}">{icon(kind, label)}'
        f'<span>{html.escape(full_name(kind, label))}'
        f'{"<i>if cold</i>" if dim else ""}</span></div>'
        for kind, label, dim in rows
    )
    return Html(f'<div class="hd">{day} · {r.on:%a %-d}</div>{body}')


VARIANTS = [
    ("E", "Drawn icons + full name", variant_e, "small e"),
    ("E", "Drawn icons + full name", variant_e, "medium e"),
    ("A", "Emoji + Label", variant_a, "small"),
    ("B", "Emoji + colour heart", variant_b, "small"),
    ("C", "Paper doll", variant_c, "small"),
    ("D", "Lock-screen line", variant_d, "inline"),
]


def samples() -> list[tuple[str, Response]]:
    """Real dates, one per interesting case the rendering must show."""
    found: dict[str, Response] = {}
    for offset in range(60):
        on = TODAY + timedelta(days=offset)
        for weather, case in ((40.0, "cold"), (80.0, "warm"), (None, "unknown")):
            r = answer(STATE, on, {} if weather is None else {on: weather})
            kind = r.day_type.value
            ow = "jacket" if r.outfit.jacket else "sweater" if r.outfit.sweater else "none"
            found.setdefault(f"{kind} · {case} · {ow}", r)
    wanted = [
        "office · warm · none",
        "office · cold · sweater",
        "office · unknown · sweater",
        "home · cold · sweater",
        "home · cold · jacket",
        "home · unknown · jacket",
    ]
    return [(k, found[k]) for k in wanted if k in found]


def cell(rendered: str) -> str:
    return rendered if isinstance(rendered, Html) else html.escape(rendered)


def page() -> str:
    cases = samples()
    head = "".join(f"<th>{html.escape(k)}</th>" for k, _ in cases)
    rows = "".join(
        f"<tr><th>{key} — {name}</th>"
        + "".join(
            f'<td><div class="{size}">{cell(fn(r))}</div></td>'
            for _, r in cases
        )
        + "</tr>"
        for key, name, fn, size in VARIANTS
    )
    return f"""<!doctype html><meta charset="utf-8">
<title>PROTOTYPE — emoji Outfit</title>
<style>
body {{ font: 13px -apple-system, BlinkMacSystemFont, \"SF Pro Text\", system-ui, sans-serif; background: #ddd; margin: 16px; }}
th {{ text-align: left; vertical-align: top; padding: 6px; }}
td {{ padding: 6px; vertical-align: top; }}
.small {{ width: 158px; height: 158px; border-radius: 22px; background: #1c1c1e;
  color: #fff; padding: 14px; box-sizing: border-box; white-space: pre;
  font-size: 17px; line-height: 1.35; overflow: hidden; }}
.medium {{ width: 338px; height: 158px; border-radius: 22px;
  background: #1c1c1e; color: #fff; padding: 12px 14px;
  box-sizing: border-box; overflow: hidden; }}
.e {{ font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui; white-space: normal; padding: 11px 12px; line-height: 1; }}
.e .hd {{ font-size: 12px; color: #aaa; margin-bottom: 4px; font-weight: 600; }}
.e .row {{ display: flex; align-items: center; gap: 6px; height: 27px; }}
.e.small .row {{ font-size: 13px; }}
.e.medium .row {{ font-size: 15px; }}
.e .row.dim {{ opacity: .5; }}
.e i {{ font-style: normal; font-size: 11px; color: #9cf; margin-left: 5px; }}
.e.small i {{ display: none; }}
.e.small svg {{ width: 22px; height: 22px; }}
.inline {{ width: 260px; color: #111; white-space: pre; font-size: 15px;
  background: #fff8; padding: 4px 8px; border-radius: 8px; }}
</style>
<h1>PROTOTYPE — emoji Outfit</h1>
<p>Real Outfits from the State, today {TODAY}. Weather is forced per column;
❄️? = Outerwear only if it's cold (no forecast yet).</p>
<table><tr><th></th>{head}</tr>{rows}</table>"""


out = Path(__file__).with_suffix(".html")
out.write_text(page())
subprocess.run(["open", str(out)], check=False)
print(out)
