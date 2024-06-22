"""Simple HTML parser with interpolation support."""
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Any

from tagstr_site.examples import (
    MainResult,
    PLACEHOLDER,
    interleave_with_values,
    Attrs,
)


@dataclass
class HtmlNode:
    """A single HTML document object model node"""

    tag: str | None = None
    children: list[str, "HtmlNode"] = field(default_factory=list)


class HtmlBuilder(HTMLParser):
    def __init__(self):
        super().__init__()
        self.root = HtmlNode()
        self.stack = [self.root]
        self.values = []

    def feed(self, data: Any) -> None:
        match data:
            case str():
                # Leaving out the escaping of possible $$ in data
                super().feed(data)
            case getvalue, _, conv, spec:
                value = getvalue()
                self.values.append(value)
                super().feed(PLACEHOLDER)

    def result(self) -> HtmlNode:
        """Convenience method to close the feed and return root."""
        self.close()
        # Don't worry about other cases for now
        return self.root.children[0]

    @property
    def parent(self):
        """Easy access to the previous node in the stack."""
        return self.stack[-1]

    def handle_starttag(self, tag: str, attrs: Attrs) -> None:
        this_node = HtmlNode(tag)
        self.parent.children.append(this_node)
        self.stack.append(this_node)

    def handle_endtag(self, tag: str) -> None:
        node = self.stack.pop()
        if node.tag != tag:
            raise SyntaxError("Start tag {node.tag!r} does not match end tag {tag!r}")

    def handle_data(self, data: str) -> None:
        """Replace the placeholders with the interpolation values."""
        interleaved_children = interleave_with_values(data, self.values)

        for child in interleaved_children:
            match child:
                case str():
                    self.parent.children.append(child)
                case list():
                    self.parent.children.extend(child)


def main() -> MainResult:
    """Main entry point for this example."""
    name = "World"
    builder = HtmlBuilder()
    builder.feed("<div>Hello ")
    tag_args = (lambda: name, "name", None, None)
    builder.feed(tag_args)
    builder.feed("</div>")
    root_node = builder.result()

    return ("div", root_node.tag), (root_node.children, ["Hello ", "World"])


if __name__ == "__main__":
    print(main())
