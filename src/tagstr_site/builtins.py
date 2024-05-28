"""Additions to Python's built-in functions.

This PEP will lead to concrete implementations of the protocols as part of Python built-ins. As demo, we provide some
implementations, but also to show that alternate implementations are in-scope. For example, in tests."""

from typing import Any, Callable, Literal, NamedTuple


class DecodedConcrete(str):
    """An example of an implementation of a decoded string.

    This will be in CPython if the PEP is accepted. But there can also be alternate implementations of the protocol,
    for example, for tests.
    """

    _raw: str

    def __new__(cls, raw: str):
        decoded = raw.encode("utf-8").decode("unicode-escape")
        if decoded == raw:
            decoded = raw
        chunk = super().__new__(cls, decoded)
        chunk._raw = raw
        return chunk

    @property
    def raw(self):
        return self._raw


class InterpolationConcrete(NamedTuple):
    getvalue: Callable[[], Any]
    expr: str
    conv: Literal["a", "r", "s"] | None = None
    formatspec: str | None = None
