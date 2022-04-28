xattr
-----

.. image:: https://travis-ci.org/xattr/xattr.svg?branch=master
    :target: https://travis-ci.org/xattr/xattr

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

Note: On Linux, custom xattr keys need to be prefixed with the `user`
namespace, ie: `user.your_attr`.
