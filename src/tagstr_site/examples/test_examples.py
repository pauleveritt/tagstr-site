import pytest

from .htmlbasic.hb1 import main as hb1
from .htmlbasic.hb2 import main as hb2
from .htmlbasic.hb3 import main as hb3


@pytest.mark.parametrize("example", (hb1, hb2, hb3))
def test_examples(example):
    results = example()
    if isinstance(results[0], str):
        # Put example in tuple
        results = (results,)
    for expected, actual in results:
        assert expected == actual
