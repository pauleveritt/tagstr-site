from typing import Interpolation
from tagstr_site.tstring import t, Template


def test_empty():
    template = t""
    assert isinstance(template, Template)
    assert len(template.args) == 1
    assert template.args[0] == ""
    assert template.source == ("",)

def test_simple():
    template = t"hello"
    assert isinstance(template, Template)
    assert len(template.args) == 1
    assert template.args[0] == "hello"
    assert template.source == ("hello",)

def test_only_interpolation():
    template = t"{42}"
    assert isinstance(template, Template)
    assert len(template.args) == 3
    assert template.args[0] == ""
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == 42
    assert template.args[2] == ""
    assert template.source == ("", "")

def test_mixed():
    v = 99
    template = t"hello{42}world{v}goodbye"
    assert isinstance(template, Template)
    assert len(template.args) == 5
    assert template.args[0] == "hello"
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == 42
    assert template.args[2] == "world"
    assert isinstance(template.args[3], Interpolation)
    assert template.args[3].value == v
    assert template.args[4] == "goodbye"
    assert template.source == ("hello", "world", "goodbye")
