"""Parse into an AST with interpolation support."""

from hb1 import HtmlBuilder as BaseBuilder
from tagstr_site.builtins import InterpolationConcrete
from tagstr_site.examples import MainResult
from tagstr_site.tagtyping import Interpolation


class HtmlBuilder(BaseBuilder):
    def __init__(self):
        super().__init__()
        self.index = 0

    def feed(self, arg: str | Interpolation) -> None:
        # We don't need Decoded as this method never uses raw
        match arg:
            case str() as s:
                # Leaving out the escaping of possible $$ in data
                super().feed(s)
            case Interpolation():
                # TODO Jim is it ok to omit "as t"
                # TODO Jim we don't have a default case for no match
                super().feed(f"x${self.index}x")
        self.index += 1

def main() -> MainResult:
    """Main entry point for this example."""
    name = "World"
    builder = HtmlBuilder()
    builder.feed("<div>Hello ")
    interpolation = InterpolationConcrete(lambda: name, 'name', None, None)
    builder.feed(interpolation)
    builder.feed("</div>")
    root_node = builder.result()

    assert "div" == root_node.tag
    assert ["Hello ", 'x$1x'] == root_node.children

    return ("div", root_node.tag), (root_node.children, ["Hello ", "x$1x"])


if __name__ == "__main__":
    print(main())
