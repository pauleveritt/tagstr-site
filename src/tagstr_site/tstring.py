from typing import (
    Any,
    Interpolation,
    Decoded,
    Protocol,
    runtime_checkable,
)

# -----------------------------------------------------------------------
# A simple "implementation" of proposed t-strings, using the older
# PEP 750 tag string behavior.
# -----------------------------------------------------------------------


@runtime_checkable
class Template(Protocol):
    @property
    def args(self) -> tuple[Interpolation | str, ...]: ...

    @property
    def source(self) -> tuple[str, ...]: ...

    @property
    def raw(self) -> str: ...


class _ValueInterpolation(Interpolation):
    def __init__(
        self, value: Any, expr: str, conv: str | None, format_spec: str | None
    ):
        self.value = value
        self.expr = expr
        self.conv = conv
        self.format_spec = format_spec

    def getvalue(self) -> str:
        return self.value



class _TemplateConcrete(Template):
    _args: tuple[Interpolation | str, ...]
    _source: tuple[str, ...]
    _raw: str

    def __init__(self, args: tuple[Interpolation | str, ...], source: tuple[str, ...], raw: str):
        self._args = args
        self._source = source
        self._raw = raw

    @property
    def args(self) -> tuple[Interpolation | str, ...]:
        return self._args

    @property
    def source(self) -> tuple[str, ...]:
        return self._source

    @property
    def raw(self) -> str:
        return self._raw

    # CONSIDER what, if anything, should __str__() return?


def t(*args: Interpolation | str) -> Template:
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

    eo_args: list[Interpolation | str] = []
    last_was_str: bool = False

    for arg in args:
        if isinstance(arg, Interpolation):
            if not last_was_str:
                # TODO ideally we'd construct something that conforms to `Decoded`
                # here. But AFAIK we *can't* with the current cpython implementation.
                eo_args.append("")
            value_interpolation = _ValueInterpolation(arg.getvalue(), arg.expr, arg.conv, arg.format_spec)  # type: ignore
            eo_args.append(value_interpolation)
            last_was_str = False
        else:
            eo_args.append(arg)
            last_was_str = True

    if not last_was_str:
        eo_args.append("")

    # Make a tuple of the odd elements, which is good to memoize off of
    source = tuple(eo_args[::2])

    # Cobble together something like a `raw` string that we might include in
    # a full implementation of PEP 750. This is a hack and it does not fully
    # work. It also does not support `conv` or `format_spec`.
    raw = "".join(
        f"{{{arg.expr}}}" if isinstance(arg, Interpolation) else arg for arg in eo_args  # type: ignore
    )
    return _TemplateConcrete(tuple(eo_args), source, raw)


# >>> from tagstr_site.tstring import t
# >>> x = t"hello {42}"
# >>> x.source
# (DecodedConcrete('hello '), '')
# >>> x.raw
# 'hello {42}'
# >>> x.args[0]
# DecodedConcrete('hello ')
# >>> x.args[1]
# <tagstr_site.tstring._ValueInterpolation object at 0xffffb72541a0>
# >>> x.args[1].value
# 42
# >>> x.args[2]
# ''




