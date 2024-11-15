# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Rocket optimizer"
copyright = "2024, Jan Heimann"
author = "Jan Heimann"
release = "0.7"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "sphinx_copybutton"]


templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = 'furo'

import os
import sys
sys.path.insert(0, os.path.abspath('.'))

# Configuration for static files
html_static_path = ['_static']

# Configuration of sphinx-copybutton
copybutton_prompt_text = "Copy to Clipboard"
copybutton_exclude = ".linenos, .gp, .go"
