"""No command at all, through the recording seam.

A bare invocation has nothing to record, so `apply` is handed no
command and gives the State straight back. That is what lets the shell
make the same call either way, and what makes the State it gets back
worth comparing before it writes.
"""

from datetime import date

from what2wear.core import apply
from what2wear.model import get_default_state

TODAY = date(2026, 8, 22)


def test_no_command_gives_back_the_very_same_state() -> None:
    state = get_default_state(TODAY)
    assert apply(state, None, TODAY) is state
