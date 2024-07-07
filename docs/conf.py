project = "tagstr_site"
copyright = "2024, Jim Baker"
author = "Jim Baker"
release = "0.0.1"
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
]
# templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "lazy.md"]
html_theme = "sphinx_book_theme"
html_title = "Using Tag Strings"
# html_static_path = ["_static"]
myst_enable_extensions = ["colon_fence"]
html_theme_options = {"navigation_with_keys": False}
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
