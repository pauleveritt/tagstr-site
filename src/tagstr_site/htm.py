from __future__ import annotations

from collections.abc import Iterable
from html import escape
from html.parser import HTMLParser
from dataclasses import dataclass, field
from typing import Any, Callable, Generator, Literal, NamedTuple, Protocol, Sequence, runtime_checkable
import re
from collections import abc


@runtime_checkable
class Interpolation(Protocol):
    def __len__(self):
        ...

    def __getitem__(self, index: int):
        ...

    def getvalue(self) -> Callable[[], Any]:
        ...

    expr: str
    conv: Literal['a', 'r', 's'] | None
    format_spec: str | None


class InterpolationConcrete(NamedTuple):
    getvalue: Callable[[], Any]
    expr: str
    conv: Literal['a', 'r', 's'] | None = None
    format_spec: str | None = None


@runtime_checkable
class HTML(Protocol):
    tag: str
    attrs: dict
    children: Sequence[str | HTML]


# Use as an AST for HTML, with placeholders

@dataclass
class AstNode:
    tag: str | Callable[[Any], Any] = None
    attrs: list[tuple[str, str | None]] = field(default_factory=list)
    children: list[str | AstNode] = field(default_factory=list)


@dataclass
class HtmlNode:
    tag: str
    attrs: dict = field(default_factory=dict)
    children: list[str | HtmlNode] = field(default_factory=list)

    def __str__(self):
        attrs = []
        for k, v in self.attrs.items():
            match k, v:
                case str(), bool():
                    attrs.append(k)
                case str(), int():
                    attrs.append(f'{k}="{v}"')
                case str(), str():
                    attrs.append(f'{k}="{escape(v, quote=True)}"')
                case 'style', dict() as css:
                    # TODO are there other examples of dict structures
                    # beside the style attr? Could this occur in a
                    # custom tag?
                    decl = []
                    for property, value in css.items():
                        decl.append(f'{property}: {value}')
                    attrs.append(f'{k}="{escape(('; ').join(decl))}"')

        children = []
        for child in self.children:
            match child:
                case str():
                    children.append(escape(child))
                case HTML():
                    children.append(str(child))

        spaced = [f'<{self.tag}']
        if attrs:
            spaced.append(' ')
            spaced.append(' '.join(attrs))

        if children:
            spaced.append('>')
            spaced.append(''.join(children))
            spaced.append(f'</{self.tag}>')
        else:
            spaced.append('/>')

        return ''.join(spaced)


placeholder_re = re.compile(r'(x\$\d+x)')
placeholder_index_re = re.compile(r'x\$(?P<index>\d+)x')
valid_attribute_name_re = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_\-\.]*$')
valid_tagname_re = re.compile(r'^(?!.*--)(?!-?[0-9])[\w-]+(-[\w-]+|[a-zA-Z])?$')


def escape_placeholder(string: str) -> str:
    return string.replace('$', '$$')


def unescape_placeholder(string: str) -> str:
    return string.replace('$$', '$')


# NOTE: doesn't validate the following:
#
# Well-formed HTML - tags are properly closed - use stack field for this
# Valid HTML, such as li must be a child of ul or ol

class AstParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.root = AstNode()
        self.stack: list[AstNode] = [self.root]
        self.index = 0
        self.exprs: dict[int, str] = {}

    @property
    def parent(self):
        return self.stack[-1]

    def feed(self, arg: str | Interpolation) -> None:
        match arg:
            case str() as s:
                super().feed(escape_placeholder(s))
            case Interpolation() as interpolation:
                self.exprs[self.index] = interpolation.expr
                super().feed(f'x${self.index}x')
        self.index += 1

    def result(self) -> AstNode:
        self.close()
        match self.root.children:
            case []:
                raise ValueError('Nothing to return')
            case [child]:
                return child
            case _:
                return self.root

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        this_node = AstNode(tag, attrs)
        last_node = self.parent
        last_node.children.append(this_node)
        self.stack.append(this_node)

    def handle_data(self, data: str) -> None:
        children = self.parent.children
        children.append(data)

    def handle_endtag(self, tag: str) -> None:
        recovered_tag = self.recover_interpolations(tag)
        recovered_parent = self.recover_interpolations(self.parent.tag)
        if  recovered_tag != recovered_parent:
            raise RuntimeError(f"Unexpected </{recovered_tag}>")
        self.stack.pop()

    def recover_interpolations(self, tag: str) -> str:
        recovered_tag = []
        for arg in _split_by_placeholder(tag):
            match arg:
                case str() as s:
                    recovered_tag.append(s)
                case int() as i:
                    recovered_tag.append(f'{{{self.exprs[i]}}}')
        return ''.join(recovered_tag)

