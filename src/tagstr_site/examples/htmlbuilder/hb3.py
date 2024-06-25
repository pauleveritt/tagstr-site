"""Add an HTML tag function to call the builder."""

from tagstr_site.examples import HtmlNode, MainResult
from tagstr_site.examples.htmlbasic.hb2 import HtmlBuilder


def html(*args) -> HtmlNode:
    builder = HtmlBuilder()
    for arg in args:
        builder.feed(arg)
    return builder.result()


def main() -> MainResult:
    """Main entry point for this example."""
    name = "World"
    result: HtmlNode = html"<div>Hello {name}</div>"
    return ("div", result.tag), ()
    assert result.tag == "div"
    assert result.children == ["Hello ", "World"]


if __name__ == "__main__":
    print(main())
