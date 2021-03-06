# -*- coding: utf-8 -*-
#
# electrical documentation build configuration file, created by
# sphinx-quickstart on Thu Mar 22 15:47:53 2012.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import sys
import os
import sphinx_bootstrap_theme

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath('..'))

# -- General configuration -----------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.mathjax',
              'sphinxcontrib.napoleon']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'contents'

# General information about the project.
project = u'corr'
copyright = u'2019 US NIST MGI'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = "0.2"
# The full version, including alpha/beta/rc tags.
release = "0.2"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']
autoclass_content = 'both'

# The reST default role (used for this markup: `text`) to use for all documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []


# -- Options for HTML output ---------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#html_theme = 'sphinxdoc'
html_theme = 'bootstrap'
html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
# ("Storage", "rst/corr-db/README.html", True),
# ("API", "rst/corr-api/README.html", True),
# ("Cloud", "rst/corr-cloud/README.html", True),
# ("Frontend", "rst/corr-view/README.html", True),
html_theme_options = {
    'navbar_title': "*",
    'navbar_links': [
        ("launch", "rst/LAUNCH.html", True),
        ("use", "rst/USE.html", True),
        ("contribute", "https://github.com/usnistgov/corr", True),
        ("corr.nist.gov", "https://corr.nist.gov", True),
    ],
    'navbar_pagenav': False,
    'navbar_sidebarrel': False,
    'globaltoc_depth': 1,
    'source_link_position': '',
    'bootswatch_theme': 'cosmo'
}

# Add any paths that contain custom themes here, relative to this directory.
#html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = "CoRR"

# A shorter title for the navigation bar.  Default is the same as html_title.
html_short_title = "CoRR"

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = 'logo.png'

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = 'logo.ico'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
html_additional_pages = {}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
html_show_copyright = False

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = 'corrdoc'


# -- Options for LaTeX output --------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
    ('index', 'corr.tex', u'CoRR Documentation',
     u'Faical Yannick P. Congo', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True


# -- Options for manual page output --------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'corr', u'CoRR Documentation',
     [u'Faical Yannick P. Congo'], 1)
]

# If true, show URL addresses after external links.
#man_show_urls = False


# -- Options for Texinfo output ------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    ('index', 'corr', u'CoRR Documentation',
     u'Faical Yannick P. Congo', 'corr', 'Cloud of Reproducible Records',
     'Miscellaneous'),
]


# Documents to append as an appendix to all manuals.
#texinfo_appendices = []

# If false, no module index is generated.
#texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#texinfo_show_urls = 'footnote'

from recommonmark.parser import CommonMarkParser
from recommonmark.transform import AutoStructify

source_parsers = {'.md' : CommonMarkParser}
source_suffix = ['.rst', '.md']

def url_resolver(url):
    """Resolve url for both documentation and Github online.

    If the url is an IPython notebook links to the correct path.

    Args:
      url: the path to the link (not always a full url)

    Returns:
      a local url to either the documentation or the Github

    """
    if url[-6:] == '.ipynb':
        return url[4:-6] + '.html'
    else:
        return url

def setup(app):
    app.add_config_value('recommonmark_config', {
            'url_resolver': url_resolver,
            'auto_toc_tree_section': 'Contents',
            }, True)
    app.add_transform(AutoStructify)
    app.add_stylesheet('corr.css')

import shutil, os, glob

rst_directory = 'rst'
# db_directory = 'rst/corr-db'
# api_directory = 'rst/corr-api'
# cloud_directory = 'rst/corr-cloud'
# view_directory = 'rst/corr-view'

for directory in [rst_directory]:#, db_directory, api_directory, cloud_directory, view_directory]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# 'corr-db/README.md',
# 'corr-api/README.md',
# 'corr-cloud/README.md',
# 'corr-view/README.md',

files_to_copy = (
    'README.md',
    'LAUNCH.md',
    'USE.md'
)

print("+"*24)
print(files_to_copy)

for fpath in files_to_copy:
    for fpath_glob in glob.glob(os.path.join('..', fpath)):
        fpath_glob_ = '/'.join(fpath_glob.split('/')[1:])
        print("{} -> {}".format(fpath_glob, os.path.join(rst_directory, fpath_glob_)))
        shutil.copy(fpath_glob, os.path.join(rst_directory, fpath_glob_))
