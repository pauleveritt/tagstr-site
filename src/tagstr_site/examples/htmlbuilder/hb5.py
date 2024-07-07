"""Actually fill in the placeholders with interpolations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Generator, Callable

from tagstr_site.examples import TestSetup
from tagstr_site.examples.htmlbuilder.hb2 import AstParser
from tagstr_site.examples.htmlbuilder.hb4 import (
    placeholder_re, placeholder_index_re, HtmlNode,
    Fill as BaseFill,
)
from tagstr_site.htm import HTML
from tagstr_site.tagtyping import Interpolation


@dataclass
class Fill(BaseFill):
    """A policy that can fill in nodes in an AST, using interpolations."""
    args: Sequence[str | Interpolation]

    def split_by_placeholder(self, s: str) -> Generator[str | Interpolation]:
        """Split any strings with placeholders, then lookup the interpolation by position."""
        for split in placeholder_re.split(s):
            if split != '':
                if m := placeholder_index_re.match(split):
                    # We have a string with a placeholder. Get the index position
                    # from the placeholder, then grap the interpolation at
                    # that position in the args.
                    yield self.args[int(m.group('index'))]
                else:
                    # Not yet doing any unescaping of the placeholder
                    yield split

    def fill(self, s: str, convert: Callable = str) -> Generator[dict | str | HTML]:
        """Split into any placeholders then fill them from interpolations."""
        for i, split in enumerate(self.split_by_placeholder(s)):
            match split:
                # The 3.14 branch doesn't yet have Interpolation
                # case Interpolation() as interpolation:
                case tuple() as interpolation:
                    # Not yet running a convert function to escape string values.
                    # yield interpolation.getvalue()
                    yield interpolation[0]()
                case str() as s:
                    yield s

def html(*args: str | Interpolation) -> HTML:
    parser = AstParser()
    for arg in args:
        parser.feed(arg)
    return Fill(args).interpolate(parser.result())

def setup() -> HTML:
    name = "World"
    # Manually typing the result since IDE can't process tag functions yet
    root_node: HtmlNode = html"<div>Hello {name}</div>"
    return root_node

def test() -> TestSetup:
    root_node = setup()
    return ("div", root_node.tag), (root_node.children, ["Hello ", "World"])


def main():
    """Main entry point for this example."""
    root_node = setup()
    assert "div" == root_node.tag
    assert ["Hello ", "World"] == root_node.children


if __name__ == "__main__":
    main()
