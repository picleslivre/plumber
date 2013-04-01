#!/usr/bin/env python
import plumber
try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension


setup(
    name="plumber",
    version='.'.join(plumber.__version__),
    description="Simple data transformation pipeline.",
    author="Gustavo Fonseca",
    author_email="gustavofons@gmail.com",
    license="BSD",
    url="http://docs.scielo.org",
    py_modules=["plumber"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
