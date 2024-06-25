"""Simple HTML parser with interpolation support."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Generator

from tagstr_site.examples import (
    MainResult,
    Attrs,
)
from tagstr_site.tagtyping import Decoded, Interpolation


@dataclass
class HtmlNode:
    """A single HTML document object model node."""

    tag: str | None
    attrs: dict[str, object] = field(default_factory=dict)
    children: list[str | HtmlNode] = field(default_factory=list)


class HtmlBuilder(HTMLParser):
    def __init__(self):
        super().__init__()
        self.root = HtmlNode(tag=None)
        self.stack = [self.root]
        self.index = 0

    def feed(self, data: Decoded | Interpolation) -> None:
        match data:
            case Decoded() as decoded:
                # Leaving out the escaping of possible $$ in data
                super().feed(decoded)
            case Interpolation():
                super().feed(f'x${self.index}x')
        self.index += 1

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
        self.parent.children.append(data)

    def result(self) -> HtmlNode:
        """Convenience method to close the feed and return root."""
        self.close()
        # Don't worry about other cases for now
        return self.root.children[0]




placeholder_re = re.compile(r'(x\$\d+x)')
placeholder_index_re = re.compile(r'x\$(?P<index>\d+)x')


def split_by_placeholder(s: str, args: list[Decoded | Interpolation]) -> Generator[str | Interpolation]:
    """During interpolation, find placeholders and split on correct boundaries."""
    for split in placeholder_re.split(s):
        # Empty strings can be dropped
        if split != '':
            if m := placeholder_index_re.match(split):
                # Get the index and then grab the interpolation from args at that position
                index = int(m.group('index'))
                yield args[index]
            else:
                # Later we will ensure this string is unescaped (in case the original string
                # had a placeholder.)
                yield split


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
