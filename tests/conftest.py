"""What the whole suite shares: the example Wardrobe.

Loaded from `example.yaml` rather than restated in memory, so the
closets the core is exercised against are the ones the config boundary
really parses, and there is no second copy to drift.
"""

from pathlib import Path

from what2wear.config import load_state

EXAMPLE = Path(__file__).parent.parent / "example.yaml"
WARDROBE = load_state(EXAMPLE)
