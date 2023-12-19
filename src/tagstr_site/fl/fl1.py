from __future__ import annotations

from tagstr_site import Chunk, Thunk


def fl(*args: Chunk | Thunk) -> str:
    """Tag string which is largely just an echo."""
    result = []
    for arg in args:
        match arg:
            case str():
                result.append(arg)
            case getvalue, _, _, _:
                result.append(str(getvalue()))

    return f"{''.join(result)}"


def demo():
    results = []
    # Make a variable that is in scope for all the tagged strings
    greeting = "Hello"
    for i in range(3):
        # The ``i`` variable is in-scope for each rendering when
        # getvalue() is called.
        result = fl'{i}: {greeting}'
        results.append(result)

    return "\n".join(results)
