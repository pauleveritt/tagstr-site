from typing import (
    Any,
    Sequence,
    Interpolation as OldInterpolation,
)
from dataclasses import dataclass



# A simple "implementation" of proposed t-strings, using the older
# PEP 750 tag string behavior.
#
# NOTE: the final implementation, these will *not* be dataclasses.


@dataclass(frozen=True)
class Interpolation:
    value: Any
    expr: str
    conv: str | None
    format_spec: str | None


@dataclass(frozen=True)
class Template:
    args: Sequence[str | Interpolation]
    """Args. Always of length 2n+1 for `n` interpolations."""



def t(*args: str | Interpolation) -> Template:
    """
    Implement the proposed PEP 750 template string behavior, using the
    older cpython implementation of tagged strings.

    See test_tstring.py for examples of the expected behavior.
    """

    eo_args: list[str | Interpolation] = []
    last_was_str: bool = False

    for arg in args:
        if isinstance(arg, OldInterpolation):
            if not last_was_str:
                eo_args.append("")
            value_interpolation = Interpolation(arg.getvalue(), arg.expr, arg.conv, arg.format_spec)  # type: ignore
            eo_args.append(value_interpolation)
            last_was_str = False
        else:
            eo_args.append(arg)
            last_was_str = True

    if not last_was_str:
        eo_args.append("")

    assert len(eo_args) >= 1
    assert len(eo_args) % 2 == 1

    return Template(tuple(eo_args))

