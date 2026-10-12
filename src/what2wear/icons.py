"""Garment art: the one source of drawings the pages and widget share.

Each Garment is an ordered list of layers in a 76-unit box. A layer is
one path filled or stroked in one solid color, with an optional alpha,
and its path uses only `M`, `L`, `Q`, `C` and `Z`: what the widget's
`DrawContext` can draw. That has no transforms and can't clip, so the
silhouettes, drawn in a 64-unit space, are placed into the box with
their offsets and scale baked into the numbers, and stripes are the
silhouette cut into bands ahead of time.
"""

import math
import re
from collections.abc import Callable, Mapping
from functools import cache
from itertools import pairwise
from types import MappingProxyType

from what2wear.model import DayType, Garment

type Point = tuple[float, float]
type Layer = Mapping[str, str | float]


def _get_circle_path(cx: float, cy: float, r: float) -> str:
    """Draw a circle as four cubic curves.

    Defined above the shapes rather than below its callers, because
    they are built from it as the module loads.
    """
    k = r * 0.5523
    return (
        f"M{cx} {cy - r} "
        f"C{cx + k} {cy - r} {cx + r} {cy - k} {cx + r} {cy} "
        f"C{cx + r} {cy + k} {cx + k} {cy + r} {cx} {cy + r} "
        f"C{cx - k} {cy + r} {cx - r} {cy + k} {cx - r} {cy} "
        f"C{cx - r} {cy - k} {cx - k} {cy - r} {cx} {cy - r} Z"
    )


LONG_SLEEVES = (
    "L50 11 Q56 13 57 20 L60 50 Q60.3 52 58.3 52.2 L54 52.6 "
    "Q52.2 52.7 52 51 L49 27 L48.6 57 Q48.6 59 46.6 59 L17.4 59 "
    "Q15.4 59 15.4 57 L15 27 L12 51 Q11.8 52.7 10 52.6 L5.7 52.2 "
    "Q3.7 52 4 50 L7 20 Q8 13 14 11 Z"
)

SILHOUETTES = MappingProxyType(
    {
        "tee": "M23 9 Q32 16 41 9 L51 12 Q54 13 56 16 L61 23 "
        "Q62 25 60 26.5 L54.5 30 Q53 31 52 29.5 L48.5 25 L48.5 56 "
        "Q48.5 58.5 46 58.5 L18 58.5 Q15.5 58.5 15.5 56 L15.5 25 "
        "L12 29.5 Q11 31 9.5 30 L4 26.5 Q2 25 3 23 L8 16 "
        "Q10 13 13 12 Z",
        "button-up": "M23 8 L32 14 L41 8 " + LONG_SLEEVES,
        "sweater": "M23 9 Q32 15.5 41 9 " + LONG_SLEEVES,
        "jacket": "M22 7 L32 13 L42 7 " + LONG_SLEEVES,
        "pants": "M18 4 L46 4 Q47.5 4 47.6 5.5 L51 57.5 "
        "Q51.1 60 48.6 60 "
        "L37.5 60 Q35.4 60 35.2 58 L32 22 L28.8 58 Q28.6 60 26.5 60 "
        "L15.4 60 Q12.9 60 13 57.5 L16.4 5.5 Q16.5 4 18 4 Z",
        "shoe": "M5 36 Q5 29 10 28 L21 27 Q24 27 26 30 Q30 35 38 36 "
        "L50 38 Q59 40 59 47 L59 49 Q59 52 56 52 L8 52 Q5 52 5 49 Z",
    }
)

