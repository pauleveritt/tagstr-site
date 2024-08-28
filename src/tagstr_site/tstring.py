from typing import Interpolation, Decoded, Protocol, runtime_checkable, Annotated, TextIO


@runtime_checkable
class Template[T](Protocol):
    # CONSIDER What is T useful for?

    @property
    def args(self) -> tuple[Interpolation | Decoded, ...]:
        ...

    @property
    def source(self) -> str:
        ...


class EagerInterpolationConcrete(Interpolation):
    def __init__(self, interpolation: Interpolation):
        # For now, support both `.value` *and* `.getvalue()`.
        self.value = interpolation.getvalue()
        self.expr = interpolation.expr
        self.conv = interpolation.conv
        self.format_spec = interpolation.format_spec

    def getvalue(self) -> str:
        return self.value


class TemplateConcrete[T](Template[T]):
    _args: tuple[Interpolation | Decoded, ...]
    _source: str

    def __init__(self, args: tuple[Interpolation | Decoded, ...], source: str):
        self._args = args
        self._source = source

    @property
    def args(self) -> tuple[Interpolation | Decoded, ...]:
        return self._args

    @property
    def source(self) -> str:
        return self._source

    # CONSIDER __str__(self) returns `self.source`?


def t(*args: Interpolation | Decoded) -> Template:
    eager_args = tuple(EagerInterpolationConcrete(arg) if isinstance(arg, Interpolation) else arg for arg in args)
    # XXX support Interpolation.conv and .format_spec
    # XXX possibly we want `arg.raw` when `arg` is `Decoded`?
    source = "".join(f"{{{arg.expr}}}" if isinstance(arg, Interpolation) else arg for arg in args)
    return TemplateConcrete(eager_args, source)



# >>> from tagstr_site.tstring import t
# >>> x = t"hello {42}"
# >>> x.source
# 'hello {42}'
# >>> x.args[0]
# DecodedConcrete('hello ')
# >>> x.args[1].value
# 42



def as_t(text: TextIO | str) -> Template:
    """
    Read a template from a file-like object and return a `Template` object
    by evaluating the text as a template string *in the caller's context*.
    """
    # This is hacknology that follows a question by Paul in our Discord chat.
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
    s = (text if isinstance(text, str) else text.read())
    texpr = f"{dunder}\"{s.replace('"', '\\"')}\""

    # XXX I expect that setting `locals=calling_frame.f_locals` rather than
    # merging the two dicts should work fine, but it doesn't. A bug?
    template = eval(texpr, globals={**calling_globals, **calling_frame.f_locals})
    assert isinstance(template, Template)
    return template


# >>> from io import StringIO
# >>> from tagstr_site.tstring import as_t
# >>> g = 42
# >>> def f():
# ...     l = 10
# ...     return as_t(StringIO("{l} and {g}"))
# ...
# >>> f()
# <tagstr_site.tstring.TemplateConcrete object at 0x7f4c1c1b1d60>
# >>> f().source
# '{l} and {g}'
# >>> f().args[0].value
# 10
# >>> f().args[1]
# DecodedConcrete(' and ')
# >>> f().args[2].value
# 42
