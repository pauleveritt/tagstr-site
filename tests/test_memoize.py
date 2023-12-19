"""Test the memoize example."""
from inspect import getclosurevars
from tagstr_site.memoize.memoize1 import demo1
from tagstr_site.memoize.memoize2 import demo2


# def test_make_memoization_key_static():
#     these_args = ("Hello", "World")
#     result = memoization_key(*these_args)
#     assert result == these_args
#
#
# def test_make_memoization_key_with_thunk():
#     thunk = Thunk(lambda x: x, "", None, None)
#     these_args = ("Hello", thunk, "World")
#     result = memoization_key(*these_args)
#     assert result == ("Hello", "World")
#
# def test_greeting():
#     name = "World"
#     result = greet"Hello {name:s} nice to meet you"
#     assert "Hello World nice to meet you!" == result

# # def test_demo():
# #     result = main()
# #     assert result["children"][0]["attributes"]["yo"] == 1
# #
# # def test_greet1():
# #     name = "World"
# #     result = greet1"Hello {name:s} nice to meet you"
# #     assert "Hello World nice to meet you!" == result
# #
# # def test_make_memoization_key_static():
# #     these_args = ("Hello", "World")
# #     result = memoization_key(*these_args)
# #     assert result == these_args
# #
# #
# # def test_make_memoization_key_with_thunk():
# #     thunk = Thunk(lambda: 9, "", None, None)
# #     these_args = ("Hello", thunk, "World")
# #     result = memoization_key(*these_args)
# #     assert result == ("Hello", "World")
#
#
# def test_greet2():
#     name = "World"
#     result = greet2"Hello {name:s} nice to meet you"
#     assert "Hello World nice to meet you!" == result


def test_demo1():
    results = demo1()
    assert results[0] == "Hello World"
    assert results[1] == "Salut World"
    fl_tag = results[2]
    closure_vars = getclosurevars(fl_tag)
    count = closure_vars.nonlocals["count"]
    assert count == 2


def test_demo2():
    results = demo2()
    assert results[0] == "Hello World"
    assert results[1] == "Salut World"
    fl_tag = results[2]
    closure_vars = getclosurevars(fl_tag)
    cache_hit = closure_vars.nonlocals["cache_hit"]
    template_cache = closure_vars.nonlocals["template_cache"]
    assert cache_hit == 0
    cache_keys = list(template_cache.keys())
    assert len(cache_keys) == 2
    assert cache_keys[0][0] == "Hello "
    assert cache_keys[1][0] == "Salut "