# Seams, plackets, cuffs and laces, stroked over the body.
LINES = MappingProxyType(
    {
        "tee": "M24.5 10.5 Q32 18 39.5 10.5",
        "button-up": "M32 14 L32 59 M5.2 46 L11.8 46.7 "
        "M58.8 46 L52.2 46.7",
        "sweater": "M25 11 Q32 17.5 39 11 M15.3 53 L48.7 53 "
        "M4.9 45.5 L12.1 46.3 M59.1 45.5 L51.9 46.3",
        "jacket": "M32 13 L32 59 M15.3 53 L48.7 53 M20 42 L26 40.5 "
        "M44 42 L38 40.5 M4.9 45.5 L12.1 46.3 M59.1 45.5 L51.9 46.3",
        "pants": "M16.8 10 L47.2 10 M32 10 L32 20 "
        "M18 10 Q20 16 25.5 10 M46 10 Q44 16 38.5 10",
        "shoe": "M5.5 46 L58.5 46 M24 32 L28 30 M27.5 35 L31.5 32.5 "
        "M31.5 37 L35 34.5",
    }
)

# Collars and lapels, filled in the tone.
PARTS = MappingProxyType(
    {
        "button-up": "M23 8 L32 14 L26 19 L20.5 10.5 Z "
        "M41 8 L32 14 L38 19 L43.5 10.5 Z",
        "jacket": "M22 7 L32 13 L32 15.5 L21 9.5 Z "
        "M42 7 L32 13 L32 15.5 L43 9.5 Z "
        + _get_circle_path(32, 15.5, 1.3),
    }
)

# An Office Shirt's five buttons, down its placket.
BUTTONS = " ".join(
    _get_circle_path(32, y, 1.8) for y in (21, 29, 37, 45, 53)
)

STRIPED_SILHOUETTES = frozenset(
    {"tee", "button-up", "sweater", "jacket"}
)

# Where each silhouette sits in the box, as (dx, dy, scale): a pair of
# shoes is two, the far one up and behind, drawn first.
PLACEMENTS = MappingProxyType({"shoe": ((14, -3, 0.86), (4, 10, 0.92))})
CENTERED_PLACEMENTS = ((6, 6, 1),)

SHADE = "#000000"
SHADE_ALPHA = 0.22
SHADE_DROP = 2.2
LINE_WIDTH = 1.8
OUTLINE_WIDTH = 2
BUTTON_WIDTH = 1.1
BUTTON_LIGHTNESS = 0.7

# Below this luminance a Color is dark, and its tone is lightened so
# it still shows on a dark background. The art can't know light from
# dark mode, so one rule serves both.
DARK_LUMINANCE = 0.35
LIGHTEN_AMOUNT = 0.62
DARKEN_AMOUNT = 0.42

STRIPE_WIDTH = 1.8
STRIPE_SPACING = 5
CURVE_STEPS = 8
MIN_POLYGON_POINTS = 3

SEGMENT = re.compile(r"([MLQCZ])([^MLQCZ]*)")


def get_art(
    kind: str, garment: Garment, day_type: DayType
) -> tuple[Layer, ...]:
    """Draw `garment`, a `kind` from the `day_type` Closet.

    A Shirt's cut follows its Closet: an Office Shirt is a long-sleeve
    button-up with a collar, a placket and buttons, and a Home Shirt a
    crew-neck tee. Each layer has a `d` path and either a `fill` or a
    `stroke` with its `width`, each `#rrggbb`, and an `alpha` when it
    isn't 1.

    Returns:
        Its layers in drawing order, in the 76-unit box.
    """
    color = garment.color
    paints = {
        "color": color,
        "stripe": garment.stripe_color,
        "tone": _get_tone(color),
        "button": _mix(color, "#ffffff", BUTTON_LIGHTNESS),
    }
    return tuple(
        _paint(layer, paints)
        for layer in get_art_template(kind, day_type)
        if _get_role(layer) != "stripe"
        or garment.stripe_color is not None
    )


def get_art_template(kind: str, day_type: DayType) -> tuple[Layer, ...]:
    """Draw a `kind` from the `day_type` Closet in no Color yet.

    The layers are `get_art`'s, striped, with each paint either a
    fixed `#rrggbb` or the role a Garment's Colors fill: `color`,
    `stripe`, `tone` or `button`. The page script paints them as the
    wearer picks Colors, by the same rule as `get_art`.

    Returns:
        Its layers in drawing order, in the 76-unit box.
    """
    silhouette = _get_silhouette(kind, day_type)
    layers = _get_layers(silhouette)
    return tuple(
        _place(layer, dx, dy, scale)
        for dx, dy, scale in PLACEMENTS.get(
            silhouette, CENTERED_PLACEMENTS
        )
        for layer in layers
    )


