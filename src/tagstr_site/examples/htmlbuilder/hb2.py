"""Parse into an AST with interpolation placeholders.

Doesn't yet support actual filling in data of interpolations.
"""

from tagstr_site.examples.htmlbuilder.hb1 import AstParser as BaseParser
from tagstr_site.builtins import InterpolationConcrete
from tagstr_site.examples import MainResult
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

def main() -> MainResult:
    """Main entry point for this example."""
    name = "World"
    parser = AstParser()
    parser.feed("<div>Hello ")
    interpolation = InterpolationConcrete(lambda: name, 'name', None, None)
    parser.feed(interpolation)
    parser.feed("</div>")
    root_node = parser.result()

    assert "div" == root_node.tag
    assert ["Hello ", 'x$1x'] == root_node.children

    return ("div", root_node.tag), (root_node.children, ["Hello ", "x$1x"])


if __name__ == "__main__":
    print(main())
