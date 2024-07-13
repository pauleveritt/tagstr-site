from tagstr_site.htm import html
from conftest import name  # noqa F401

def test_insert_value():
    name = "viewdom"  # noqa F401
    result = str(html("<div>Hello {name}</div>"))
    assert "<div>Hello viewdom</div>" == result

def test_value_from_import():
    def Hello():
        return html("<div>Hello {name}</div>")

    result = str(Hello())
    assert "<div>Hello World</div>" == result


def test_passed_in_prop():
    def Hello(name):
        return html("<div>Hello {name}</div>")

    result = str(Hello(name="viewdom"))
    assert "<div>Hello viewdom</div>" == result

