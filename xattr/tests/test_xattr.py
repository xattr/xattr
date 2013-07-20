import os
from unittest import TestCase
from tempfile import mkdtemp, NamedTemporaryFile

import xattr


class BaseTestXattr(object):
    def test_attr(self):
        x = xattr.xattr(self.tempfile)
        self.assertEqual(x.keys(), [])
        self.assertEqual(dict(x), {})

        x['user.sopal'] = b'foo'
        x['user.sop.foo'] = b'bar'
        del x

        x = xattr.xattr(self.tempfile)
        self.assertTrue('user.sopal' in x)
        self.assertEqual(x['user.sopal'], b'foo')
        self.assertTrue('user.sop.foo' in x)
        self.assertEqual(x['user.sop.foo'], b'bar')

        del x['user.sop.foo']
        del x

        x = xattr.xattr(self.tempfile)
        self.assertTrue('user.sop.foo' not in x)

    def test_symlink_attrs(self):
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
