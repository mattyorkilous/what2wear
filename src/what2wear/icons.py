"""Garment icons: the one source of shapes the Day page and widget draw.

Each path sits in a 32x32 box and uses only `M`, `L`, `Q` and `Z`, the
moves the widget's `DrawContext` can make. It can't clip or dash, so
stripes are rectangles and the shirt placket is short segments.

A detail strokes each kind's own lines, then its outline, so a Garment
the color of the background still shows.
"""

from types import MappingProxyType

from what2wear.model import Garment

SHAPES = MappingProxyType(
    {
        "shirt": "M9 5 L4 8 L1 14 L6 16 L8 12 L8 29 L24 29 L24 12 "
        "L26 16 L31 14 L28 8 L23 5 L19 5 L16 9 L13 5 Z",
        "sweater": "M9 5 L3 9 L1 26 L6 26 L8 14 L8 29 L24 29 L24 14 "
        "L26 26 L31 26 L29 9 L23 5 Q16 10 9 5 Z",
        "jacket": "M9 4 L3 8 L1 27 L6 27 L8 14 L8 30 L24 30 L24 14 "
        "L26 27 L31 27 L29 8 L23 4 L19 4 L16 12 L13 4 Z",
        "pants": "M8 3 L24 3 L26 30 L19 30 L16 12 L13 30 L6 30 Z",
        "shoes": "M3 14 L11 14 Q14 19 20 19 L28 21 Q31 22 30 26 "
        "L3 26 Z",
    }
)

DETAILS = MappingProxyType(
    {
        kind: f"{lines} {SHAPES[kind]}"
        for kind, lines in {
            "shirt": "M16 9 L16 10 M16 13 L16 14 M16 17 L16 18 "
            "M16 21 L16 22 M16 25 L16 26",
            "sweater": "M8 27 L24 27 M1.5 23 L6.5 23 M25.5 23 L30.5 23",
            "jacket": "M16 12 L16 30",
            "pants": "M8 6 L24 6",
            "shoes": "M3 23 L30 23",
        }.items()
    }
)

# Stripes fit inside a top's torso.
STRIPES = " ".join(
    f"M{x} 13 L{x + 1.5} 13 L{x + 1.5} 28 L{x} 28 Z"
    for x in (10, 14, 18, 22)
)


def get_icon(kind: str, garment: Garment) -> dict[str, str]:
    """Draw `garment`, a `kind`, in its Colors.

    Returns:
        Its `shape` to fill with `fill`, a `pattern` to fill with
        `pattern_fill` if it's striped, and a `detail` to stroke.
    """
    return {
        "shape": SHAPES[kind],
        "fill": garment.color,
        **(
            {"pattern": STRIPES, "pattern_fill": garment.stripe_color}
            if garment.stripe_color
            and kind in {"shirt", "sweater", "jacket"}
            else {}
        ),
        "detail": DETAILS[kind],
    }
