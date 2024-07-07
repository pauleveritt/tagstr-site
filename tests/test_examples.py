import pytest

from tagstr_site.examples.htmlbuilder.hb1 import test as hb1
from tagstr_site.examples.htmlbuilder.hb2 import test as hb2
from tagstr_site.examples.htmlbuilder.hb3 import test as hb3
from tagstr_site.examples.htmlbuilder.hb4 import test as hb4
from tagstr_site.examples.htmlbuilder.hb5 import test as hb5
from tagstr_site.examples.htmlbuilder.hb6 import test as hb6
from tagstr_site.examples.htmlbuilder.hb7 import test as hb7


@pytest.mark.parametrize("example", (hb1, hb2, hb3, hb4, hb5, hb6, hb7))
def test_examples(example):
    results = example()
    if isinstance(results[0], str):
        # Put example in tuple
        results = (results,)
    for expected, actual in results:
        assert expected == actual
