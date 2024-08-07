import pytest

from tagstr_site.htm import AstParser, InterpolationConcrete, html, HtmlNode, AstNode


def test_ast_root_string():
    parser = AstParser()
    parser.feed("Hello World")
    root_node = parser.result()
    # TODO Should this be an AstNode?
    assert root_node == "Hello World"


def test_ast_root_node():
    parser = AstParser()
    parser.feed("<div>Hello World</div>")
    root_node = parser.result()
    assert root_node == AstNode(
        tag="div",
        children=["Hello World"]
    )

def test_ast_attributes():
    parser = AstParser()
    parser.feed('<div title="Greeting">Hello World</div>')
    root_node = parser.result()
    assert root_node == AstNode(
        tag="div",
        attrs=[("title", "Greeting")],
        children=["Hello World"]
    )


def test_ast_placeholder():
    name = "World"
    parser = AstParser()
    parser.feed("<div>Hello ")
    interpolation = InterpolationConcrete(lambda: name, "name", None, None)
    parser.feed(interpolation)
    parser.feed("</div>")
    root_node = parser.result()
    assert root_node == AstNode(
        tag="div",
        children=["Hello ", "x$1x"]
    )

def test_ast_subcomponent():
    def MyComponent():
        return html"<span>Hello</span>"

    parser = AstParser()
    parser.feed('<div><')
    parser.feed(InterpolationConcrete(lambda: MyComponent, "MyComponent", None, None))
    parser.feed('></')
    parser.feed(InterpolationConcrete(lambda: MyComponent, "MyComponent", None, None))
    parser.feed('></div>')
    root_node = parser.result()
    children = root_node.children
    assert "x$1x" == children[0].tag
    assert root_node == AstNode(
        tag="div",
        children=[AstNode(tag="x$1x")]
    )


def test_ast_attributes_placeholder():
    name = "World"
    parser = AstParser()
    parser.feed("<div>Hello ")
    interpolation = InterpolationConcrete(lambda: name, "name", None, None)
    parser.feed(interpolation)
    parser.feed("</div>")
    # Manually typing the result since IDE can't process tag functions yet
    root_node = parser.result()
    assert "div" == root_node.tag
    assert ["Hello ", "x$1x"] == root_node.children


def test_basic_tag_usage():
    name = "World"
    root_node = html"<div>Hello {name}</div>"
    assert "div" == root_node.tag
    assert ["Hello ", "World"] == root_node.children


def test_basic_attributes():
    title = "The Greeting"
    root_node = html'<h1 title={title}>Hello World</h1>'
    assert dict(title="The Greeting") == root_node.attrs
    assert ["Hello World"] == root_node.children


def test_basic_stringifying():
    name = "World"
    title = "The Greeting"
    root_node = html'<div title={title}>Hello {name}</div>'
    result = str(root_node)
    assert '<div title="The Greeting">Hello World</div>' == result


def test_closing_tag_double_slash():
    root_node = html"<div>123<//>"
    assert "div" == root_node.tag


def test_interpolate_tag_name():
    level = 1
    root_node = html'<h{level}>Hello</h{level}>'
    assert "h1" == root_node.tag


def test_interpolate_tag_name_not_matching():
    level = 1
    wrong_level = 2
    with pytest.raises(RuntimeError) as exc:
        root_node = html'<h{level}>Hello</h{wrong_level}>'
    assert "Unexpected </h{wrong_level}>" == str(exc.value)


def test_end_tag_must_match_start_tag():
    root_node = html'<h1>Hello</h1>'
    assert "h1" == root_node.tag


def test_end_tag_does_not_match_start_tag():
    with pytest.raises(RuntimeError) as e:
        html"<h1>Hello</h2>"
    assert "Unexpected </h2>" in str(e.value)

def test_genexp_in_interpolation():
    items = (html'<li>Item #{i}</li>' for i in range(5))
    listing = html'<ol>{items}</ol>'
    expected = '<ol><li>Item #0</li><li>Item #1</li><li>Item #2</li><li>Item #3</li><li>Item #4</li></ol>'
    assert expected == str(listing)

def test_basic_component_ast_parse():
    def MyComponent():
        return
    parser = AstParser()
    parser.feed("<div>Hello ")
    interpolation = InterpolationConcrete(lambda: MyComponent, "MyComponent", None, None)
    parser.feed(interpolation)
    parser.feed("</div>")
    # Manually typing the result since IDE can't process tag functions yet
    root_node = parser.result()
    assert "div" == root_node.tag
    assert ["Hello ", "x$1x"] == root_node.children


def test_basic_component_as_tag_string():
    def MyComponent():
        return html"<span>Hello</span>"

    result = html"<div><{MyComponent}></{MyComponent}></div>"
    assert "<div><span>Hello</span></div>" == str(result)


@pytest.mark.skip(reason="Not implemented yet")
def test_full_component():
    MyComponent = HtmlNode('div', {'class': 'custom'}, ["My component"])

    x = 42
    y = 47
    result = html"""
<html>
  <head><title>Test</title></head>
  <body>
    <h1 class="foo" {x}>Parse {y}</h1>
    <{MyComponent} baz="bar"><p>Extra</p></{MyComponent}>',
  </body>
</html>    
    """


def test_basic_component_double_slash():
    # Simplify this later
    MyComponent = HtmlNode('div', {'class': 'custom'}, ["My component"])

    x = 42
    y = 47
    result = html"""<html>
  <head><title>Test</title></head>
  <body>
    <h1 class="foo" {x}>Parse {y}</h1>
    <{MyComponent} baz="bar"><p>Extra</p></{MyComponent}>',
  </body>
</html>    
    """

# TODO
# - Clean up the (fake) builtins and typing modules on this side
# - Subcomponents
# - Attributes
#   * Pass in a dict
#   * Collapse boolean
#   * Nested dict aka style attribute
# - Various styles to close calling a component
#   * <Header title="!"></Header>,
#   * <Header title="!" />
#   * <Header title="!"/>
#   * <Header title="!"><//>
# - Escape/unescape input for placeholders
# - Items yield "best practice" from htm.main
# - Class attributes and ordering
# - Regex policies e.g. valid tag names
# - format_spec etc.
# - Any ValueError/TypeError that gets raised, write tests to ensure
