# Lazy Evaluation

People love f-strings, but one frequent complaint: immediate execution. Sometimes lazy evaluation is needed, where the
evaluation might not happen immediately.

```{note}
This example shows that "lazy" is best used in a mode where you
either use it immediately, or never use it. As will be shown, if
you defer the execution until much-later, then (like exception
instances) you'll get surprising results.
```

## Getting Started

<!--- invisible-code-block: python
from tagstr_site.fl.fl1 import demo
-->

Let's return to the greeting example from the PEP. As a starting point, it's the common  pattern:

```{literalinclude} ../../src/tagstr_site/fl/fl1.py
```

To focus on lazy execution, we've left out all the bits to handle edge cases: ``decode_raw`` and ``format_value`` etc.
The demo shows us the result of each pass:

```{code-block} python
>>> demo()
'0: Hello\n1: Hello\n2: Hello'
```

This example, though, is a good illustration of tag string's "lambda capture".
For each ``fl`` usage in the ``for`` loop, tag strings provides a lambda callable which executes in the scope it is called.
As such, the ``i`` variable from the ``range`` is in scope, as well as ``greeting`` from the ``demo1`` function scope.

This is important in just a bit.

## Tag String Class

<!--- invisible-code-block: python
from tagstr_site.fl.fl2 import demo
-->

Our strategy for deferred evaluation: only execute when the result is stringified. In this step, let's convert the tag
string function to return an instance of a dataclass:

```{literalinclude} ../src/tagstr_site/fl/fl2.py
:start-at: @dataclass
:end-at: return Lazy
```

Our ``fl`` function now just returns an instance. No tag string processing is done until ``str(result)`` in
the ``demo`` function:

```{literalinclude} ../src/tagstr_site/fl/fl2.py
:start-at: def demo
:end-at: return "\n"
:emphasize-lines: 7
```

The ``demo`` returns the same output:

```{code-block} python
>>> demo()
'0: Hello\n1: Hello\n2: Hello'
```

To recap: our tag string is split in half. The usage returns an instance. The processing happens with the ``str()`` call.

## Deferred String-ifying

<!--- invisible-code-block: python
from tagstr_site.fl.fl3 import demo
-->

What happens if we wait too long before executing the tag scope?
In this example, the ``str()`` is called outside the loop:

```{literalinclude} ../../src/tagstr_site/fl/fl3.py
:start-at: def demo
:end-at: return "\n"
:emphasize-lines: 11
```

As the comment notes, the "lambda capture" function runs and gets ``i`` from the scope.
But it's the last ``i`` *after* the loop finishes:

```{code-block} python
>>> demo()
'2: Hello\n2: Hello\n2: Hello'
```

As such, the rule of thumb for lazy evaluation: either use it immediately, or throw it out.
Like exception tracebacks, you shouldn't hold onto them for later use.
That's a foot-gun.
