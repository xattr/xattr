xattr
-----

xattr is a Python wrapper for extended filesystem attributes.

xattr also ships with an `xattr` command line tool for viewing and
editing extended filesystem attributes. On platforms that support or
ship with the attr package, you may prefer to use the `getfattr`
and `setfattr` command line tools from the attr package.

Extended attributes extend the basic attributes of files and directories
in the file system.  They are stored as name:data pairs associated with
file system objects (files, directories, symlinks, etc).

Extended attributes are currently only available on Darwin 8.0+ (Mac OS X 10.4)
and Linux 2.6+. Experimental support is included for Solaris and FreeBSD.

Python 3.8+ is required as of v1.0.0, and this is the minimum version
that is compatible with Python 3.12+.

Versions older than v1.0.0 are no longer supported, but are
available for use. v0.10.1 is the last version to support older versions
of Python (including 2.7).

Note: On Linux, custom xattr keys need to be prefixed with the `user`
namespace, ie: `user.your_attr`.

Note: If you need to read or write Spotlight metadata attributes on macOS,
see osxmetadata_ which provides a native macOS means to do so without
directly manipulating extended attributes. osxmetadata also provides access
to other macOS metadata attributes and extended attributes via xattr.

.. _osxmetadata: https://github.com/RhetTbull/osxmetadata
