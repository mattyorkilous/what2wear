"""The one failure the tool raises on its own.

Always a failure a person caused and can fix -- a State file that
cannot be read, a Reset naming a Shirt that is not there -- so the
shell prints it rather than tracing. Nothing tells the two apart, so
they are one thing.
"""


class What2wearError(Exception):
    """Something the wearer did that the wearer can undo."""
