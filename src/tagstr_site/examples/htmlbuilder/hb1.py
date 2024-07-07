"""Basic HTML parser."""
from __future__ import annotations
from dataclasses import dataclass, field
from html.parser import HTMLParser

from tagstr_site.examples import TestSetup, Attrs


@dataclass
class AstNode:
    """Parsed representation of an HTML tag string."""

    tag: str | None = None
    # Not yet implementing attributes, default to empty list
    attrs: list[tuple[str, str | None]] = field(default_factory=list)
    children: list[str | AstNode] = field(default_factory=list)


class AstParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.root = AstNode()
        self.stack: list[AstNode] = [self.root]

    @property
    def parent(self) -> AstNode:
        """Easy access to the previous node in the stack."""
        return self.stack[-1]

    def handle_starttag(self, tag: str, attrs: Attrs) -> None:
        this_node = AstNode(tag=tag, attrs=attrs)
        last_node = self.parent
        last_node.children.append(this_node)
        self.stack.append(this_node)

    def handle_data(self, data: str) -> None:
        children = self.parent.children
        children.append(data)

    def handle_endtag(self, tag: str) -> None:
        node = self.stack.pop()
        # if node.tag != tag:
        #     raise SyntaxError("Start tag {node.tag!r} does not match end tag {tag!r}")

    def result(self) -> AstNode:
        """Convenience method to close the feed and return root."""
        self.close()
        match self.root.children:
            case []:
                raise ValueError("Nothing to return")
            case [child]:
                return child
            case _:
                return self.root


def setup() -> AstNode:
    parser = AstParser()
    parser.feed("<div>Hello World</div>")
    root_node = parser.result()
    return root_node


def test() -> TestSetup:
    root_node = setup()
    return ("div", root_node.tag), ("Hello World", root_node.children[0])


def main():
    """Main entry point for this example."""
    root_node = setup()
    assert "div" == root_node.tag
    assert "Hello World" == root_node.children[0]


if __name__ == "__main__":
    main()
