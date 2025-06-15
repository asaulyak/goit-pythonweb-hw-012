# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
import os
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(".."))
sys.path.append(os.path.abspath("."))  # Add current directory to Python path

# Mock the src.config module
sys.modules['src.config'] = MagicMock()
from mock_config import settings
sys.modules['src.config'].settings = settings

project = "Contacts REST API"
copyright = "2025, Eugene Asaulyak"
author = "Eugene Asaulyak"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc"]

autodoc_mock_imports = ["src.config"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
