# Tag strings

An early stage PEP that introduces tag strings - a natural extension of "f-strings" from [PEP 498](https://peps.python.org/pep-0498/) which enables Python developers to create and use their own custom tags (or prefixes) when working with string literals and any interpolation. Tag strings are based on a related idea in JavaScript, [tagged template literals](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals#tagged_templates) but with a Pythonic syntax for both the use of and the definition of tags.

## Try tag strings today!

### Using [GitHub Codespaces](https://github.com/features/codespaces)

The fastest way to try tag strings, right in your browser.

1. Go to the [repo homepage](https://github.com/pauleveritt/tagstr-site/)
1. Click the "Code" button
1. Click the "Codespaces" tab
1. Click "Create codespace on main"
1. After things spin up, you'll have [vscode](https://code.visualstudio.com/) in your browser, attached to cloud dev environment
1. Open a terminal in vscode (`ctrl` + `shift` + `\``)
1. `make install`
1. Try it! `python src/tagstr_site/htmldom.py`

### Using your local dev machine

If you have [vscode](https://code.visualstudio.com/) and [Docker](https://www.docker.com/) installed locally, you can:

1. Clone this repository
1. Open it in `vscode`
1. When prompted by `vscode`, click the "Re-open in Container" button
1. Open a terminal in vscode (`ctrl` + `shift` + `\``)
1. `make install`
1. Try it! `python src/tagstr_site/htmldom.py`

## Documents

- [Documentation](https://pauleveritt.github.io/tagstr-site/) from this website including the [HTML tutorial](https://pauleveritt.github.io/tagstr-site/htmlbuilder.html)
- [WIP PEP](https://github.com/jimbaker/tagstr/blob/main/pep.rst)
- [Implementation (WIP) based on 3.14](https://github.com/lysnikolaou/cpython/tree/tag-strings-rebased)

## Related Work

- [Flufl i18n substitutions](https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders)
- [Tagged library](https://github.com/jviide/tagged)
- [PEP 501: Interpolation templates](https://peps.python.org/pep-0501/)
- [Earlier work by the same authors](https://github.com/jimbaker/fl-string-pep)

## cpython docker images

This repo has a `/docker/` submodule that contains dockerfiles used to build [Lysandros](https://github.com/lysnikolaou)' underlying [cpython branch](https://github.com/lysnikolaou/cpython/tree/tag-strings-rebased). [Koudai](https://github.com/koxudaxi) manages the submodule and also has published the images to a registry at https://hub.docker.com/r/koxudaxi/python to make them easier to use.
