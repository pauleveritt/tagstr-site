"""Test the fl example."""

from tagstr_site.fl.fl1 import demo as demo1
from tagstr_site.fl.fl2 import demo as demo2
from tagstr_site.fl.fl3 import demo as demo3

# TODO Parametrize these into a single test function
def test_demo1():
    results = demo1()
    assert results == '0: Hello\n1: Hello\n2: Hello'


def test_demo2():
    results = demo2()
    assert results == '0: Hello\n1: Hello\n2: Hello'


def test_demo3():
    results = demo3()
    assert results == '2: Hello\n2: Hello\n2: Hello'
