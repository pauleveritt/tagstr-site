from typing import Iterable, TextIO, Any, Interpolation

from .tstring import Template, _ValueInterpolation, _TemplateConcrete, t


# NOTE WELL: this is experimental code for fun. Your mileage may vary.

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
    raw = source if isinstance(source, str) else source.read()
    args: list[Interpolation | str] = []
    last_was_str: bool = False
    for part in _parse_str(raw):
        if isinstance(part, _InterpolationExpr):
            if not last_was_str:
                args.append("")
            value = eval(part, context)
            # TODO support Interpolation.conv and .format_spec
            args.append(_ValueInterpolation(value, part, None, None))
            last_was_str = False
        else:
            # TODO create a concrete Decoded class and handle .raw
            args.append(part)
            last_was_str = True
    if not last_was_str:
        args.append("")
    return _TemplateConcrete(tuple(args), tuple(arg for arg in args if isinstance(arg, str)), raw)


# >>> from tagstr_site.tstring import make_template
# >>> x = make_template("{a} and {b}", {"a": 10, "b": 42})
# >>> x
# <tagstr_site.tstring._TemplateConcrete object at 0x7f4c1c1b1d60>
# >>> x.raw
# '{a} and {b}'
# >>> x.args[0]
# ''
# >>> x.args[1]
# <tagstr_site.tstring._ValueInterpolation object at 0xffffb7463b10>>
# >>> x.args[1].value
# 10
# >>> x.args[2]
# ' and '
# >>> x.args[3].value
# 42
# >>> x.args[4]
# ''


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
# >>> x.raw
# '{l} and {g}'
# >>> x.args[0]
# ''
# >>> x.args[1].value
# 10
# >>> x.args[2]
# DecodedConcrete(' and ')
# >>> x.args[3].value
# 42
# >>> x.args[4]
# ''
