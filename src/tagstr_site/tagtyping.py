"""Tag string additions to the Python typing module.

This PEP focuses on the structure and behavior more than the implementations. These are expressed as protocols which
will live in Python's typing module."""
from typing import Protocol, Callable, Any, Literal


class Interpolation(Protocol):
    def __len__(self):
        ...

    def __getitem__(self, index: int):
        ...

    @property
    def getvalue(self) -> Callable[[], Any]:
        ...

    @property
    def expr(self) -> str:
        ...

    @property
    def conv(self) -> Literal["a", "r", "s"] | None:
        ...

    @property
    def formatspec(self) -> str | None:
        ...


class Decoded(Protocol):
    def __str__(self) -> str:
        ...

    @property
    def raw(self) -> str:
        ...


class TagFunction(Protocol):
    def __call__(self, *args: Interpolation | Decoded) -> Any:
        ...
