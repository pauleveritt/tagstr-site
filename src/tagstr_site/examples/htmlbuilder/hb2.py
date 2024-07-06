"""Parse into an AST with interpolation placeholders.

Doesn't yet support actual filling in data of interpolations.
"""

from tagstr_site.examples.htmlbuilder.hb1 import AstNode, AstParser as BaseParser
from tagstr_site.builtins import InterpolationConcrete
from tagstr_site.examples import TestSetup
from tagstr_site.tagtyping import Interpolation


class AstParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.index = 0

    def feed(self, arg: str | Interpolation) -> None:
        # We don't need Decoded as this method never uses raw
        match arg:
            case str() as s:
                # Leaving out the escaping of possible $$ in data
                super().feed(s)
            # case Interpolation():
            case tuple():  # Temporary, while waiting for 3.14 implementation
                # TODO Jim we don't have a default case for no match
                super().feed(f"x${self.index}x")
            case _:
                raise ValueError("Arg not shaped like a string nor Interpolation")
        self.index += 1


def setup() -> AstNode:
    name = "World"
    parser = AstParser()
    parser.feed("<div>Hello ")
    interpolation = InterpolationConcrete(lambda: name, "name", None, None)
    parser.feed(interpolation)
    parser.feed("</div>")
    # Manually typing the result since IDE can't process tag functions yet
    root_node: AstNode = parser.result()
    return root_node


def test() -> TestSetup:
    root_node = setup()

    return ("div", root_node.tag), (root_node.children, ["Hello ", "x$1x"])


def main():
    """Main entry point for this example."""
    root_node = setup()
    assert "div" == root_node.tag
    assert ["Hello ", "x$1x"] == root_node.children


if __name__ == "__main__":
    main()
