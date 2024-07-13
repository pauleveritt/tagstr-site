import pytest

from tagstr_site.htm import AstParser, InterpolationConcrete, html, HtmlNode


def test_ast_basic_parsing():
    parser = AstParser()
    parser.feed("<div>Hello World</div>")
    root_node = parser.result()
    assert "div" == root_node.tag
    assert "Hello World" == root_node.children[0]


def test_ast_basic_placeholder():
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


@pytest.mark.skip(reason="Not implemented yet")
def test_basic_component():
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

@pytest.mark.skip(reason="Not implemented yet")
def test_basic_component_double_slash():
    # Simplify this later
    MyComponent = HtmlNode('div', {'class': 'custom'}, ["My component"])

    x = 42
    y = 47
    result = html"""
<html>
  <head><title>Test</title></head>
  <body>
    <h1 class="foo" {x}>Parse {y}</h1>
    <{MyComponent} baz="bar"><p>Extra</p><//>',
  </body>
</html>    
    """

# TODO
# - AST allows <h{level}> (currently complains that placeholder doesn't match)
# - Escape/unescape input for placeholders
# - Subcomponents
# - format_spec etc.
# - Items yield "best practice" from htm.main
# - Attributes
#   * Pass in a dict
#   * Collapse boolean
#   * Nested dict aka style attribute
# - Regex policies e.g. valid tag names
# - Various styles to close calling a component
#   * <Header title="!"></Header>,
#   * <Header title="!" />
#   * <Header title="!"/>
#   * <Header title="!"><//>
# - Any ValueError/TypeError that gets raised, write tests to ensure
# - Class attributes and ordering