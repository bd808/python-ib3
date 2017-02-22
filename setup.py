#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import setuptools
import sys

setup_requires = [
    'setuptools_scm>=1.15.0',
]
if 'nosetests' in sys.argv[1:]:
    setup_requires.append('nose>=1.0')

tests_require = ['nose>=1.0']

name = 'ib3'
description = 'IRC bot framework using mixins to provide common functionality'

with io.open('README.rst', encoding='utf-8') as readme:
    long_description = readme.read()

params = dict(
    name=name,
    use_scm_version=True,
    description=description,
    long_description=long_description,
    author='Bryan Davis',
    author_email='bd808@bd808.com',
    url='https://github.com/bd808/python-ib3',
    download_url='https://pypi.python.org/pypi/ib3',
    packages=setuptools.find_packages(
        exclude=['docs', 'tests', 'tests.*']),
    include_package_data=True,
    install_requires=[
        'irc>=15.0.3',
    ],
    extras_require={
        'testing': tests_require,
    },
    setup_requires=setup_requires,
    test_suite='nose.collector',
    tests_require=tests_require,
    license='GPLv3+',
    platforms=['any', ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        (
            'License :: OSI Approved :: '
            'GNU General Public License v3 or later (GPLv3+)'
        ),
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
    ],
)

if __name__ == '__main__':
    setuptools.setup(**params)
