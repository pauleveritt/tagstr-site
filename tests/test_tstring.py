from typing import Interpolation, Decoded
from tagstr_site.tstring import t, Template


def test_empty():
    template = t""
    assert isinstance(template, Template)
    assert len(template.source) == 1
    assert len(template.raw) == 1
    assert len(template.values) == 0
    assert len(template.exprs) == 0
    assert len(template.convs) == 0
    assert len(template.format_specs) == 0
    assert len(template.args) == 1
    assert template.source == ("",)
    assert template.raw == ("",)
    assert template.args[0] == ""

def test_simple():
    template = t"hello"
    assert isinstance(template, Template)
    assert len(template.source) == 1
    assert len(template.raw) == 1
    assert len(template.values) == 0
    assert len(template.exprs) == 0
    assert len(template.convs) == 0
    assert len(template.format_specs) == 0
    assert len(template.args) == 1
    assert template.source == ("hello",)
    assert template.raw == ("hello",)
    assert template.args[0] == "hello"

def test_only_interpolation():
    template = t"{42}"
    assert isinstance(template, Template)
    assert len(template.source) == 2
    assert len(template.raw) == 2
    assert len(template.values) == 1
    assert len(template.exprs) == 1
    assert len(template.convs) == 1
    assert len(template.format_specs) == 1
    assert len(template.args) == 3
    assert template.source == ("", "")
    assert template.raw == ("", "")
    assert template.values == (42,)
    assert template.exprs == ("42",)
    assert template.convs == (None,)
    assert template.format_specs == (None,)
    assert isinstance(template.args[0], Decoded)
    assert template.args[0] == ""
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == 42
    assert isinstance(template.args[2], Decoded)
    assert template.args[2] == ""

def test_mixed():
    v = 99
    template = t"hello{42}world{v}goodbye"
    assert isinstance(template, Template)
    assert len(template.source) == 3
    assert len(template.raw) == 3
    assert len(template.values) == 2
    assert len(template.exprs) == 2
    assert len(template.convs) == 2
    assert len(template.format_specs) == 2
    assert len(template.args) == 5
    assert template.source == ("hello", "world", "goodbye")
    assert template.raw == ("hello", "world", "goodbye")
    assert template.values == (42, v)
    assert template.exprs == ("42", "v")
    assert template.convs == (None, None)
    assert template.format_specs == (None, None)
    assert isinstance(template.args[0], Decoded)
    assert template.args[0] == "hello"
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == 42
    assert isinstance(template.args[2], Decoded)
    assert template.args[2] == "world"
    assert isinstance(template.args[3], Interpolation)
    assert template.args[3].value == v
    assert isinstance(template.args[4], Decoded)
    assert template.args[4] == "goodbye"
