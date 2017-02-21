#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import os
import subprocess
import sys

import sphinx_rtd_theme

if 'check_output' not in dir(subprocess):
    import subprocess32 as subprocess

sys.path.insert(0, os.path.abspath('../'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'irc': ('https://python-irc.readthedocs.io/en/stable/', None),
}

# General information about the project.
root = os.path.join(os.path.dirname(__file__), '..')
setup_script = os.path.join(root, 'setup.py')
fields = ['--name', '--version', '--author']
dist_info_cmd = [sys.executable, setup_script] + fields
output_bytes = subprocess.check_output(dist_info_cmd, cwd=root)
project, version, author = output_bytes.decode('utf-8').strip().split('\n')

_origin_date = datetime.date(2017, 2, 19)
_today = datetime.date.today()

copyright = '{_origin_date.year}-{_today.year} {author}'.format(**locals())

release = version

master_doc = 'index'
pygments_style = 'sphinx'
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']

suppress_warnings = ['image.nonlocal_uri']
