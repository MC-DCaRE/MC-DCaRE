# Configuration file for the Sphinx documentation builder.
#
# MC-DCaRE documentation build configuration.

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "MC-DCaRE"
copyright = "2024-2026, BC Cancer Physics"
author = "BC Cancer Physics"

release = "0.3"
version = "0.3.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

myst_heading_anchors = 3