def _split_by_placeholder(s: str) -> str | int :
    for split in placeholder_re.split(s):
        if split != '':
            if m := placeholder_index_re.match(split):
                yield int(m.group('index'))
            else:
                yield unescape_placeholder(split)


@dataclass
class Fill:
    args: Sequence[str | Interpolation]

    def split_by_placeholder(self, s: str) -> Generator[str | Interpolation]:
        for split in placeholder_re.split(s):
            if split != '':
                if m := placeholder_index_re.match(split):
                    yield self.args[int(m.group('index'))]
                else:
                    yield unescape_placeholder(split)

    def fill(self, s: str, convert) -> Generator[dict | str | HTML]:
        for i, split in enumerate(self.split_by_placeholder(s)):
            match split:
                case Interpolation() as interpolation:
                    conversion = convert(interpolation.getvalue())
                    match conversion:
                        case Iterable() as it:
                            yield from it
                        case _:
                            yield conversion
                case str() as s:
                    yield s

    def convert_child(self, value: Any) -> Generator[HTML | str]:
        match value:
            case HTML():
                yield value
            case str() as s:
                yield escape(s)
            case Iterable() as it:
                for child in it:
                    yield from self.convert_child(child)
            case _:
                # NOTE we could apply the format_spec, conv here
                # applies to non-iterable values like integers, etc
                yield escape(str(value))

    def convert_attr_key(self, value: Any) -> str:
        match value:
            case str() as s:
                k = escape(s, quote=True)
                if not valid_attribute_name_re.match(k):
                    raise ValueError(f'Not a valid attribute name: {k!r}')
                return k
            case _:
                raise TypeError(f'Expected str, got {value!r}')

    def convert_attr_value(self, value: Any) -> dict | list[str]:
        match value:
            case dict() as d:
                return d
            case str() as s:
                return [escape(s, quote=True)]
            case int() as n:
                return [str(n)]
            case _:
                raise TypeError(f'Expected dict, str, or int, got {value!r}')

    def fill_attr(self, k: str, v: str | None) -> dict:
        def require_one_value(it):
            values = list(it)
            if len(values) > 1:
                raise ValueError("Value must be single")
            return values[0]

        match k, v:
            case str(), None:
                k_only = require_one_value(self.fill(k, self.convert_attr_value))
                match k_only:
                    case dict():
                        return k_only
                    case str():
                        return {k_only: True}
            case str(), str():
                return {
                    require_one_value(self.fill(k, self.convert_attr_key)):
                    require_one_value(self.fill(v, self.convert_attr_value))
                }

    def convert_name(self, value: Any) -> HTML | str:
        match value:
            case HTML() as node:
                return node
            case str() as s:
                return s
            case int() as n:
                return str(n)
            case abc.Callable() as f:
                return self.convert_name(f())
            case _:
                raise TypeError(f'Expected HTML, str, or int, got {value!r}')

    def fill_tag(self, tag: str, attrs, children) -> HTML:
        elems = list(self.fill(tag, self.convert_name))
        if any(isinstance(elem, HTML) for elem in elems):
            if len(elems) > 1:
                raise ValueError(f'Can only have a standalone HTML component in name: {elems!r}')
            node = elems[0]
            # FIXME this is probably not the right way to override things. Need
            # to determine a better default policy - and make it configurable
            # for any given node supporting the HTML protocol
            return type(node)(node.tag, node.attrs | attrs, node.children + children)
        else:
            tag = ''.join(elems)
            if not valid_tagname_re.match(tag):
                raise ValueError(f'Not a valid tag: {tag}')
            return HtmlNode(tag, attrs, children)

    def interpolate(self, tag: AstNode) -> HTML:
        children = []
        for child in tag.children:
            match child:
                case AstNode() as node:
                    children.append(self.interpolate(node))
                case str() as s:
                    children.extend(self.fill(s, self.convert_child))

        attrs = {}
        for k, v in tag.attrs:
            attrs |= self.fill_attr(k, v)

        return self.fill_tag(tag.tag, attrs, children)


def html(*args: str | Interpolation) -> HTML:
    parser = AstParser()
    for arg in args:
        parser.feed(arg)
    return Fill(args).interpolate(parser.result())


if __name__ == "__main__":
# FIXME this code currently fails
#     print(html"""<html>
#   <head><title>Test</title></head>
#   <body>
#     <h1 class="foo" {x}>Parse {y}</h1>
#     <{MyComponent} baz="bar"><p>Extra</p><//>',
#   </body>
# </html>
# """)

    # Something like the following looks a lot nicer, and we should show
    # this as the best practice - specially once the list item gets at
    # all somewhat complicated

    def items(n):
        for i in range(n):
            yield html"<li>Item #{i}</li>"

    print(html"<ol>{items(5)}</ol>")