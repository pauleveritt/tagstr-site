# fl tag implementation - fl version of f-string eval

from __future__ import annotations

from dataclasses import dataclass
from typing import *

from tagstr_site.tagtyping import Decoded, Interpolation

DecodedConcrete = str

@dataclass
class LazyFString:
    args: Sequence[Decoded | Interpolation]

    def __str__(self) -> str:
        result = []
        for arg in self.args:
            match arg:
                case DecodedConcrete():
                    result.append(arg)
                case getvalue, _, _, _:
                    result.append(str(getvalue()))

        return f"{''.join(result)}"


def fl(*args: Decoded | Interpolation) -> LazyFString:
    return LazyFString(args)


def demo():
    """Stringify a LazyFString instance for each result"""
    results = []
    greeting = "Hello"
    for i in range(3):
        result = fl'{i}: {greeting}'
        results.append(result)

    # When __str__ is called, getvalue() is called, which
    # gets ``i`` from the scope. That value is now 2.
    return "\n".join([str(result) for result in results])
