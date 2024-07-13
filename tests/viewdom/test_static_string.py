from markupsafe import Markup

from tagstr_site.htm import html, HtmlNode


def test_simple_render():
    result = str(html("<div>Hello World</div>"))
    assert "<div>Hello World</div>" == result

def test_show_vdom():
    result = html('<div class="container">Hello World</div>')
    assert HtmlNode(
        tag="div",
        attrs={"class": "container"},
        children=["Hello World"]
    ) == result


def test_expressions_as_values():
    vdom = html('<div class="container{1}">Hello World</div>')
    result = str(vdom)
    assert '<div class="container1">Hello World</div>' == result

def test_child_nodes():
    vdom = html("<div>Hello <span>World<em>!</em></span></div>")
    expected = HtmlNode(tag="div",
        children=[
            "Hello ",
            HtmlNode(
                tag="span",
                children=["World", HtmlNode(tag="em", attrs={}, children=["!"])],
            ),
        ],)
    assert expected == vdom

def test_doctype():
    doctype = Markup("<!DOCTYPE html>\n")
    vdom = html("{doctype}<div>Hello World</div>")
    result = str(vdom)
    assert "<!DOCTYPE html>\n<div>Hello World</div>" == result

def test_boolean_attribute_value():
    vdom = html("<div editable={True}>Hello World</div>")
    result = str(vdom)
    assert "<div editable>Hello World</div>" == result
