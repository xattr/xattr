import os
from unittest import TestCase
from tempfile import mkstemp, mkdtemp

import xattr

class TestFile(TestCase):
    def setUp(self):
        self.tempfh, self.tempfile = mkstemp()

    def tearDown(self):
        os.close(self.tempfh)
        os.unlink(self.tempfile)

    def testAttr(self):
        x = xattr.xattr(self.tempfile)
        self.assertEqual(x.keys(), [])
        self.assertEqual(dict(x), {})

        x['user.sopal'] = 'foo'
        x['user.sop.foo'] = 'bar'
        del x

        x = xattr.xattr(self.tempfile)
        self.assertTrue('user.sopal' in x)
        self.assertEqual(x['user.sopal'], 'foo')
        self.assertTrue('user.sop.foo' in x)
        self.assertEqual(x['user.sop.foo'], 'bar')

        del x['user.sop.foo']
        del x
        
        x = xattr.xattr(self.tempfile)
        self.assertTrue('user.sop.foo' not in x)


class TestDir(TestFile):
    def setUp(self):
        self.tempfile = mkdtemp()
    
    def tearDown(self):
        os.rmdir(self.tempfile)
