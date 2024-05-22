"""Demo of memoizing static parts of tag string.

The PEP mentions how tag strings can help memoize the unchanging parts.
This code provides an example.
"""

from __future__ import annotations

from functools import cache
from types import CodeType
from typing import *
from typing import Any

from tagstr_site.taglib import decode_raw
from tagstr_site.tagtyping import Decoded, Interpolation
from tagstr_site.htmltag import DomCodeGenerator


@cache
def make_compiled_template(*args: str | CodeType) -> Callable:
    builder = DomCodeGenerator()
    for i, arg in enumerate(decode_raw(*args)):
        match arg:
            case str():
                builder.feed(arg)
            case _:
                                                                                                                                                                                                                                                                                       builder.add_interpolation(i)
    code_obj = compile(builder.code, '<string>', 'exec')
    captured = {}
    exec(code_obj, captured)
    return captured['compiled']


def immutable_bits(*args: Decoded | Interpolation) -> tuple[str | tuple[Any], ...]:
    bits = []
    for arg in args:
        if isinstance(arg, str):
            bits.append(arg)
        else:
            bits.append((arg[0].__code__,))
    return tuple(bits)


def make_html_tag() -> Callable:
    def f(tag_name: str, attributes: Dict | None, children: List | None) -> Dict:
        d = {'tag_name': tag_name}
        if attributes:
            d['attributes'] = attributes
        if children:
            d['children'] = children
        return d

    def html_tag(*args: Decoded | Interpolation) -> Any:
        compiled = make_compiled_template(*immutable_bits(*args))
        return compiled(f, *args)
    return html_tag


def main():
    # Example usage to adapt. Subset of functionality in IDOM's vdom constructor
    html = make_html_tag()

    return html"""<html>
        <body attr="blah" yo={1}>
          <p>Hello</p>
        </body>
    </html>
    """


if __name__ == '__main__':
    main()


# def memoization_key(*args: Decoded | Interpolation) -> tuple[str, ...]:
#     return tuple(arg for arg in args if isinstance(arg, str))
#
#
# def make_greet_tag(*args: Decoded | Interpolation) -> str:
#     """Use caching of templates in greeting."""
#     result = []
#     for arg in args:
#         match arg:
#             case str():
#                 result.append(arg)
#             case getvalue, _, _, _:
#                 result.append(getvalue())
#
#     return f"{''.join(result)}!"
#
#
# def greet(*args: Decoded | Interpolation) -> str:
#     """The actual greet tag, as a cache-oriented wrapper."""
#     return make_greet_tag(*args)

# @cache
# def make_compiled_template(*args: Decoded | Interpolation) -> Callable:
#     print(f'Making compiled template {hash(args)}...')
#     builder = DomCodeGenerator()
#     for i, arg in enumerate(decode_raw(*args)):
#         match arg:
#             case str():
#                 builder.feed(arg)
#             case _:
#                 builder.add_interpolation(i)
#     print("Code:\n", builder.code)
#     code_obj = compile(builder.code, '<string>', 'exec')
#     captured = {}
#     exec(code_obj, captured)
#     return captured['compiled']
#
#
# @dataclass
# class GreetingTag:
#     count: int = 0
