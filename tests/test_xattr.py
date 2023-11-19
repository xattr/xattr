import os
import sys
import unittest
from unittest import TestCase
from tempfile import mkdtemp, NamedTemporaryFile

import xattr


class BaseTestXattr(object):
    # TESTDIR for temporary files usually defaults to "/tmp",
    # which may not have XATTR support (e.g. tmpfs);
    # manual override here.
    TESTDIR = None

    def test_update(self):
        x = xattr.xattr(self.tempfile)
        attrs = {
            'user.test.key1': b'test_value1',
            'user.test.key2': b'test_value2'
        }
        x.update(attrs)
        for k, v in attrs.items():
            self.assertEqual(x[k], v)

    def test_attr(self):
        x = xattr.xattr(self.tempfile)

        # Solaris 11 and forward contain system attributes (file flags) in
        # extended attributes present on all files, so cons them up into a
        # comparison dict.
        d = {}
        if sys.platform == 'sunos5' and 'SUNWattr_ro' in x:
            d['SUNWattr_ro'] = x['SUNWattr_ro']
            d['SUNWattr_rw'] = x['SUNWattr_rw']

        # SELinux systems use an attribute which must be accounted for
        if sys.platform.startswith('linux') and 'security.selinux' in x:
            d['security.selinux'] = x['security.selinux']

        self.assertEqual(list(x.keys()), list(d.keys()))
        self.assertEqual(list(x.list()), list(d.keys()))
        self.assertEqual(dict(x), d)

        x['user.sopal'] = b'foo'
        x['user.sop.foo'] = b'bar'
        x[u'user.\N{SNOWMAN}'] = b'not a snowman'
        del x

        x = xattr.xattr(self.tempfile)
        attrs = set(x.list())
        self.assertTrue('user.sopal' in x)
        self.assertTrue(u'user.sopal' in attrs)
        self.assertEqual(x['user.sopal'], b'foo')
        self.assertTrue('user.sop.foo' in x)
        self.assertTrue(u'user.sop.foo' in attrs)
        self.assertEqual(x['user.sop.foo'], b'bar')
        self.assertTrue(u'user.\N{SNOWMAN}' in x)
        self.assertTrue(u'user.\N{SNOWMAN}' in attrs)
        self.assertEqual(x[u'user.\N{SNOWMAN}'],
                         b'not a snowman')

        del x[u'user.\N{SNOWMAN}']
        del x['user.sop.foo']
        del x

        x = xattr.xattr(self.tempfile)
        self.assertTrue('user.sop.foo' not in x)

    def test_setxattr_unicode_error(self):
        x = xattr.xattr(self.tempfile)
        def assign():
            x['abc'] = u'abc'
        self.assertRaises(TypeError, assign)

        msg = "Value must be bytes, str was passed."

        try:
            assign()
        except TypeError:
            e = sys.exc_info()[1]
            self.assertEqual(str(e), msg)

    def test_symlink_attrs(self):
        symlinkPath = self.tempfilename + '.link'
        os.symlink(self.tempfilename, symlinkPath)
        try:
            symlink = xattr.xattr(symlinkPath, options=xattr.XATTR_NOFOLLOW)
            realfile = xattr.xattr(self.tempfilename)
            try:
                symlink['user.islink'] = b'true'
            except IOError:
                # Solaris, Linux don't support extended attributes on symlinks
                raise unittest.SkipTest("XATTRs on symlink not allowed"
                                        " on filesystem/platform")
            self.assertEqual(dict(realfile), {})
            self.assertEqual(symlink['user.islink'], b'true')
        finally:
            os.remove(symlinkPath)


class TestFile(TestCase, BaseTestXattr):
    def setUp(self):
        self.tempfile = NamedTemporaryFile(dir=self.TESTDIR)
        self.tempfilename = self.tempfile.name

    def tearDown(self):
        self.tempfile.close()


class TestDir(TestCase, BaseTestXattr):
    def setUp(self):
        self.tempfile = mkdtemp(dir=self.TESTDIR)
        self.tempfilename = self.tempfile

    def tearDown(self):
        os.rmdir(self.tempfile)


class TestFileWithSurrogates(TestFile):
    def setUp(self):
        if sys.platform not in ('linux', 'linux2'):
            raise unittest.SkipTest('Files with invalid encoded names are only supported under linux')
        self.tempfile = NamedTemporaryFile(prefix=b'invalid-\xe9'.decode('utf8','surrogateescape'), dir=self.TESTDIR)
        self.tempfilename = self.tempfile.name
