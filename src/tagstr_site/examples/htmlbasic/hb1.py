"""Basic HTML parser."""

from html.parser import HTMLParser

from tagstr_site.examples import HtmlNode, MainResult, Attrs


class HtmlBuilder(HTMLParser):
    def __init__(self):
        super().__init__()
        self.root = HtmlNode()
        self.stack = [self.root]

    @property
    def parent(self):
        """Easy access to the previous node in the stack."""
        return self.stack[-1]

    def handle_starttag(self, tag: str, attrs: Attrs) -> None:
        this_node = HtmlNode(tag)
        self.parent.children.append(this_node)
        self.stack.append(this_node)

    def handle_data(self, data: str) -> None:
        self.parent.children.append(data)

    def handle_endtag(self, tag: str) -> None:
        node = self.stack.pop()
        if node.tag != tag:
            raise SyntaxError("Start tag {node.tag!r} does not match end tag {tag!r}")

    def result(self) -> HtmlNode:
        """Convenience method to close the feed and return root."""
        self.close()
        # Don't worry about other cases for now
        return self.root.children[0]


def main() -> MainResult:
    """Main entry point for this example."""
    builder = HtmlBuilder()
    builder.feed("<div>Hello World</div>")
    root_node = builder.result()
    return ("div", root_node.tag), ("Hello World", root_node.children[0])


if __name__ == "__main__":
    print(main())
