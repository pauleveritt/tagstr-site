"""Outline a Fill strategy to interpolate the values."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Generator, Callable

from tagstr_site.examples import MainResult, Attrs
from tagstr_site.examples.htmlbuilder.hb1 import AstNode
from tagstr_site.examples.htmlbuilder.hb2 import ASTParser
from tagstr_site.htm import HTML
from tagstr_site.tagtyping import Interpolation

placeholder_re = re.compile(r'(x\$\d+x)')
placeholder_index_re = re.compile(r'x\$(?P<index>\d+)x')


@dataclass
class HtmlNode:
    """Implementation of a node or tree of an HTML DOM."""
    tag: str
    # Not yet implementing attributes, default to empty list
    attrs: dict = field(default_factory=dict)
    children: list[str | HtmlNode] = field(default_factory=list)


@dataclass
class Fill:
    """A policy that can fill in nodes in an AST, using interpolations."""

    # The convert callable is unused for now
    def fill(self, s: str, convert: Callable | None = None) -> Generator[dict | str | HTML]:
        """Split into any placeholders then fill them from interpolations."""
        # For now, simulate splitting and filling
        yield "I WAS FILLED" if "$" in s else s

    def interpolate(self, tag: AstNode) -> HTML:
        """The entry point for processing interpolations."""
        children = []
        for child in tag.children:
            match child:
                case AstNode() as node:
                    children.append(self.interpolate(node))
                case str() as s:
                    children.extend(self.fill(s))

        # For now, skip handling of attributes
        return self.fill_tag(tag=tag.tag, children=children)

    def fill_tag(self, tag: str, attrs: Attrs | None = None, children: list[str | HTML] | None = None) -> HTML:
        """Make an HTML-like-node with any policies."""
        # Reminder, not processing attributes yet.
        return HtmlNode(tag=tag, children=children)


def html(*args: str | Interpolation) -> HTML:
    parser = ASTParser()
    for arg in args:
        parser.feed(arg)
    return Fill().interpolate(parser.result())


def main() -> MainResult:
    """Main entry point for this example."""
    name = "World"
    # Manually typing the result since IDE can't process tag functions yet
    root_node: HtmlNode = html"<div>Hello {name}</div>"

    assert "div" == root_node.tag
    assert ["Hello ", "I WAS FILLED"] == root_node.children

    return ("div", root_node.tag), (root_node.children, ["Hello ", "I WAS FILLED"])


if __name__ == "__main__":
    print(main())
