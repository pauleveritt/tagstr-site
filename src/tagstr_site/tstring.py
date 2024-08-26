from typing import Interpolation, Decoded, Protocol, runtime_checkable, Annotated


@runtime_checkable
class Template[T](Protocol):
    # TODO What about Template[T]? What would [T] even be?

    @property
    def args(self) -> tuple[Interpolation | Decoded, ...]:
        ...

    @property
    def source(self) -> str:
        ...


class _EagerInterpolation(Interpolation):
    def __init__(self, interpolation: Interpolation):
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
    eager_args = tuple(_EagerInterpolation(arg) if isinstance(arg, Interpolation) else arg for arg in args)
    # XXX possibly we want `else arg.raw` if `arg` is `Decoded`?
    source = "".join(f"{{{arg.expr}}}" if isinstance(arg, Interpolation) else arg for arg in args)
    return TemplateConcrete(eager_args, source)



