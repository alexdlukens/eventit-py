import os
import sys

import toml

sys.path.insert(0, os.path.abspath("../../"))
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Eventit-py"
copyright = "2024, Alexander Lukens"
author = "Alexander Lukens"

# get the release version from pyproject.toml

# Read the pyproject.toml file
with open("../../pyproject.toml", "r") as f:
    pyproject = toml.load(f)

# Get the release version
release = pyproject["tool"]["poetry"]["version"]
version = f"v{release}"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "sphinx_rtd_theme", "sphinx.ext.napoleon"]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

html_logo = (
    "_static/logos/EventIT_Logo_Original_with_Transparent_Background_cropped.svg"
)
html_theme_options = {
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "vcs_pageview_mode": "",
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
}

html_context = {
    "display_github": True,
    "github_user": "alexdlukens",
    "github_repo": "eventit-py",
    "github_version": "master/docs/source/",
}
