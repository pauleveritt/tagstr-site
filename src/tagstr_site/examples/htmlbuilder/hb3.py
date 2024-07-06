"""Add an HTML tag function to call the builder."""

from tagstr_site.examples.htmlbuilder.hb1 import AstNode
from tagstr_site.examples.htmlbuilder.hb2 import AstParser
from tagstr_site.examples import MainResult
from tagstr_site.tagtyping import Interpolation


def html(*args: str | Interpolation) -> AstNode:
    parser = AstParser()
    for arg in args:
        parser.feed(arg)
    return parser.result()


def main() -> MainResult:
    """Main entry point for this example."""
    name = "World"
    # Manually typing the result since IDE can't process tag functions yet
    root_node: AstNode = html"<div>Hello {name}</div>"

    assert "div" == root_node.tag
    assert ["Hello ", 'x$1x'] == root_node.children

    return ("div", root_node.tag), (root_node.children, ["Hello ", "x$1x"])


if __name__ == "__main__":
    print(main())
