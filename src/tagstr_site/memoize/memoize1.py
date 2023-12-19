from __future__ import annotations

from tagstr_site.memoize import TagStringArgs, TagStringCallable


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
    count = 0
    def f(*args: TagStringArgs) -> str:
        nonlocal count
        count += 1
        return greet_tag(*args)

    return f


def demo1() -> tuple[str, str, TagStringCallable]:
    """Stringify a LazyFString instance for each result"""

    greet = make_greet()
    name = "World"

    result0: str = greet'Hello {name}'
    result1: str = greet'Salut {name}'

    return result0, result1, greet
