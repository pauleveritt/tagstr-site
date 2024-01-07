project = "tagstr_site"
copyright = "2024, Jim Baker"
author = "Jim Baker"
release = "0.0.1"
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]
# templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "sphinx_book_theme"
# html_static_path = ["_static"]
myst_enable_extensions = ["colon_fence"]
