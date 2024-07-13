import pytest

from tagstr_site.htm import html

pytest.skip(reason="Not yet implemented", allow_module_level=True)


def test_syntax():
    message = "Say Howdy"
    not_message = "So Sad"
    show_message = True
    result = str(
        html(
            """
        <h1>Show?</h1>
        {message if show_message else not_message}
    """
        )
    )

    assert "<h1>Show?</h1>Say Howdy" == result

