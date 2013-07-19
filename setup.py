#!/usr/bin/env python

import os
import sys

from setuptools import setup

# HACK for setup.py build, this way it can find cffi and thus make the
# extension
for path in os.listdir("."):
    if path.endswith(".egg"):
        sys.path.append(path)

try:
    from xattr import lib
except ImportError:
    ext_modules = []
else:
    ext_modules = [lib.ffi.verifier.get_extension()]


VERSION = '0.6.4'
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
    platforms=['MacOS X', 'Linux', 'FreeBSD', 'Solaris'],
    ext_modules=ext_modules,
    entry_points={
        'console_scripts': [
            "xattr = xattr.tool:main",
        ],
    },
    install_requires=["cffi"],
    setup_requires=["cffi"],
    test_suite="xattr.tests.all_tests_suite",
    zip_safe=False,
)
