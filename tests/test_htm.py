from tagstr_site.htm import AstParser, InterpolationConcrete, html


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
    name = "World"
    level = 1
    title = "The Greeting"
    root_node = html'<h{level} title={title}>Hello {name}</h{level}>'
    assert "h1" == root_node.tag
    assert dict(title="The Greeting") == root_node.attrs
    assert ["Hello ", "World"] == root_node.children


def test_basic_stringifying():
    name = "World"
    title = "The Greeting"
    root_node = html'<div title={title}>Hello {name}</div>'
    result = str(root_node)
    assert '<div title="The Greeting">Hello World</div>' == result

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
