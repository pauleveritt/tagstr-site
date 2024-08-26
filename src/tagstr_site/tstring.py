from typing import Interpolation, Decoded, Protocol, runtime_checkable, Annotated


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
