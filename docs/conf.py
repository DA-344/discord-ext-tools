import os
import sys
from importlib.metadata import version as get_version

# Any extensions or modules to document with autodoc in other directories
# must be added to sys.path here. If they are relative to this directory
# use os.path.abspath as shown here.
sys.path.insert(0, os.path.abspath('..'))
sys.path.append(os.path.abspath('extensions'))

# Extensions to use within the sphinx build
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.autosummary",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.duration",
    "sphinxcontrib_trio",
    "exception_hierarchy",
    "attributetable",
    "resourcelinks",
    "myst_parser",
    "sphinx_copybutton",
    "sphinxext.opengraph",
    "sphinx_autodoc_typehints",
]

always_document_param_types = True
toc_object_entries_show_parents = "hide"
autosectionlabel_prefix_document = True

autodoc_member_order = "bysource"
autodoc_typehints = "none"
napoleon_attr_annotations = True

extlinks = {
    "issue": ("https://github.com/DA-344/discord-ext-tools/issues/%s", "GH-%s"),
}
intersphinx_mapping = {
    "py": ("https://docs.python.org/3", None),
    "dpy": ("https://discordpy.readthedocs.io/en/latest/", None),
}
rst_prolog = """
.. |coro| replace:: This function is a |coroutine_link|_.
.. |maybecoro| replace:: This function *could be* a |coroutine_link|_.
.. |coroutine_link| replace:: *coroutine*
.. _coroutine_link: https://docs.python.org/3/library/asyncio-task.html#coroutine
"""

# The suffix of source filenames.
source_suffix = {
    ".rst": "restructuredtext",
}

# Master toctree doc
master_doc = "index"

# General information about the project
project = "discord-tools"
copyright = "2024-present, DA344"

# Full Version
release = get_version("discord.py-tools")
# X.Y version
version = ".".join(release.split(".")[:2])


# This assumes a tag is available for final releases
master_tags = ("a", "b", "rc", "dev")
branch = (
    "master"
    if any(tag in version for tag in master_tags) else
    f"v{release}"
)
html_title = f"{project} v{version} Documentation"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

exclude_patterns = ["_build", "node_modules", "build"]

html_experimental_html5_writer = True
html_theme = "furo"
html_context = {}

resource_links = {
    "issues": "https://github.com/DA-344/discord-ext-tools/issues",
}

base_colors = {
    "white": "#ffffff",
    "grey-1": "#f9f9fa",
    "grey-1-8": "rgba(249, 249, 250, 0.8)",
    "grey-2": "#ededf0",
    "grey-3": "#d7d7db",
    "grey-4": "#b1b1b3",
    "grey-5": "#2a2a2b",
    "grey-6": "#4a4a4f",
    "grey-7": "#2a2a2b",
    "grey-8": "#1e1e1f",
    "black": "#0c0c0d",
    "blue-1": "#3399ff",
    "blue-2": "#0a84ff",
    "blue-3": "#0060df",
    "blue-4": "#003eaa",
    "blue-5": "#002275",
    "blue-6": "#000f40",
    "blurple": "#7289da",
}

html_theme_options = {
    "source_repository": "https://github.com/Pycord-Development/pycord",
    "source_branch": "master",
    "source_directory": "docs/",
    "light_css_variables": {
        # Theme
        # "color-brand-primary": "#5865f2",
        "font-stack": "'Outfit', sans-serif",
        # Custom
        **base_colors,
        "attribute-table-title": "var(--grey-6)",
        "attribute-table-entry-border": "var(--grey-3)",
        "attribute-table-entry-text": "var(--grey-5)",
        "attribute-table-entry-hover-border": "var(--blue-2)",
        "attribute-table-entry-hover-background": "var(--grey-2)",
        "attribute-table-entry-hover-text": "var(--blue-2)",
        "attribute-table-badge": "var(--grey-7)",
        "light-snake-display": "unset",
        "dark-snake-display": "none",
    },
    "dark_css_variables": {
        # Theme
        # "color-foreground-primary": "#fff",
        # "color-brand-primary": "#5865f2",
        # "color-background-primary": "#17181a",
        # "color-background-secondary": "#1a1c1e",
        # "color-background-hover": "#33373a",
        # Custom
        "attribute-table-title": "var(--grey-3)",
        "attribute-table-entry-border": "var(--grey-5)",
        "attribute-table-entry-text": "var(--grey-3)",
        "attribute-table-entry-hover-border": "var(--blue-1)",
        "attribute-table-entry-hover-background": "var(--grey-6)",
        "attribute-table-entry-hover-text": "var(--blue-1)",
        "attribute-table-badge": "var(--grey-4)",
        "light-snake-display": "none",
        "dark-snake-display": "unset",
    },
}
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
html_js_files = ["js/custom_js"]

html_search_language = "en"
htmlhelp_basename = "dpy-ext-tools-doc"


latex_elements = {}
latex_documents = [
    ('index', 'discord-tools.tex', 'discord-tools Documentation',
     'DA344', 'manual'),
]
man_pages = [
    ('index', 'discord-tools', 'discord-tools Documentation',
     ['DA344'], 1)
]
texinfo_documents = [
    ('index', 'discord-tools', 'discord-tools Documentation',
     'DA344', 'discord-tools', 'One line description of project.', 'Miscellaneous',),
]