def _get_silhouette(kind: str, day_type: DayType) -> str:
    if kind == "shirt":
        return "button-up" if day_type is DayType.OFFICE else "tee"
    return "shoe" if kind == "shoes" else kind


def _get_layers(silhouette: str) -> tuple[Layer, ...]:
    """Draw `silhouette` in paint roles, in the 64-unit space.

    A soft shade under the body, the body, its stripes, the details
    and the outline in its tone, then any buttons.
    """
    body = SILHOUETTES[silhouette]
    return (
        {
            "d": _move(body, 0, SHADE_DROP),
            "fill": SHADE,
            "alpha": SHADE_ALPHA,
        },
        {"d": body, "fill": "color"},
        *(
            ({"d": _cut_stripes(silhouette), "fill": "stripe"},)
            if silhouette in STRIPED_SILHOUETTES
            else ()
        ),
        *(
            ({"d": PARTS[silhouette], "fill": "tone"},)
            if silhouette in PARTS
            else ()
        ),
        {"d": LINES[silhouette], "stroke": "tone", "width": LINE_WIDTH},
        {"d": body, "stroke": "tone", "width": OUTLINE_WIDTH},
        *(
            (
                {"d": BUTTONS, "fill": "button"},
                {"d": BUTTONS, "stroke": "tone", "width": BUTTON_WIDTH},
            )
            if silhouette == "button-up"
            else ()
        ),
    )


def _get_tone(color: str) -> str:
    """Get the outline-and-detail color of `color`.

    A dark Color's tone is lighter than it, and any other's darker.
    """
    if _get_luminance(color) < DARK_LUMINANCE:
        return _mix(color, "#ffffff", LIGHTEN_AMOUNT)
    return _mix(color, "#000000", DARKEN_AMOUNT)


def _get_luminance(color: str) -> float:
    """Weigh `color`'s sRGB channels by Rec. 709, from 0 to 1."""
    red, green, blue = (
        channel / 255 for channel in _get_channels(color)
    )
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def _get_channels(color: str) -> tuple[int, ...]:
    return tuple(int(color[at : at + 2], 16) for at in (1, 3, 5))


def _mix(color: str, other: str, amount: float) -> str:
    """Mix `color` `amount` of the way toward `other`.

    A channel rounds half up, as the page script's `Math.round` does,
    so the live redraw paints what the server draws.
    """
    return "#" + "".join(
        f"{math.floor(start + (end - start) * amount + 0.5):02x}"
        for start, end in zip(
            _get_channels(color), _get_channels(other), strict=True
        )
    )


def _get_role(layer: Layer) -> str:
    return str(layer.get("fill", layer.get("stroke")))


def _paint(layer: Layer, paints: Mapping[str, str | None]) -> Layer:
    """Fill `layer`'s role from `paints`, or keep its fixed color."""
    paint = _get_role(layer)
    return {
        **layer,
        ("fill" if "fill" in layer else "stroke"): paints.get(paint)
        or paint,
    }


def _move(path: str, dx: float, dy: float, scale: float = 1) -> str:
    """Scale every point of `path`, then offset it by `dx`, `dy`."""
    return " ".join(
        command
        + " ".join(
            _format_point((x * scale + dx, y * scale + dy))
            for x, y in points
        )
        for command, points in _split(path)
    )


def _split(path: str) -> tuple[tuple[str, tuple[Point, ...]], ...]:
    """Split `path` into its commands, each with its points."""
    return tuple(
        (
            command,
            _pair(tuple(float(number) for number in numbers.split())),
        )
        for command, numbers in SEGMENT.findall(path)
    )


