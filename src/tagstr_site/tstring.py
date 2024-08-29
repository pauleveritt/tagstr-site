from typing import (
    Annotated,
    Any,
    Interpolation,
    Iterable,
    Protocol,
    runtime_checkable,
    TextIO,
)

# -----------------------------------------------------------------------
# A simple "implementation" of proposed t-strings, using the older
# PEP 750 tag string behavior.
# -----------------------------------------------------------------------


@runtime_checkable
class Template[T](Protocol):
    # CONSIDER What is T useful for?

    @property
    def args(self) -> tuple[Interpolation | str, ...]: ...

    @property
    def source(self) -> str: ...


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


class _TemplateConcrete[T](Template[T]):
    _args: tuple[Interpolation | str, ...]
    _source: str

    def __init__(self, args: tuple[Interpolation | str, ...], source: str):
        self._args = args
        self._source = source

    @property
    def args(self) -> tuple[Interpolation | str, ...]:
        return self._args

    @property
    def source(self) -> str:
        return self._source

    # CONSIDER what should __str__(self) return?


def t(*args: Interpolation | str) -> Template:
    eager_args = tuple(
        _ValueInterpolation(arg.getvalue(), arg.expr, arg.conv, arg.format_spec)  # type: ignore
        if isinstance(arg, Interpolation)
        else arg
        for arg in args
    )
    # TODO support Interpolation.conv and .format_spec
    # XXX possibly we want `arg.raw` when `arg` is `Decoded`?
    source = "".join(
        f"{{{arg.expr}}}" if isinstance(arg, Interpolation) else arg for arg in args  # type: ignore
    )
    return _TemplateConcrete(eager_args, source)


# >>> from tagstr_site.tstring import t
# >>> x = t"hello {42}"
# >>> x.source
# 'hello {42}'
# >>> x.args[0]
# DecodedConcrete('hello ')
# >>> x.args[1]
# <tagstr_site.tstring._ValueInterpolation object at 0xffffb72541a0>
# >>> x.args[1].value
# 42


# -----------------------------------------------------------------------
# An experimental method for taking an arbitrary string and converting
# it to a Template by evaluating it with explicitly provided context.
# -----------------------------------------------------------------------


class _InterpolationExpr(str):
    pass


def _parse_str(s: str) -> Iterable[str | _InterpolationExpr]:
    """Parse a string like it's a t-string. Kinda."""

    # This is a cheap implementation for demonstration only. I doubt it
    # handles all the cases correctly. It's also not very efficient. etc.

    i = 0
    n = len(s)
    buffer = []

    while i < n:
        if s[i] == "{":
            if i + 1 < n and s[i + 1] == "{":
                buffer.append("{")
                i += 2
            else:
                if buffer:
                    yield "".join(buffer)
                    buffer = []
                i += 1
                brace_start = i
                depth = 1
                while i < n and depth > 0:
                    if s[i] == "{":
                        depth += 1
                    elif s[i] == "}":
                        depth -= 1
                    i += 1
                if depth != 0:
                    raise SyntaxError("t-string: expecting '}'")
                yield _InterpolationExpr(s[brace_start : i - 1])
        elif s[i] == "}":
            if i + 1 < n and s[i + 1] == "}":
                buffer.append("}")
                i += 2
            else:
                raise SyntaxError("t-string: expecting '}'")
        else:
            buffer.append(s[i])
            i += 1

    if buffer:
        yield "".join(buffer)


def make_template(source: TextIO | str, context: dict[str, Any]) -> Template:
    """
    Read a template from a file-like object or a `str` and return a `Template`
    instance.

    Use the provided `context` dictionary to evaluate the template string.
    """
    source = source if isinstance(source, str) else source.read()
    args: list[Interpolation | str] = []
    for part in _parse_str(source):
        if isinstance(part, _InterpolationExpr):
            value = eval(part, context)
            # TODO support Interpolation.conv and .format_spec
            args.append(_ValueInterpolation(value, part, None, None))
        else:
            # TODO create a concrete Decoded class and handle .raw
            args.append(part)
    return _TemplateConcrete(tuple(args), source)


# >>> from tagstr_site.tstring import make_template
# >>> x = make_template("{a} and {b}", {"a": 10, "b": 42})
# >>> x
# <tagstr_site.tstring._TemplateConcrete object at 0x7f4c1c1b1d60>
# >>> x.source
# '{a} and {b}'
# >>> x.args[0]
# <tagstr_site.tstring._ValueInterpolation object at 0xffffb7463b10>>
# >>> x.args[0].value
# 10
# >>> x.args[1]
# ' and '
# >>> x.args[2].value
# 42


# -----------------------------------------------------------------------
# A hacknological experimental method for taking an arbitrary string
# and converting it to a Template by evaluating it with the caller's
# context.
# -----------------------------------------------------------------------


def as_t(text: TextIO | str) -> Template:
    """
    Read a template from a file-like object and return a `Template` object
    by evaluating the text as a template string *in the caller's context*.
    """
    # This is HACKNOLOGY that follows a question by Paul in our Discord chat.
    import inspect

    frame = inspect.currentframe()
    assert frame is not None
    calling_frame = frame.f_back
    assert calling_frame is not None

    # make sure the `t` function is available in the eval context; wouldn't
    # be necessary if cpython supported t-strings directly
    dunder = "__as_t__t__"
    calling_globals = dict(calling_frame.f_globals)
    assert dunder not in calling_globals
    calling_globals[dunder] = t

    # Build an expression that evaluates to the template string.
    s = text if isinstance(text, str) else text.read()
    texpr = f"{dunder}\"{s.replace('"', '\\"')}\""

    # XXX I expect that setting `locals=calling_frame.f_locals` rather than
    # merging the two dicts should work fine, but it doesn't. A bug?
    template = eval(texpr, {**calling_globals, **calling_frame.f_locals})
    assert isinstance(template, Template)
    return template


# >>> from tagstr_site.tstring import as_t
# >>> g = 42
# >>> def f():
# ...     l = 10
# ...     return as_t("{l} and {g}")
# ...
# >>> x = f()
# >>> x
# <tagstr_site.tstring._TemplateConcrete object at 0x7f4c1c1b1d60>
# >>> x.source
# '{l} and {g}'
# >>> x.args[0].value
# 10
# >>> x.args[1]
# DecodedConcrete(' and ')
# >>> x.args[2].value
# 42
