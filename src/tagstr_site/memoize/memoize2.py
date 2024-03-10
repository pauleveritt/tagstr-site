from __future__ import annotations

from typing import Any

from tagstr_site.typing import Decoded, Interpolation
from tagstr_site.memoize import TagStringArgs, TagStringCallable

def immutable_bits(*args: Decoded | Interpolation) -> tuple[str | tuple[Any], ...]:
    bits = []
    for arg in args:
        if isinstance(arg, str):
            bits.append(arg)
        else:
            bits.append((arg[0].__code__,))
    return tuple(bits)

def greet_tag(*args: TagStringArgs) -> str:
        result = []
        for arg in args:
            match arg:
                case str():
                    result.append(arg)
                case getvalue, _, _, _:
                    result.append(str(getvalue()))

        return f"{''.join(result)}"




def make_greet() -> TagStringCallable:
    """A closure which keeps an instance """
    cache_hit = 0
    template_cache = dict()
    def f(*args: TagStringArgs) -> str:
        nonlocal cache_hit

        # Get the "key" for these args
        template_key = immutable_bits(*args)

        # If it's in the cache, increment hit counter and return
        if template_key in template_cache:
            cache_hit += 1
            return template_cache[template_key]

        # Not in the cache. Generate the result and store it.
        template_cache[template_key] = greet_tag(*args)
        return template_cache[template_key]

    return f


def demo2() -> tuple[str, str, TagStringCallable]:
    """Stringify a LazyFString instance for each result"""

    greet = make_greet()
    name = "World"

    result0: str = greet'Hello {name}'
    result1: str = greet'Salut {name}'

    return result0, result1, greet
