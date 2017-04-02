#!/usr/bin/env python

import os
import sys

from setuptools import setup

VERSION = '0.9.2'
DESCRIPTION = "Python wrapper for extended filesystem attributes"
LONG_DESCRIPTION = """
Extended attributes extend the basic attributes of files and directories
in the file system.  They are stored as name:data pairs associated with
file system objects (files, directories, symlinks, etc).

Extended attributes are currently only available on Darwin 8.0+ (Mac OS X 10.4)
and Linux 2.6+. Experimental support is included for Solaris and FreeBSD.
"""

CLASSIFIERS = filter(bool, map(str.strip,
"""
Environment :: Console
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Natural Language :: English
Operating System :: MacOS :: MacOS X
Operating System :: POSIX :: Linux
Operating System :: POSIX :: BSD :: FreeBSD
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 3
Topic :: Software Development :: Libraries :: Python Modules
""".splitlines()))

setup(
    name="xattr",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    author="Bob Ippolito",
    author_email="bob@redivi.com",
    url="http://github.com/xattr/xattr",
    license="MIT License",
    packages=['xattr'],
    ext_package='xattr',
    platforms=['MacOS X', 'Linux', 'FreeBSD', 'Solaris'],
    entry_points={
        'console_scripts': [
            "xattr = xattr.tool:main",
        ],
    },
    install_requires=["cffi>=1.0.0"],
    setup_requires=["cffi>=1.0.0"],
    cffi_modules=["xattr/lib_build.py:ffi"],
    test_suite="xattr.tests.all_tests_suite",
    zip_safe=False,
)
