# Building an HTML Templating Engine

HTML templating is an important part of web development and Python has a long, long history here. Template languages are
like a domain-specific language (DSL), which tag strings were built for. Tag strings provide an opportunity: a
syntax specifically designed to ease HTML templating.

In the tutorial to follow, you'll learn how to create an `html` tag which can do just this. Specifically, the
tutorial will bring your markup and logic closer together by taking inspiration from
[JSX](https://reactjs.org/docs/introducing-jsx.html), a syntax extension to
JavaScript commonly used in [ReactJS](https://reactjs.org/) projects.

Here are some examples of the kinds of things you could ultimately do.

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

This might be difficult to achieve with a standard templating solution.
More interesting though: this `html` tag will output a structured
representation of the HTML that can be freely manipulated - a Document Object Model
(DOM) of sorts for HTML.

```python
node: HTML = html"<h1/>"
node.attributes["color"] = "blue"
node.children.append("Hello, world!")
assert str(node) == '<h1 color="blue">Hello, world!</h1>'
```

But first, let's see why tag strings might be a better fit over existing, mature choices such as Jinja2.

## Why not Jinja2?

Python template languages such as Jinja2 take contextual data and generate larger bodies of text, such as HTML. For
example, if you wanted to create a simple todo list using Jinja it might look something like this.

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
it's less straightforward.

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

The result:

```html
<h1>My Todo List</h1>
<ol>
  <li value="3">Eat</li>
  <li style="font-weight: bold">Eat</li>
  <li type="a" style="font-weight: bold">Eat</li>
</ol>
```

One problem: Jinja is a generic templating tool, so the specific needs that come with rendering
HTML, like expanding dynamic attributes, aren't supported out of the box. More broadly, Jinja templates make it
difficult to coordinate business and UI logic since markup in the template is kept separate from your logic in Python.

This is a key point, one that makes it hard to provide good tooling. Jinja2 has different scope rules, calling
semantics, and composition approaches than Python. This means tools like Black, Ruff, and mypy can't really peak inside
that part of your project.

## Review: tag string protocols

With tag strings, we write a function that receives an `args` sequence of `Decoded` and `Interpolation` values. These
are Python "protocols". `Decoded` is a string with an extra `raw` value.

```{literalinclude} ../src/tagstr_site/tagtyping.py
:start-at: class Decoded
:end-at: raw
```

The `Interpolation` object captures a dynamic part (between braces) in a tag string.

```{literalinclude} ../src/tagstr_site/tagtyping.py
:start-after: class Interpolation
:end-at: format_spec
```

## AST and HTML trees

We're going to use an HTML "template" to render some data. Our strategy could be to do all the processing in one step. But most templating systems split into several steps, for reasons such as performance.

This tutorial will show a parsing step and a rendering step. The parsing step will create an [abstract syntax tree](https://en.wikipedia.org/wiki/Abstract_syntax_tree) or AST. The AST will be a nested collection of Python data, representing the tree of HTML. It will also, though, capture the "placeholders" where something dynamic needs to be inserted.

For this, we'll have an `AstParser` which generates `AstNode` objects. Here's what the `AstNode` will look like:

```{literalinclude} ../src/tagstr_site/htm.py
:start-at: Use as an AST for HTML
:end-at: children: list
```

In a second step, we'll use the `AstNode` tree to create a tree of `HtmlNode` objects, with the rendered data.

## Parsing HTML

Before we introduce templating, let's cover the basics of HTML parsing. In the next few steps, we'll keep it very
simple: for example, no support for attributes.

Given that you're going to be parsing HTML, it will be useful to lean on Python's
built-in {py:class}`html.parser.HTMLParser` which can be subclassed to customize its behavior:

:::{note}
An {py:class}`html.parser.HTMLParser` instance is fed HTML data 
and calls handler
methods when start tags, end tags, text, comments, and other markup elements are
encountered. The user should subclass {py:class}`html.parser.HTMLParser` and override
its methods to implement the desired behavior.
:::

Specifically, we'll fill in these `HTMLParser` methods:

- {py:meth}`html.parser.HTMLParser.handle_starttag` - handles the start tag of an element (`<div id="something">`).
- {py:meth}`html.parser.HTMLParser.handle_data` - processes text in the body of an element (`<div>arbitrary text</div>`).
- {py:meth}`html.parser.HTMLParser.handle_endtag` - handles the end tag of an element (`</div>`).

Let's start with a class that inherits from the `HTMLParser`.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb1.py
:start-at: class AstParser
:end-at: return self.stack[-1]
```

Our initializer function makes a root node and sets it as the only element in the "stack". The root node is an instance of the `AstNode` object described above.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb1.py
:start-at: @dataclass
:end-at: children: list
```

Again: for now, we're not interested for now with attributes.

What's the purpose of `self.stack`? As we go down through nested nodes, we need to keep track of the parent element that is
currently being constructed at any point. This lets you append newly created child elements and body text to
the appropriate parent element. We use a data structure called
a [stack](<https://en.wikipedia.org/wiki/Stack_(abstract_data_type)>) to do just this.

The `parent` property is just a convenience, making it easier to grab the most-recent node on the stack.

The `AstParser` needs a method to handle the starting of a tag.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb1.py
:start-at: def handle_starttag
:end-at: self.stack.append
```

With this, the starting of a tag -- such as `<div>` -- makes a new `AstNode` and adds it to the parent node's children.
The method also "pushes" this new node onto the stack, making it the "parent".

The `handle_data` method takes care of the non-node children. Primarily, this is the plain text.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb1.py
:start-at: def handle_data
:end-at: children.append
```

The `handle_endtag` is run when a tag closes, for example, `</div>`:

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb1.py
:start-at: def handle_endtag
:end-at: raise
```

This example doesn't do much -- it just "pops" the current tag from the stack and ensures the starting and ending tag
names match.

To simplify the process of closing the `HTMLParser` and extracting the `AstNode` tree, we
add a `result()` method.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb1.py
:start-at: def result
:end-at: return self.root
```

Let's see this in action. First we construct a root `AstNode`.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb1.py
:start-at: parser = AstParser()
:end-at: root_node = 
```

Now poke around and see if it has what we expect.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb1.py
:start-at: assert "div"
:end-at: assert "Hello
```

That's it for a very simple HTML parser. It can handle a tree of nodes, but can't handle attributes. It certainly can't
handle templating. Let's tackle that next.

## Handling interpolations

We now have an "AST" representation of the HTML. But not the interpolations. In fact, we haven't implemented the {py:meth}`html.parser.HTMLParser.feed` method. This means we're using the standard feed method. It only takes strings, and our tag function's `args` is a sequence of string-like values and interpolations

:::{note}
Tag functions can take a string-like thing and an interpolation. The PEP defines protocols for these: `Decoded` and
`Interpolation`. The tutorial will use these protocol names, rather than implementation names.
:::

Our interpolations are position-based, so we need to keep an index as we are fed the args.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb2.py
:start-at: class AstParser
:end-at: self.index
:emphasize-lines: 4
```

:::{note}
Remember, each `arg` will never have more than one "position" to substitute. Tag string evaluation digests the tag
string value into chunks.
:::

We now override the base class's feed method.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb2.py
:start-at: def feed
:end-at: self.index += 1
:emphasize-lines: 1, 4, 8, 11, 13
```

- Our `feed` method takes strings and `Interpolation`
- The pattern matching expects something shaped like a string or an `Interpolation`, and fails if it gets something else
- Strings just get fed to the parser for now (later, some processing)
- Interpolations get fed a placeholder that encodes the index

This placeholder strategy is the key to the templating. We are encoding a tiny bit of structure, into a string. Namely, the position in the args that should later get substituted.

:::{note}
Why `x$Nx`as placeholder? `HTMLParser`includes a regex pattern for element tags that expects them to begin with a letter.
To allow element tags themselves to be interpolated (e.g. `div`), the first character of the placeholder must meet this
requirement. In our case, we just happen to have chosen `x`.

Also, after "escaping" user provided strings by replacing all `$` characters with `$$`, there is no way for a user to
feed a string that would result in `x$Nx`. Thus, we can reliably identify any `x$Nx` passed to the parser to be
placeholders.
:::

Let's see the updated `AstParser` in action.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb2.py
:start-at: name = "World"
:end-at: root_node: AstNode
```

As you can see, it can encode interpolation points.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb2.py
:start-at: assert "div"
:end-at: assert ["Hello
```

That's it for the parser update. It re-uses the methods we already implemented for start/end tag and data. Let's hook `AstParser` up to a tag function.

## Tag function

So far we've made example `AstNode` roots by talking to the parser. To simplify our work, and to build towards tag strings, let's make a tag function that returns an `AstNode`.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb3.py
:start-at: def html
:end-at: return parser
```

This is a simple tag function. It makes an `AstParser` and pumps `args` into its `feed`. When done, it returns the parser's `result`.

Now our demos can use tag strings.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb3.py
:start-at: name = 
:end-at: root_node: AstNode
```

This tag string results in the same `AstNode`.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb3.py
:start-at: assert "div"
:end-at: assert ["Hello "
```

We're now ready to start interpolating.

## Starting a fill strategy

DSLs are going to have rich ideas about filling data into templates. It's nice to isolate this "filling" part: for testing, for swapping policies, etc.

In this step we introduce a fill strategy. It doesn't *actually* do any dynamic filling. Instead, we just outline how it works.

We'll go in the order of processing. Our `html` tag function is now going to return something that looks like HTML. As such, we have an `HTML` protocol, so we can be independent with the implementation. Here's the implementation we are using: an `HtmlNode`.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb4.py
:start-after: The start of
:end-at: children
```

Our tag function now returns `HTML` instead of `AstNode`. It does this by using a `Fill` strategy that interpolates *into* the parser results. Meaning, it fills the AST.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb4.py
:start-at: def html
:end-at: return Fill
:emphasize-lines: 5
```

Next we have the `Fill` dataclass. It stores the `args` it was given. This dataclass the heart of the filling-in step.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb4.py
:start-after: Pluggable
:end-at: args
```

The action starts in the `interpolate` method. This is the method called by tag function, passing in the AST.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb4.py
:start-at: def interpolate
:end-at: return self.fill_tag
:emphasize-lines: 6,8
```

This pattern matching block is the dispatcher approach we've been seeing. It handles `AstNode` objects from the parser, going through children. 

If the child is another *node*, the method recurses, calling `self.interpolate` again and appending the result. If the parser stored a *string*, `interpolate` calls the filling strategy and returns the result.

The filling strategy in this section is just a stand-in. We'll do actual interpolation in the next step.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb4.py
:start-at: def fill
:end-at: yield "I WAS
```

Our `self.interpolate` method closed with a call to `self.fill_tag`, passing in the AstNode's tag and the interpolated children. Here's a simple version `self.fill_tag`.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb4.py
:start-at: def fill_tag
:end-at: return HtmlNode
```

While we're not filling in the `HTML` with values from the tag string, we are filling them in with fake results. Let's see it in use:

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb4.py
:start-at: name = 
:end-at: root_node: HtmlNode
```

As you can see -- `I WAS FILLED`.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb4.py
:start-at: assert "div"
:end-at: assert ["Hello
```

With this introduction to fill strategies in place, let's actually fill in the placeholders with real values.

## Fill in values

It turns out that filling in values is a pretty interesting step in the process. Our previous `fill` method was boring: it ignored what it was passed and just returned `I WAS FILLED` if the string had a placeholder in it.

In this step we will process the placeholder and get the correct value. Along the way, we'll leave behind a spot to do any handling of the value. Here's the new `fill` method.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb5.py
:start-at: def fill
:end-at: yield s
:emphasize-lines: 7,11
```

It's terse but action-packed. First, it calls another method to pick apart the structure in the string, in case it is a placeholder. It does this by calling a helper method `self.split_by_placeholder`.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb5.py
:start-at: def split_by_placeholder
:end-at: yield split
:emphasize-lines: 5,9
```

This helper is looking to see if a string looks like it has a placeholder. If so, it gets the index from the `x$ix` structure in the string. It then yields the arg at that position.

The helper has returned either a string or an...`Interpolation`! We are now back to the point where we can call the lambda to evaluate the expression.

The pattern matching in the `fill` method handles either the interpolation (by getting the value) or just return ing a string. We'll do more here in the next steps.

Let's see our first look at dynamic HTML rendering.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb5.py
:start-at: name =
:end-at: root_node: HtmlNode
```

We have indeed filled in some values.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb5.py
:start-at: assert "div"
:end-at: assert ["Hello "
```

It's now time to handle attributes, albeit a simple case.

## Simple attributes

So far we left out attribute handling, to let us get an end-to-end view of the simplest case. Attributes are actually a topic with lots of interesting possibilities. Which we'll ignore for now, and just handle the simplest usage.

Nothing changes in most of our code. The AST parser and tag function remain the same. Our `Fill` policy, though, will be taught how to handle attributes.

We said the `interpolate()` method was the tag function's entry point to filling. We'll start there.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb6.py
:start-at: def interpolate
:end-at: return self.fill_tag
:emphasize-lines: 10-14
```

The tag function passed this method an AST node to get interpolated. That node might have attributes and those attributes might be dynamic -- meaning, need interpolation.

We pass each attribute to a new `self.fill_attr` method, then pass the newly-filled attributes to `self.fill_tag`.

Filling placeholders in an attribute is -- for now -- simple.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb6.py
:start-at: def fill_attr
:end-at: return {
```

Also as part of this step, we close the loop on two places we skipped. Our `fill` method now calls a passed-in conversion function. If none is provided, it defaults to `str()`. Let's use that conversion function.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb6.py
:start-at: def fill(
:end-at: yield s
:emphasize-lines: 10
```

Next, we clean up `fill_tag` to support interpolation in the tag name itself.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb6.py
:start-at: def fill_tag(
:end-at: return HtmlNode
:emphasize-lines: 3
```

With this in place, we make an example that uses both attributes and a dynamic heading level in a tag.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb6.py
:start-at: name = "World"
:end-at: root_node: HtmlNode
```

We now have attriburtes and our heading level matches the integer `1` from the variable.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb6.py
:start-at: assert "h1"
:end-at: assert ["Hello
```

We've now implemented quite a bit of templating. Except: making a string. Let's see that next.

## DOM to string

We have an HTML "DOM" as nested Python data. We need a way to "stringify" it, possibly with some policies along the way.

We'll add a `__str__` method to our `HtmlNode` dataclass.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb7.py
:start-after: Add a `__str__`
:end-at: return ''.join(spaced)
```

Quite a bit going on, as HTML has a number of interesting places to customize. With this in place, we can stringify our `HtmlNode`.

```{literalinclude} ../src/tagstr_site/examples/htmlbuilder/hb7.py
:start-at: result = str(root_node)
:end-at: assert expected == result
```

## Wrapup

We've just seen the basics for writing an HTML templating engine based on tag strings. 
There's a lot more to show -- escaping inputs, using the conversion and format_spec flags, subcomponents -- but those are topics for other tutorials.
