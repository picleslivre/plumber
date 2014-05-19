#!/usr/bin/env python
import sys
from setuptools import setup, Extension

import plumber

tests_require = []
PY2 = sys.version_info[0] == 2
if PY2:
    tests_require.append('mock')


setup(
    name="picles.plumber",
    version='.'.join(plumber.__version__),
    description="Simple data transformation pipeline.",
    author="Gustavo Fonseca & contributors",
    author_email="gustavo@gfonseca.net",
    license="BSD",
    url="https://github.com/picleslivre/plumber/",
    py_modules=["plumber"],
    package_data={'': ['README.md', 'LICENSE']},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ],
    tests_require=tests_require,
    test_suite='tests',
)
