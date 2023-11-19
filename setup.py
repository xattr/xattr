#!/usr/bin/env python

from setuptools import setup

setup(
    ext_package='xattr',
    platforms=['MacOS X', 'Linux', 'FreeBSD', 'Solaris'],
    cffi_modules=["xattr/lib_build.py:ffi"],
    zip_safe=False,
)
