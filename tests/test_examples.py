import pytest

from tagstr_site.examples.htmlbuilder.hb1 import main as hb1
from tagstr_site.examples.htmlbuilder.hb2 import main as hb2
from tagstr_site.examples.htmlbuilder.hb3 import main as hb3
from tagstr_site.examples.htmlbuilder.hb4 import main as hb4
from tagstr_site.examples.htmlbuilder.hb5 import main as hb5
from tagstr_site.examples.htmlbuilder.hb6 import main as hb6


@pytest.mark.parametrize("example", (hb1, hb2, hb3, hb4, hb5, hb6))
def test_examples(example):
    results = example()
    if isinstance(results[0], str):
        # Put example in tuple
        results = (results,)
    for expected, actual in results:
        assert expected == actual
