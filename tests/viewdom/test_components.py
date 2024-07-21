import pytest
from tagstr_site.htm import html

pytest.skip(reason="Not yet implemented", allow_module_level=True)

def test_simple_heading():
    def Heading():
        return html("<h1>My Title</h1>")
    vdom = html("<{Heading} />")
    assert "Heading" == vdom.tag
    result = str(vdom)
    assert "<h1>My Title</h1>" == result


def test_simple_props():
    def Heading(title):
        return html("<h1>{title}</h1>")
    result = str(html('<{Heading} title="My Title" />'))
    assert "<h1>My Title</h1>" == result

def test_children_props():
    def Heading(children, title):
        return html("<h1>{title}</h1><div>{children}</div>")
    result = str(html('<{Heading} title="My Title">Child<//>'))
    assert "<h1>My Title</h1><div>Child</div>" == result

def test_expression_props():
    def Heading(title):
        return html("<h1>{title}</h1>")
    result = str(html('<{Heading} title={"My Title"} />'))
    assert "<h1>My Title</h1>" == result


def test_scope_value():
    def Heading(title):
        """The default heading."""
        return html("<h1>{title}</h1>")

    this_title = "My Title"
    result = str(html("<{Heading} title={this_title} />"))

    assert "<h1>My Title</h1>" == result


def test_optional_props():
    def Heading(title="My Title"):
        return html("<h1>{title}</h1>")

    result = str(html("<{Heading} />"))
    assert "<h1>My Title</h1>" == result

def test_spread_props():
    def Heading(title, this_id):
        return html("<div title={title} id={this_id}>Hello</div>")

    props = dict(title="My Title", this_id="d1")
    result = str(html("<{Heading} ...{props}>Child<//>"))
    assert '<div title="My Title" id="d1">Hello</div>' == result


def test_pass_component():
    def DefaultHeading():
        return html("<h1>Default Heading</h1>")

    def Body(heading):
        return html("<body><{heading} /></body>")

    result = str(html("<{Body} heading={DefaultHeading} />"))
    assert "<body><h1>Default Heading</h1></body>" == result

def test_default_component():
    def DefaultHeading():  # pragma: nocover
        return html("<h1>Default Heading</h1>")

    def OtherHeading():
        return html("<h1>Other Heading</h1>")

    def Body(heading=DefaultHeading):
        return html("<body><{heading} /></body>")

    result = str(html("<{Body} heading={OtherHeading}/>"))
    assert "<body><h1>Other Heading</h1></body>" == result


def test_conditional_default():
    def DefaultHeading():
        return html("<h1>Default Heading</h1>")

    def OtherHeading():
        return html("<h1>Other Heading</h1>")

    def Body(heading=None):
        return html("<body>{heading if heading else DefaultHeading}</body>")

    result = str(html("<{Body} heading={OtherHeading}/>"))
    assert "<body><h1>Other Heading</h1></body>" == result


def children_props():
    def Heading(children, title):
        return html("<h1>{title}</h1><div>{children}</div>")

    result = str(html('<{Heading} title="My Title">Child<//>'))
    assert "<h1>My Title</h1><div>Child</div>" == result


def test_generators():
    def Todos():
        for todo in ["First", "Second"]:  # noqa B007
            yield html("<li>{todo}</li>")

    result = str(html("<ul><{Todos}/></ul>"))
    assert "<ul><li>First</li><li>Second</li></ul>" == result


def test_subcomponents():
    title = "My Todos"

    def Todo(label):
        return html("<li>{label}</li>")

    def TodoList(todos):
        return html("<ul>{[Todo(label) for label in todos]}</ul>")

    todos = ["first"]
    result = str(
        html(
            """
      <h1>{title}</h1>
      <{TodoList} todos={todos} />
    """
        )
    )
    assert "<h1>My Todos</h1><ul><li>first</li></ul>" == result


