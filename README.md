# Tag strings

An early stage PEP that introduces tag strings - a natural extension of "f-strings" from [PEP 498](https://peps.python.org/pep-0498/) which enables Python developers to create and use their own custom tags (or prefixes) when working with string literals and any interpolation. Tag strings are based on a related idea in JavaScript, [tagged template literals](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals#tagged_templates) but with a Pythonic syntax for both the use of and the definition of tags.

## Install

```shell
$ path/to/venv/bin/pip install -e .
```

## Docker

This repo has a `/docker/` directory with Dockerfiles for various images.
Koudai manages these and also has published them to a registry at https://hub.docker.com/r/koxudaxi/python
to make it easier to use.

## Documents

- [WIP PEP](https://github.com/jimbaker/tagstr/blob/main/docs/pep.rst)
- [Tutorial](https://github.com/jimbaker/tagstr/blob/main/docs/tutorial.rst)
- [Implementation (WIP)](https://github.com/gvanrossum/cpython/tree/tag-strings-v2)

## Examples

- [Shell](https://github.com/jimbaker/tagstr/blob/main/src/tagstr/shell.py)
- [SQL](https://github.com/jimbaker/tagstr/blob/main/src/tagstr/sql.py)
- [HTML](https://github.com/jimbaker/tagstr/blob/main/src/tagstr/htmldom.py)
- [Among others...](https://github.com/jimbaker/tagstr/blob/main/src/tagstr)

## Related Work

- [Flufl i18n substitutions](https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders)
- [Tagged library](https://github.com/jviide/tagged)
- [PEP 501: Interpolation templates](https://peps.python.org/pep-0501/)
- [Earlier work by the same authors](https://github.com/jimbaker/fl-string-pep)

## Devcontainers and vscode

If you use [vscode](https://code.visualstudio.com/) and have [Docker](https://www.docker.com/) installed, this repository includes a [devcontainer](https://code.visualstudio.com/docs/devcontainers/containers) to get you running the included demos on top of a pre-release version of python that supports tag strings.

To get going:

1. Open this repository in `vscode`
2. When prompted by `vscode`, click the "Re-open in Container" button
3. After the container is built and running, open a terminal. The terminal should be "inside" the devcontainer. You'll be running as a root user and a python [venv](https://docs.python.org/3/library/venv.html) will already be configured and activated.
4. Run `make install` to install dependencies into your venv
5. Try a demo! For instance, `python src/tagstr_site/htmldom.py`
