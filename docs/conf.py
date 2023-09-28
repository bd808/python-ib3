#!/usr/bin/env python3
import datetime
import importlib.metadata

import sphinx_rtd_theme

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "irc": ("https://python-irc.readthedocs.io/en/stable/", None),
}

# General information about the project.
metadata = importlib.metadata.metadata("ib3")
project = metadata["name"]
version = metadata["version"]
author = "Bryan Davis"

_origin_date = datetime.date(2017, 2, 19)
_today = datetime.date.today()

copyright = f"{_origin_date.year}-{_today.year} {author} and contributors"
release = version

master_doc = "index"
pygments_style = "sphinx"
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ["_static"]

suppress_warnings = ["image.nonlocal_uri"]
