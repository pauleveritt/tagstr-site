# HTML Templating

Outline
- Event callbacks

## A basic HTML parser

- In this tutorial, we're leaving out a lot of detail in the first pass
  - Such as: attributes
- Extend :class:`~html.parser.HTMLParser`
- It gets fed a string of HTML
- Calls handler methods at certain events: start tag, end tag, etc.
- Let's write a parser that makes a "JSON" representation
  - handle_starttag, handle_data, handle_endtag
- Nothing nested

## Interpolations

- Needs to accept a tuple of strings and callables
- The callables need to be something you can "interpolate" later
- The `feed` method stores a placeholder for the interpolation
- Later, in the handler methods, put the actual value in for the placeholder
- One-line utility functions to escape/unescape placeholders

## Attributes

## Nested

- Using a stack
- Add a context manager to easily close the root
- Make an `__str__()` and `__to_json__()` to omit the root
