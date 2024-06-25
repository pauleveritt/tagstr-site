# Building an HTML Templating Engine

HTML templating is an important part of web development and Python has a long, long history here. Template languages are
like a domain-specific language (DSL), which tag strings were built for. Tag strings provide an opportunity to develop a
syntax specifically designed to make declaring elaborate HTML documents easier.

In the tutorial to follow, you'll learn how to create an `html` tag which can do just this. Specifically, the
tutorial will bring your markup and logic closer together by taking inspiration from
[JSX](https://reactjs.org/docs/introducing-jsx.html), a syntax extension to
JavaScript commonly used in [ReactJS](https://reactjs.org/) projects.

Here are some examples of what you'll be able to do:

```python
# Attribute expansion
attributes = {"color": "blue", "style": {"font-weight": "bold"}}
assert (
           str(html"<h1 {attributes}>Hello, world!</h1>")
       == '<h1 color="blue" style="font-weight:bold">Hello, world!<h1>'
)

# Recursive construction
assert (
           str(html"<body>{[html" < h{i} / > " for i in range(1, 4)]}</body>")
       == "<body><h1></h1><h2></h2><h3></h3></body>"
)
```

While this would certainly be difficult to achieve with a standard templating solution,
what's perhaps more interesting is that this `html` tag will output a structured
representation of the HTML that can be freely manipulated - a Document Object Model
(DOM) of sorts for HTML:

```python
node: HTML = html
"<h1/>"
node.attributes["color"] = "blue"
node.children.append("Hello, world!")
assert str(node) == '<h1 color="blue">Hello, world!</h1>'
```

But first, let's see why tag strings might be a better fit over existing, mature choices such as Jinja2.

## Why not Jinja2?

Python template languages such as Jinja2 take contextual data and generate larger bodies of text, such as HTML. For
example, if you wanted to create a simple todo list using Jinja it might look something like this:

```python
from jinja2 import Template

t = Template("""
<h1>{{ title }}</h1>
<ol>{% for item in list_items %}
    <li>{{ item }}</li>{% endfor %}
</ol>
""")

doc = t.render(title="My Todo List", list_items=["Eat", "Code", "Sleep"])

print(doc)
```

Which will render as:

```html
<h1>My Todo List</h1>
<ol>
  <li>Eat</li>
  <li>Code</li>
  <li>Sleep</li>
</ol>
```

This is simple enough, but Jinja templates can grow rapidly in complexity. For example,
if you want to dynamically set attributes on the `<li>` elements the Jinja template
it's less straightforward:

```python
from jinja2 import Template

t = Template(
    """
<h1>{{ title }}</h1>
<ol>{% for item in list_items %}
    <li {% for key, value in item["attributes"].items() %}{{ key }}={{ value }} {% endfor %}>
        {{ item["value"] }}
    </li>{% endfor %}
</ol>
"""
)

doc = t.render(
    title="My Todo List",
    list_items=[
        {
            "attributes": {"value": "'3'"},
            "value": "Eat",
        },
        {
            "attributes": {"style": "'font-weight: bold'"},
            "value": "Eat",
        },
        {
            "attributes": {"type": "'a'", "style": "'font-weight: bold'"},
            "value": "Eat",
        },
    ],
)

print(doc)
```

The result of which is:

```html
<h1>My Todo List</h1>
<ol>
  <li value="3">Eat</li>
  <li style="font-weight: bold">Eat</li>
  <li type="a" style="font-weight: bold">Eat</li>
</ol>
```

One of the problems here is that Jinja is a generic templating tool, so the specific needs that come with rendering
HTML, like expanding dynamic attributes, aren't supported out of the box. More broadly, Jinja templates make it
difficult to coordinate business and UI logic since markup in the template is kept separate from your logic in Python.

This is a key point, one that makes it hard to provide good tooling. Jinja2 has different scope rules, calling
semantics, and composition approaches than Python. This means tools like Black, Ruff, and mypy can't really peak inside
that part of your project.

## Review: tag string protocols

With tag strings, we write a function that receives an `args` sequence of `Decoded` and `Interpolation` values. These
are Python "protocols". `Decoded` is a string with an extra `raw` value:

```{literalinclude} ../src/tagstr_site/tagtyping.py
:start-before: class Decoded
:end-at: raw
```

The `Interpolation` object captures a dynamic part (between braces) in a tag string:

```{literalinclude} ../src/tagstr_site/tagtyping.py
:start-before: class Interpolation
:end-at: format_spec
```

## Parsing HTML

Before we introduce templating, let's cover the basics of HTML parsing. In the next few steps, we'll keep it very
simple: for example, no support for attributes.

Given that you're going to be parsing HTML, it will be useful to lean on Python's
built-in :class:`~html.parser.HTMLParser` which can be subclassed to customize its
behavior:

```{note}
An :class:`~html.parser.HTMLParser` instance is fed HTML data and calls handler
methods when start tags, end tags, text, comments, and other markup elements are
encountered. The user should subclass :class:`~html.parser.HTMLParser` and override
its methods to implement the desired behavior.
```

Specifically, to modify `HTMLParser` in order to you'll need to overwrite the following methods:

- :meth:`~html.parser.HTMLParser.handle_starttag` - handles the start tag of an element (`<div id="something">`).
- :meth:`~html.parser.HTMLParser.handle_data` - processes text in the body of an element (`<div>arbitrary text</div>`).
- :meth:`~html.parser.HTMLParser.handle_endtag` - handles the end tag of an element (`</div>`).

Let's start with a class that inherits from the `HTMLParser`:

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb1.py
:start-at: class
:end-at: return self.stack[-1]
```

Our initializer function makes a root node and sets it as the only element in the "stack".

First: what is `HtmlNode`? Just a simple dataclass to keep track of the pieces of a node we are interested in.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb1.py
:start-at: @dataclass
:end-at: children: list
```

Again: for now, we're not interested for now with attributes.

What's the purpose of the stack? As we go down through nested nodes, we need to keep track of the parent element is
currently being constructed at any point. This will allow you to append newly created child elements and body text to
the appropriate parent element. We use a data structure called
a [stack](<https://en.wikipedia.org/wiki/Stack_(abstract_data_type)>) to do just this.

The `parent` property is just a convenience, making it easier to grab the most-recent node on the stack.

The `HTMLParser` needs a method to handle the starting of a tag:

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb1.py
:start-at: def handle_start
:end-at: self.stack.append
```

With this, the starting of a tag -- such as `<div>` -- makes a new `HTMLNode` and adds it to the parent node's children.
The method also "pushes" this new node onto the stack, making it the "parent".

The `handle_data` method takes care of the non-node children. Primarily, this is the plain text:

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb1.py
:start-at: def handle_data
:end-at: self.parent.children
```

The `handle_endtag` is run when a tag closes, for example, `</div>`:

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb1.py
:start-at: def handle_endtag
:end-at: raise
```

This example doesn't do much -- it just "pops" the current tag from the stack and ensures the starting and ending tag
names match.

To simplify the process of closing the `HTMLParser` and extracting the `HtmlNode` tree, we
add a `result()` method:

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb1.py
:start-at: def result
:end-at: return self.root.children
```

That's it for a very simple HTML parser. It can handle a tree of nodes, but can't handle attributes. It certainly can't
handle templating. Let's tackle that next.

TODO Markdown link to full example

## Handling interpolations

This is pretty neat! Unfortunately though, this isn't quite enough to create an `html`
tag that can interpolate values because, at this point, the `feed()` method of your
`HtmlBuilder` only accepts strings. To use this in an `html` tag it will need to
accept both decoded strings and interpolations.

:::{note}
Tag functions can take a string-like thing and an interpolation. The PEP defines protocols for these: `Decoded` and
`Interpolation`. The tutorial will use these names, to be specificl
:::

Ultimately you'll want to be able to write the following tag function:

```python
from taglib.tagtyping import Decoded, Interpolation


def html(*args: Decoded | Interpolation) -> HtmlNode:
    builder = HtmlBuilder()
    for arg in *args:
        builder.feed(arg)
    return builder.result()
```

We are currently using the base class `feed` method. We need to implement our own, as `feed` will be handed both
`Decoded` and `Interpolation` args.

One approach: pass a "placeholder" string to the parser each time `feed()` is handed an `Interpolation` instead of a
`Decoded`. The engine stores this placeholder. Then in the _handler_ methods, when the placeholder is encountered,
the handler substitutes the corresponding value.

For example, given the following tag string:

```python
html"<div>{greeting}, {name}!</div>"
```

The `feed()` method would substitute the first expression with the placeholder `x$1x` so that the _parser_ receives the
string.

In the example above, `args` will be:

```python
['<div>', InterpolationConcrete(...), ', ', InterpolationConcrete(...), '!</div>']
```

Tag strings supply args positionally, so we track the index in the placeholder, to later do the substitution.
This is an important and general principle for interpolations in templating and DSLs.

With this, the parser can handle the placeholders.

:::{note}

Why `x$Nx`as placeholder? `HTMLParser`includes a regex pattern for element tags that expects them to begin with a letter.
To allow element tags themselves to be interpolated (e.g. `div`), the first character of the placeholder must meet this
requirement. In our case, we just happen to have chosen `x`.

Also, after "escaping" user provided strings by replacing all `$` characters with `$$`, there is no way for a user to
feed a string that would result in `x$Nx`. Thus, we can reliably identify any `x$Nx` passed to the parser to be
placeholders.
:::

We'll make a small change to the initializer, to let us track the index _position_ for placeholders. This `self.index`
value increments on each interpolation within a single `feed` call:

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb2.py
:start-at: class HtmlBuil
:end-at: self.index
```

TODO Use highlighting on the changed line

:::{note}
Remember, each `arg` will never have more than one "position" to substitute. Tag string evaluation digests the tag
string value into chunks.
:::

Now we implement our own `feed()` method, to handle both incoming `Decoded` _and_ incoming `Interpolation`:

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb2.py
:start-at: def feed
:end-at: self.index += 1
```

```{warning}
This example has not switched over yet to the Python 3.14 implementation which uses protocol-based pattern matching.
```

Once `feed()` has done its parsing job on each part, the relevant methods step in to process. For now, no change to
`handle_starttag` and `handle_endtag` as we'll presume the tags are not dynamic. (We'll get back to this.)

For `handle_data`, our strategy is simple: during parsing, we just keep strings with placeholders. We defer the actual
interpolation until later in the process.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb2.py
:start-at: def handle_data
:end-at: self.parent.children.append
```

The first line is a call to `interleave_with_values`. This function lets you reconnect each occurrence of the
placeholder with its corresponding expression value:

```{literalinclude} ../src/tagstr_site/examples/__init__.py
:start-at: def interleave_with_values
:end-at: return interleaved_values
```

It does this by:

- Splitting the substituted string on the placeholder, then
- Zipping the split string back together with the expression values

Our interpolations now work. We've left a bunch out, in order to focus on the flow and idea. Let's take
another step forward and add a tag function.

TODO Paul Show an example of recursion working on interpolations

## Serializing to a string

https://gist.github.com/jimbaker/670c31e8834f4634bc6402f482e9f2ec

## Tag function

We have a class based on `HTMLParser` with a `feed()` method that takes either a decoded or an interpolation. This
pattern of calling feed multiple times matches how a tag string works: a sequence of `Decoded` or `Interpolation`
segments.

Our tag function is straightforward:

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb3.py
:start-at: def html
:end-at: return
```

Each tag function argument is sent to `feed()`, then `result()` is called. Let's see this in action:

```python

```

## Props

## Interpolated tag names

## Safe inputs, conversion, and format_spec

To escape and unescape strings in this manner it will be useful to have the following utility functions:

```{literalinclude} ../src/tagstr_site/examples/__init__.py
:start-at: def escape_p
:end-at: return string.replace("$$", "$")
```

## Subcomponents

## Compiling templates for re-use

Or tree-walking interpreter.

### TODO

- Use Guido's htmlbuilder.py tree walker version as the more accessible HTML one
- Caching
- Streaming
- Next tutorial: SQL, using SQLglot - https://github.com/tobymao/sqlglot
- FIXME validate this is well-formed HTML
