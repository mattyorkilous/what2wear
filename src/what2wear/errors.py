"""Every failure the tool raises on its own.

Both are failures a person caused and can fix -- a State file that
cannot be read, a Reset naming a Shirt that is not there -- so the
shell catches them together and prints them rather than tracing.
"""


class StateError(Exception):
    """The State file cannot be read or written, or is not one."""


class UnknownShirtError(Exception):
    """A Reset named a Shirt the day's Closet does not hold."""
