"""Stringify an HTML DOM."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape

from tagstr_site.examples import MainResult, Attrs
from tagstr_site.examples.htmlbuilder.hb2 import AstParser
from tagstr_site.examples.htmlbuilder.hb4 import HtmlNode as BaseHtmlNode
from tagstr_site.examples.htmlbuilder.hb6 import Fill as BaseFill
from tagstr_site.htm import HTML
from tagstr_site.tagtyping import Interpolation


@dataclass
class HtmlNode(BaseHtmlNode):
    def __str__(self):
        attrs = []
        for k, v in self.attrs.items():
            match k, v:
                case str(), bool():
                    attrs.append(k)
                case str(), int():
                    attrs.append(f'{k}="{v}"')
                case str(), str():
                    attrs.append(f'{k}="{escape(v, quote=True)}"')
                case 'style', dict() as css:
                    # TODO are there other examples of dict structures
                    # beside the style attr? Could this occur in a
                    # custom tag?
                    decl = []
                    for property, value in css.items():
                        decl.append(f'{property}: {value}')
                    attrs.append(f'{k}="{escape(('; ').join(decl))}"')

        children = []
        for child in self.children:
            match child:
                case str():
                    children.append(escape(child))
                case HTML():
                    children.append(str(child))

        spaced = [f'<{self.tag}']
        if attrs:
            spaced.append(' ')
            spaced.append(' '.join(attrs))

        if children:
            spaced.append('>')
            spaced.append(''.join(children))
            spaced.append(f'</{self.tag}>')
        else:
            spaced.append('/>')

        return ''.join(spaced)


@dataclass
class Fill(BaseFill):
    """A policy that can fill in nodes in an AST, using interpolations."""


    def fill_tag(self, tag: str, attrs: Attrs | None = None, children: list[str | HTML] | None = None) -> HTML:
        """Support interpolation in the tag name for dynamic heading levels and subcomponents."""
        elems = list(self.fill(tag))
        tag = ''.join(elems)
        return HtmlNode(tag, attrs, children)


# TODO Paul maybe this isn't changed and can be imported
def html(*args: str | Interpolation) -> HTML:
    parser = AstParser()
    for arg in args:
        parser.feed(arg)
    return Fill(args).interpolate(parser.result())


def main() -> MainResult:
    """Main entry point for this example."""
    name = "World"
    title = "The Greeting"
    # Manually typing the result since IDE can't process tag functions yet
    root_node: HtmlNode = html'<div title={title}>Hello {name}</div>'
    result = str(root_node)
    expected = '<div title="The Greeting">Hello World</div>'
    assert expected == result

    return expected, result


if __name__ == "__main__":
    print(main())
