from tagstr_site.htm import html


def test_simple_looping():
    message = "Hello"
    names = ["World", "Universe"]
    result = str(
        html(
            """
            <ul title="{message}">
                {[
                    html('<li>{name}</li>')
                    for name in names
                ]}
            </ul>
            """
        )
    )
    expected = "<ul title='Hello'><li>World</li><li>Universe</li></ul>"
    assert expected == result


def test_rendered_looping():
    message = "Hello"
    names = ["World", "Universe"]
    items = [html("<li>{label}</li>") for label in names]
    result = str(
        html(
            """
            <ul title="{message}">
              {items}
            </ul>
            """
        )
    )
    expected = "<ul title='Hello'><li>World</li><li>Universe</li></ul>"
    assert expected == result

