# Tutorial

Imagine: A fictional company has a standard way to do greetings. For this, it
created a tag function to properly format greetings according to its standards.

## Simple Tag Function

We start with a tag function `greet` that's used as a prefix:

```python
def greet(*args):
    """Uppercase and add exclamation."""
    salutation = args[0].upper()
    return f"{salutation}!"
```

If it looks like the `f-` in f-strings -- correct! You can then use this tag
function as a "tag" on a string:

```{code-block} python
>>> print(greet"Hello")
HELLO!
```

In the `greet` function -- a _tag_ function -- we see the first step into
tag strings. You're given an `*args` sequence for all the parts in the
string being tagged. We see how this PEP tokenizes/processes the string
being tagged, into datastructures to be easily handled.

We then see a usage -- a tagged string in `main` with `greet"Hello"`. This
"tags" the `Hello` string with the function `greet`.

## Interpolation

That example showed the basics but had no dynamicism in it. f-strings make
it easy to insert variables and expressions with extra instructions. We
call these _interpolations_. Let's see a super-simple example:

```python
def greet(*args):
    """Handle an interpolation."""
    salutation = args[0].strip()
    # Second arg is an "interpolation" tuple.
    getvalue = args[1][0]
    recipient = getvalue().upper()
    return f"{salutation} {recipient}!"
```

The second argument is the `{name}` part, represented as a tuple. The
tuple's first argument is a callable that evaluates _in the scope_ where the
tag string happened. Calling it yields the value, thus by convention we call
this `getvalue`.

This time, we'll tag a string that inserts a variable:

```{code-block} python
>>> name = "World"
>>> print(greet"Hello {name}")
Hello WORLD!
```

## Flexible Args

Our greeting now expects a string followed by a single interpolation. But
f-strings can have all kinds of things mixed in, even nested f-strings.
Let's teach our greeting to handle an arbitrary list of strings and
interpolations.

In fact, let's start adopting the jargon used in this proposal:

- _Decodeds_ are segments that are static strings
- _Interpolations_ are the structure representing an interpolation
- The _args_ are thus an arbitrary sequence of decodeds and interpolations, intermixed

Here's the code to generalize args:

```{code-block} python
def greet(*args):
    """Handle arbitrary length of args."""
    result = []
    for arg in args:
        match arg:
            case str():  # Will need a string-like test
                result.append(arg)
            case getvalue, _, _, _:  # This is an interpolation
                result.append(getvalue().upper())

    return f"{''.join(result)}!"
```

It uses Python 3.10 structural pattern matching to analyze each segment and
determine "decodeds" and "interpolations".

```{code-block} python
>>> print(greet"Hello {name} nice to meet you")  # name is still World
Hello WORLD nice to meet you!
```

## Interpolations

We just said interpolations were represented by a data structure. Let's look at them
more carefully and see what they have to offer, while adding some typing.

An interpolation is a tuple with this shape:

```{literalinclude} ../src/tagstr_site/tagtyping.py
:start-at: class Interpolation
:end-at: format_spec
```

<!--- invisible-code-block: python
from tagstr_site.tagtyping import Decoded, Interpolation
-->

It will likely be defined in the `typing` module. Once imported, you can use it as a type hint for your tag string's arguments:

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

Let's add some typing information to our greet function.

```{code-block} python
>>> print(greet"Hello {name!r:s}")  # name is still World
Hello gv: World, r: name, c: r, f: s!
```

## Wrapup

That's a quick walkthrough tag strings. For a deeper dive, see the [HTML templating tutorial](./htmlbuilder.md).