"""Tag string additions to the Python typing module.

This PEP focuses on the structure and behavior more than the implementations. These are expressed as protocols which
will live in Python's typing module."""
from typing import Protocol, Callable, Any, Literal, runtime_checkable


@runtime_checkable
class Decoded(Protocol):
    def __str__(self) -> str:
        ...

    raw: str


@runtime_checkable
class Interpolation(Protocol):
    def __len__(self):
        ...

    def __getitem__(self, index: int):
        ...

    def getvalue(self) -> Callable[[], Any]:
        ...

    expr: str
    conv: Literal['a', 'r', 's'] | None
    formatspec: str | None


class TagFunction(Protocol):
    def __call__(self, *args: Interpolation | Decoded) -> Any:
        ...
