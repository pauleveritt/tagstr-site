from typing import (
    Any,
    Sequence,
    Interpolation,
    Decoded,
    Protocol,
    runtime_checkable,
)
from dataclasses import dataclass

# -----------------------------------------------------------------------
# A simple "implementation" of proposed t-strings, using the older
# PEP 750 tag string behavior.
# -----------------------------------------------------------------------


@runtime_checkable
class Template(Protocol):
    # CONSIDER: in this example, `source` is a tuple of `str(Decoded)` for all
    # the `Decoded`s, while `raw` is a tuple of `Decoded.raw`. Do we want both?
    # Can both be constructed at compile time?
    source: tuple[str, ...]
    raw: tuple[str, ...]

    values: tuple[Any, ...]
    exprs: tuple[str, ...]
    convs: tuple[str | None, ...]
    format_specs: tuple[str | None, ...]

    @property
    def args(self) -> Sequence[Interpolation | Decoded]: ...


class _InterpolationLiteral(Interpolation):
    def __init__(
        self, value: Any, expr: str, conv: str | None, format_spec: str | None
    ):
        self.value = value
        self.expr = expr
        self.conv = conv
        self.format_spec = format_spec

    def getvalue(self) -> str:
        return self.value


class _DecodedLiteral(str):
    _raw: str

    def __new__(cls, value: str, raw: str):
        self = super().__new__(cls, value)
        self._raw = raw
        return self

    @property
    def raw(self) -> str:
        return self._raw


@dataclass(frozen=True)
class _TemplateLiteral(Template):
    source: tuple[str, ...]
    raw: tuple[str, ...]
    values: tuple[Any, ...]
    exprs: tuple[str, ...]
    convs: tuple[str | None, ...]
    format_specs: tuple[str | None, ...]

    def __post_init__(self):
        if not self.source:
            raise ValueError("source must not be empty")
        if len(self.source) != len(self.raw):
            raise ValueError("source and raw must have the same length")
        if len(self.values) != len(self.exprs) or len(self.values) != len(self.convs) or len(self.values) != len(self.format_specs):
            raise ValueError("values, exprs, convs, and format_specs must have the same length")
        if len(self.values) + 1 != len(self.source):
            raise ValueError("values must be one less than the length of source")

    @property
    def args(self) -> Sequence[Interpolation | Decoded]:
        return tuple(
            (
                _DecodedLiteral(self.source[i // 2], self.raw[i // 2])
                if i % 2 == 0
                else _InterpolationLiteral(
                    self.values[i // 2],
                    self.exprs[i // 2],
                    self.convs[i // 2],
                    self.format_specs[i // 2],
                )
            )
            for i in range(len(self.values) + len(self.source))
        )




def t(*args: Interpolation | str) -> Template:
    """
    Implement the proposed PEP 750 template string behavior, using the
    older cpython implementation of tagged strings.

    This is hilariously inefficient and exists only to demonstrate the
    expected behavior of a full implementation of PEP 750.

    See test_tstring.py for examples of the expected behavior.
    """

    # Our current cpython implementation of old-school tagged strings does
    # NOT provide even/odd behavior for `Decoded` and `Interpolation`.
    # So we effectively create it here.
    #
    # The rules are:
    #
    #   1. `args` *always* has length >= 1
    #   2. `args` *always* begins and ends with a `str` instance
    #   3. If necessary, blank-string `str` instances are created.
    #
    # This means that `args` will always have an odd length.
    #
    # The current cpython implementation has the following behvaior:
    #
    # some_tag"" -> ()  # empty tuple
    # some_tag"{42}" -> (Interpolation(42))  # no blank strings
    # some_tag"{42}{99}" -> (Interpolation(42), Interpolation(99))  # no blank strings
    #
    # see `test_tstring.py` for examples.

    eo_args: list[Interpolation | Decoded] = []
    last_was_str: bool = False

    for arg in args:
        if isinstance(arg, Interpolation):
            if not last_was_str:
                eo_args.append(_DecodedLiteral("", ""))
            value_interpolation = _InterpolationLiteral(arg.getvalue(), arg.expr, arg.conv, arg.format_spec)  # type: ignore
            eo_args.append(value_interpolation)
            last_was_str = False
        else:
            eo_args.append(arg)
            last_was_str = True

    if not last_was_str:
        eo_args.append(_DecodedLiteral("", ""))

    assert len(eo_args) >= 1
    assert len(eo_args) % 2 == 1

    source = tuple(str(arg) for arg in eo_args[::2])
    raw = tuple(arg.raw for arg in eo_args[::2])
    values = tuple(arg.value for arg in eo_args[1::2])
    exprs = tuple(arg.expr for arg in eo_args[1::2])
    convs = tuple(arg.conv for arg in eo_args[1::2])
    format_specs = tuple(arg.format_spec for arg in eo_args[1::2])

    return _TemplateLiteral(source, raw, values, exprs, convs, format_specs)
