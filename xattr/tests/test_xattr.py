import os
import sys
from unittest import TestCase
from tempfile import mkdtemp, NamedTemporaryFile

import xattr


class BaseTestXattr(object):
    def test_attr(self):
        x = xattr.xattr(self.tempfile)

        # Solaris 11 and forward contain system attributes (file flags) in
        # extended attributes present on all files, so cons them up into a
        # comparison dict.
        d = {}
        if sys.platform == 'sunos5' and 'SUNWattr_ro' in x:
            d['SUNWattr_ro'] = x['SUNWattr_ro']
            d['SUNWattr_rw'] = x['SUNWattr_rw']

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

        if sys.version_info[0] >= 3:
            msg = "Value must be bytes, str was passed."
        else:
            msg = "Value must be bytes, unicode was passed."

        try:
            assign()
        except TypeError:
            e = sys.exc_info()[1]
            self.assertEqual(str(e), msg)

    def test_symlink_attrs(self):
        # Solaris doesn't support extended attributes on symlinks
        if sys.platform == 'sunos5':
            return
        symlinkPath = self.tempfilename + '.link'
        os.symlink(self.tempfilename, symlinkPath)
        try:
            symlink = xattr.xattr(symlinkPath, options=xattr.XATTR_NOFOLLOW)
            realfile = xattr.xattr(self.tempfilename)
            symlink['user.islink'] = b'true'
            self.assertEqual(dict(realfile), {})
            self.assertEqual(symlink['user.islink'], b'true')
        finally:
            os.remove(symlinkPath)
    
    def test_bad_name_prefix(self):
        xfile = xattr.xattr(self.tempfile)
        xfile['testing'] = b'fail'
        self.assertEqual('testing' not in xfile)

    def test_good_name_prefix(self):
        xfile = xattr.xattr(self.tempfile)
        xfile['user.testing'] = b'pass'
        self.assertEqual('user.testing' in xfile)


class TestFile(TestCase, BaseTestXattr):
    def setUp(self):
        self.tempfile = NamedTemporaryFile()
        self.tempfilename = self.tempfile.name

    def tearDown(self):
        self.tempfile.close()


class TestDir(TestCase, BaseTestXattr):
    def setUp(self):
        self.tempfile = mkdtemp()
        self.tempfilename = self.tempfile

    def tearDown(self):
        os.rmdir(self.tempfile)