def _pair(numbers: tuple[float, ...]) -> tuple[Point, ...]:
    return tuple(zip(numbers[::2], numbers[1::2], strict=True))


def _format_point(point: Point) -> str:
    return " ".join(_format(number) for number in point)


def _format(number: float) -> str:
    """Format `number` to two places at most, without trailing zeros."""
    text = f"{number:.2f}".rstrip("0").rstrip(".")
    return "0" if text == "-0" else text


@cache
def _cut_stripes(silhouette: str) -> str:
    """Cut `silhouette` into vertical stripes, as plain polygons.

    They run the silhouette's full height, sleeves included.
    """
    polygon = _flatten(SILHOUETTES[silhouette])
    bands = (
        _clip(polygon, left, left + STRIPE_WIDTH)
        for left in range(3, 62, STRIPE_SPACING)
    )
    return " ".join(
        "M" + " L".join(_format_point(point) for point in band) + " Z"
        for band in bands
        if len(band) >= MIN_POLYGON_POINTS
    )


def _flatten(path: str) -> tuple[Point, ...]:
    """Trace a one-figure `path` as points, its curves sampled."""
    segments = tuple(
        (command, points)
        for command, points in _split(path)
        if command != "Z"
    )
    return tuple(
        point
        for (_, previous), (command, points) in pairwise(
            (("M", ((0.0, 0.0),)), *segments)
        )
        for point in (
            points
            if command in {"M", "L"}
            else _sample_curve((previous[-1], *points))
        )
    )


def _sample_curve(controls: tuple[Point, ...]) -> tuple[Point, ...]:
    """Sample the Bézier curve through `controls`, past its start."""
    return tuple(
        _get_curve_point(controls, step / CURVE_STEPS)
        for step in range(1, CURVE_STEPS + 1)
    )


def _get_curve_point(controls: tuple[Point, ...], t: float) -> Point:
    """Find the point `t` along a Bézier curve, by de Casteljau."""
    if len(controls) == 1:
        return controls[0]
    return _get_curve_point(
        tuple(
            (ax + (bx - ax) * t, ay + (by - ay) * t)
            for (ax, ay), (bx, by) in pairwise(controls)
        ),
        t,
    )


def _clip(
    polygon: tuple[Point, ...], left: float, right: float
) -> tuple[Point, ...]:
    """Cut `polygon` to the band from `left` to `right`.

    Sutherland-Hodgman, against each of the band's two edges.
    """
    return _clip_edge(
        _clip_edge(polygon, left, lambda x: x >= left),
        right,
        lambda x: x <= right,
    )


def _clip_edge(
    polygon: tuple[Point, ...],
    edge: float,
    keeps: Callable[[float], bool],
) -> tuple[Point, ...]:
    return tuple(
        point
        for start, end in zip(
            polygon, (*polygon[1:], *polygon[:1]), strict=True
        )
        for point in _clip_side(start, end, edge, keeps)
    )


def _clip_side(
    start: Point,
    end: Point,
    edge: float,
    keeps: Callable[[float], bool],
) -> tuple[Point, ...]:
    """Keep what of the side from `start` to `end` is inside `edge`.

    Returns:
        Where the side crosses `edge`, if it does, then `end` if it's
        kept.
    """
    crossing = (
        (_get_crossing(start, end, edge),)
        if keeps(start[0]) != keeps(end[0])
        else ()
    )
    return crossing + ((end,) if keeps(end[0]) else ())


def _get_crossing(start: Point, end: Point, x: float) -> Point:
    t = (x - start[0]) / (end[0] - start[0])
    return (x, start[1] + (end[1] - start[1]) * t)


def _place(layer: Layer, dx: float, dy: float, scale: float) -> Layer:
    """Scale and offset `layer` into the 76-unit box, widths too."""
    return {
        **layer,
        "d": _move(str(layer["d"]), dx, dy, scale),
        **(
            {"width": round(float(layer["width"]) * scale, 3)}
            if "width" in layer
            else {}
        ),
    }
