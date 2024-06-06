from dataclasses import dataclass, field
from typing import Any

# A helper for example writing
MainResult = str | tuple[tuple[str, str | None], tuple[str, Any]]

PLACEHOLDER = "x$x"

Attrs = list[tuple[str, str | None]]


@dataclass
class HtmlNode:
    """A single HTML document object model node"""

    tag: str | None = None
    children: list[str, "HtmlNode"] = field(default_factory=list)


def escape_placeholder(string: str) -> str:
    return string.replace("$", "$$")


def unescape_placeholder(string: str) -> str:
    return string.replace("$$", "$")


def join_with_values(string: str, values: list[Any]) -> tuple[str, list[Any]]:
    interleaved_values, remaining_values = interleave_with_values(string, values)
    match interleaved_values:
        case [value]:
            return value, remaining_values
        case values:
            return "".join(map(str, values)), remaining_values


def interleave_with_values(
    string: str, values: list[Any]
) -> tuple[list[Any], list[Any]]:
    if string == PLACEHOLDER:
        return values[:1], values[1:]

    *string_parts, last_string_part = string.split(PLACEHOLDER)
    remaining_values = values[len(string_parts) :]

    interleaved_values = [
        item
        for s, v in zip(string_parts, values)
        for item in (unescape_placeholder(s), v)
    ]
    interleaved_values.append(last_string_part)

    return interleaved_values #, remaining_values
