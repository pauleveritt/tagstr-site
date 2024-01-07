"""Setup Sybil and other central testing."""

from sybil import Sybil
from sybil.parsers.myst import (
    DocTestDirectiveParser as MarkdownDocTestParser,
    PythonCodeBlockParser as MarkdownPythonCodeBlockParser,
    SkipParser as MarkdownSkipParser,
)
from sybil.parsers.rest import (
    DocTestParser as ReSTDocTestParser,
    PythonCodeBlockParser as ReSTPythonCodeBlockParser,
)

markdown_examples = Sybil(
    parsers=[
        MarkdownDocTestParser(),
        MarkdownPythonCodeBlockParser(),
        MarkdownSkipParser(),
    ],
    patterns=["*.md"],
)

rest_examples = Sybil(
    parsers=[
        ReSTDocTestParser(),
        ReSTPythonCodeBlockParser(),
    ],
    patterns=["*.rst"],
    exclude="pep.rst"
)

pytest_collect_file = (markdown_examples + rest_examples).pytest()
