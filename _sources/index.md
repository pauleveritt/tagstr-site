# Tag Strings

Welcome to tag strings, a planned enhancement for Python 3.13. Here you will
find examples, specifications, and sample libraries.

## About Tag Strings

This PEP introduces tag strings for custom, repeatable string processing.
Tag strings are an extension to f-strings, with a custom function -- the "tag"
-- in place of the `f` prefix. This function can then provide rich features
such as safety checks, lazy evaluation, DSLs such as web templating, and more.

Tag strings are similar to [JavaScript tagged templates](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals#tagged_templates)
and similar ideas in other languages. See the [work-in-progress PEP](https://github.com/jimbaker/tagstr).
for more detail.

## Example

In this tiny example, a `greet` function is defined and used to "tag" strings:

```python
def greet(*args):
    """Uppercase and add exclamation."""
    salutation = args[0].upper()
    return f"{salutation}!"
```

With a string that obeys f-string semantics, we can then "tag" it:

```{code-block} python
>>> print(greet"Hello")
HELLO!
```

Tag strings are usually much richer and process the arguments Python assembles when calling:

<!--- invisible-code-block: python
from tagstr_site.tagtyping import Decoded, Interpolation
-->

```{code-block} python
def greet(*args: Decoded | Interpolation) -> str:
    """More about the interpolation."""
    result = []
    for arg in args:
        match arg:
            case str():
                result.append(arg)
            case getvalue, raw, conversion, formatspec:
                gv = f"gv: {getvalue()}"
                r = f"r: {raw}"
                c = f"c: {conversion}"
                f = f"f: {formatspec}"
                result.append(", ".join([gv, r, c, f]))

    return f"{''.join(result)}!"
```

```{toctree}
:hidden:
:maxdepth: 1
:caption: Contents

Quick Tutorial <tutorial>
HTML Templating <htmlbuilder>
```
