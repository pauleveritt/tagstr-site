"""Handle attributes. Also: escaping/unescaping."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Generator, Callable

from tagstr_site.examples import TestSetup, Attrs
from tagstr_site.examples.htmlbuilder.hb2 import AstParser
from tagstr_site.examples.htmlbuilder.hb4 import HtmlNode, AstNode
from tagstr_site.examples.htmlbuilder.hb5 import Fill as BaseFill
from tagstr_site.htm import HTML
from tagstr_site.tagtyping import Interpolation

valid_attribute_name_re = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_\-\.]*$')
valid_tagname_re = re.compile(r'^(?!.*--)(?!-?[0-9])[\w-]+(-[\w-]+|[a-zA-Z])?$')


@dataclass
class Fill(BaseFill):
    """A policy that can fill in nodes in an AST, using interpolations."""

    def fill(self, s: str, convert: Callable = str) -> Generator[dict | str | HTML]:
        """Split into any placeholders then fill them from interpolations."""
        for i, split in enumerate(self.split_by_placeholder(s)):
            match split:
                # The 3.14 branch doesn't yet have Interpolation
                case Interpolation() as interpolation:
                    # value = interpolation.getvalue()
                    value = interpolation[0]()
                    yield value if convert is None else convert(value)
                case str() as s:
                    yield s

    def fill_attr(self, k: str, v: str | None) -> dict:
        """Process attribute keys and values for any interpolations."""

        # Not handling extra stuff like looking for boolean-style attributes, nor
        # handling actual dicts, nor un-escaping.

        interpolated_key = list(self.fill(k))[0]
        interpolated_value = list(self.fill(v))[0]
        return {interpolated_key: interpolated_value}

    def fill_tag(self, tag: str, attrs: Attrs | None = None, children: list[str | HTML] | None = None) -> HTML:
        """Support interpolation in the tag name for dynamic heading levels and subcomponents."""
        elems = list(self.fill(tag))
        tag = ''.join(elems)
        return HtmlNode(tag, attrs, children)

    def interpolate(self, tag: AstNode) -> HTML:
        children = []
        for child in tag.children:
            match child:
                case AstNode() as node:
                    children.append(self.interpolate(node))
                case str() as s:
                    children.extend(self.fill(s))

        attrs = {}
        for k, v in tag.attrs:
            attrs |= self.fill_attr(k, v)

        return self.fill_tag(tag.tag, attrs, children)


def html(*args: str | Interpolation) -> HTML:
    parser = AstParser()
    for arg in args:
        parser.feed(arg)
    return Fill(args).interpolate(parser.result())


def setup() -> HTML:
    name = "World"
    level = 1
    title = "The Greeting"
    # Manually typing the result since IDE can't process tag functions yet
    root_node: HtmlNode = html'<h{level} title={title}>Hello {name}</h{level}>'
    return root_node

def test() -> TestSetup:
    root_node = setup()
    return ("h1", root_node.tag), (root_node.attrs, dict(title="The Greeting")), (root_node.children, ["Hello ", "World"])

def main():
    """Main entry point for this example."""
    root_node = setup()
    assert "h1" == root_node.tag
    assert dict(title="The Greeting") == root_node.attrs
    assert ["Hello ", "World"] == root_node.children


if __name__ == "__main__":
    main()
