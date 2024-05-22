"""Scratchpad for Paul to learn HTML parser."""
import dataclasses
from html.parser import HTMLParser
from typing import Any

import pytest

from tagstr_site.htmldom import interleave_with_values, join_with_values
from tagstr_site.tagtyping import Interpolation

HtmlAttributes = dict[str, Any]
HtmlChildren = list[str, "HtmlNode"]

PLACEHOLDER = "x$x"


def format_value(value: Any, conv, spec) -> str:
    match conv:
        case 'r':
            value = repr(value)
        case 's':
            value = str(value)
        case 'a':
            value = ascii(value)
        case None:
            pass
        case _:
            raise ValueError(f'Bad conversion: {conv!r}')
    return format(value, spec if spec is not None else '')


def test_format_value_no_conv():
    assert format_value(99, None, None) == "99"


def test_format_value_conv_r():
    assert format_value(99, "r", None) == "99"


def test_format_spec():
    assert format_value(1234567, None, ",") == "1,234,567"


def escape_placeholder(text: str) -> str:
    return text.replace("$", "$$")


def unescape_placeholder(text: str) -> str:
    return text.replace("$$", "$")


@dataclasses.dataclass
class HtmlNode:
    """A single HTML document object model node"""
    tag: str
    attributes: HtmlAttributes
    children: HtmlChildren = dataclasses.field(default_factory=list)

    def __str__(self) -> str:
        return f"<{self.tag} {self.attributes}>"


class HtmlBuilder(HTMLParser):
    def __init__(self):
        super().__init__()
        self.root = HtmlNode("", {})
        self.stack: list[HtmlNode] = [self.root]
        self.values: list[Any] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        this_node = HtmlNode(tag, dict(attrs))
        last_node = self.stack[-1]
        last_node.children.append(this_node)
        self.stack.append(this_node)

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(data)

    def handle_endtag(self, tag: str) -> None:
        node = self.stack.pop()
        if node.tag != tag:
            raise SyntaxError(f'Start tag {node.tag} does not match end {tag}')

    def result(self) -> HtmlNode:
        root = self.root
        self.close()
        match root.children:
            case []:
                raise ValueError("Nothing to return")
            case [element]:
                return element
            case _:
                return root

    def feed(self, data: str | Interpolation) -> None:
        match data:
            case str():
                super().feed(escape_placeholder(data))
            case getvalue, _, conv, spec:
                super().feed(PLACEHOLDER)
                value = format_value(getvalue(), conv, spec) if conv or spec else getvalue()
                self.values.append(value)


def test_tag_mismatch():
    builder = HtmlBuilder()
    with pytest.raises(SyntaxError):
        builder.feed("<div>Hello</span>")


def test_parse_parts():
    builder = HtmlBuilder()
    builder.feed("<div>Hello</div>")
    div = builder.result()
    assert div.tag == "div"
    assert div.children[0] == "Hello"


def test_interleave_with_values():
    tag = "h1"
    style = {"fon-weight": "bold"}
    greeting = "Hello"
    name = "Alice"

    substituted_string = "<x$x style=x$x color=blue>x$x, x$x!</x$x>"
    values = [tag, style, greeting, name, tag]

    result, _ = interleave_with_values(substituted_string, values)
    assert result == ["<", tag, " style=", style, " color=blue>", greeting, ", ", name, "!</", tag, ">"]


def test_join_with_values():
    joined, remainder = join_with_values("some-x$x-value", ["interpolated"])
    assert joined == "some-interpolated-value"
