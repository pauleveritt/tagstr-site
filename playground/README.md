## Contents

This directory contains [example notebooks that use tag strings](./content/).

It also contains tooling to publish these notebooks as a static website, which you can [use in your browser without any installation](https://pauleveritt.github.io/tagstr-site/playground/lab/index.html?path=greet.ipynb).

![[simple](images/simple.png)](https://raw.githubusercontent.com/pauleveritt/tagstr-site/main/playground/images/simple.png)

This uses the magic of [WASM](https://webassembly.org/), [pyodide](https://pyodide.org/en/stable/), and [JupyterLite](https://jupyterlite.readthedocs.io/en/stable/). We publish these changes [automatically](../.github/workflows/playground.yaml) to [github pages](https://pages.github.com/).

The `/pyodide` directory has pyodide binary of Python 3.14.0a7 based on the [PEP WIP implementation found here](https://github.com/lysnikolaou/cpython/tstrings). It is built by [a fork](https://github.com/koxudaxi/pyodide/tree/support_tag-strings) of [hoodmane's python-3.14.0a0 tag-string branch](https://github.com/hoodmane/pyodide/tree/314dev-string-fmt-pep).
