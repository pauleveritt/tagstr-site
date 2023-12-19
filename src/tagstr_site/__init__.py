"""Code likely to be included in CPython itself."""

from typing import Any, Callable, NamedTuple, Self


class Chunk(str):
    def __new__(cls, value: str) -> Self:
        chunk = super().__new__(cls, value)
        chunk._cooked = None
        return chunk

    @property
    def cooked(self) -> str:
        """Convert string to bytes then, applying decoding escapes.

        Maintain underlying Unicode codepoints. Uses the same internal code
        path as Python's parser to do the actual decode.
        """
        if self._cooked is None:
            self._cooked = self.encode('utf-8').decode('unicode-escape')
        return self._cooked


class Thunk(NamedTuple):
    getvalue: Callable[[], Any]
    raw: str
    conv: str | None
    formatspec: str | None
