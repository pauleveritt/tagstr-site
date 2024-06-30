"""Add an HTML tag function to call the builder."""

from tagstr_site.examples.htmlbuilder.hb1 import ASTParser as BaseBuilder
from tagstr_site.examples import MainResult
from tagstr_site.htm import HTML


def html(*args) -> HTML:
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
