#!/usr/bin/env python

import distutils
from distutils.core import setup, Extension

VERSION = '0.1'
DESCRIPTION = "Python wrapper for Darwin's extended filesystem attributes"
LONG_DESCRIPTION = """
Extended attributes extend the basic attributes of files and directories
in the file system.  They are stored as name:data pairs associated with
file system objects (files, directories, symlinks, etc).

Extended attributes are currently only available on Darwin 8.0 and later.
This corresponds to Mac OS X 10.4 (Tiger).
"""

CLASSIFIERS = filter(None,
"""                 
Environment :: Console
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Natural Language :: English
Operating System :: MacOS :: MacOS X
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
""".splitlines())

setup(
    name="xattr",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    author="Bob Ippolito",
    author_email="bob@redivi.com",
    url="http://undefined.org/python/#xattr",
    license="MIT License",
    packages=['xattr'],
    platforms=['MacOS X'],
    package_dir={'xattr': 'Lib/xattr'},
    ext_modules=[
        Extension("xattr._xattr", ["Modules/xattr/_xattr.c"]),
    ],
)
