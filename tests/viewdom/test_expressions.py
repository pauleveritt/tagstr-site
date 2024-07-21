import pytest

from tagstr_site.htm import html

pytest.skip(reason="Not yet implemented", allow_module_level=True)

def test_python_operation():
    name = "viewdom"
    result = str(html("<div>Hello {name.upper()}</div>"))
    assert "<div>Hello VIEWDOM</div>" == result


def test_simple_arithmetic():
    name = "viewdom"
    result = str(html("<div>Hello {1 + 3}</div>"))
    assert "<div>Hello 4</div>" == result

def test_call_function():
    def make_bigly(name: str) -> str:
        """A function returning a string, rather than a component."""
        return f"BIGLY: {name.upper()}"

    name = "viewdom"
    result = str(html("<div>Hello {make_bigly(name)}</div>"))
    assert "<div>Hello BIGLY: VIEWDOM</div>" == result
