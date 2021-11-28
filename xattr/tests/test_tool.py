import contextlib
import errno
import io
import os
import shutil
import sys
import tempfile
import unittest
import uuid

import xattr
import xattr.tool


class TestTool(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

        orig_stdout = sys.stdout

        def unpatch_stdout(sys=sys, orig_stdout=orig_stdout):
            sys.stdout = orig_stdout

        self.addCleanup(unpatch_stdout)
        sys.stdout = self.mock_stdout = io.StringIO()

    def getoutput(self):
        value = self.mock_stdout.getvalue()
        self.mock_stdout.seek(0)
        self.mock_stdout.truncate(0)
        return value

    @contextlib.contextmanager
    def temp_file(self):
        test_file = os.path.join(self.test_dir, str(uuid.uuid4()))
        fd = os.open(test_file, os.O_CREAT | os.O_WRONLY)
        try:
            yield test_file, fd
        finally:
            os.close(fd)

    def set_xattr(self, fd, name, value):
        try:
            xattr.setxattr(fd, name, value)
        except OSError as e:
            if e.errno == errno.ENOTSUP:
                raise unittest.SkipTest('xattrs are not supported')
            raise

    def test_utf8(self):
        with self.temp_file() as (file_path, fd):
            self.set_xattr(fd, 'user.test-utf8',
                           u'\N{SNOWMAN}'.encode('utf8'))
            self.set_xattr(fd, 'user.test-utf8-and-nul',
                           u'\N{SNOWMAN}\0'.encode('utf8'))

        xattr.tool.main(['prog', '-p', 'user.test-utf8', file_path])
        self.assertEqual(u'\N{SNOWMAN}\n', self.getoutput())

        xattr.tool.main(['prog', '-p', 'user.test-utf8-and-nul', file_path])
        self.assertEqual(u'''
0000   E2 98 83 00                                        ....

'''.lstrip(), self.getoutput())

        xattr.tool.main(['prog', '-l', file_path])
        output = self.getoutput()
        self.assertIn(u'user.test-utf8: \N{SNOWMAN}\n', output)
        self.assertIn(u'''
user.test-utf8-and-nul:
0000   E2 98 83 00                                        ....

'''.lstrip(), output)

    def test_non_utf8(self):
        with self.temp_file() as (file_path, fd):
            self.set_xattr(fd, 'user.test-not-utf8', b'cannot\xffdecode')

        xattr.tool.main(['prog', '-p', 'user.test-not-utf8', file_path])
        self.assertEqual(u'''
0000   63 61 6E 6E 6F 74 FF 64 65 63 6F 64 65             cannot.decode

'''.lstrip(), self.getoutput())

        xattr.tool.main(['prog', '-l', file_path])
        self.assertIn(u'''
user.test-not-utf8:
0000   63 61 6E 6E 6F 74 FF 64 65 63 6F 64 65             cannot.decode

'''.lstrip(), self.getoutput())

    def test_nul(self):
        with self.temp_file() as (file_path, fd):
            self.set_xattr(fd, 'user.test', b'foo\0bar')
            self.set_xattr(fd, 'user.test-long',
                           b'some rather long value with\0nul\0chars in it')

        xattr.tool.main(['prog', '-p', 'user.test', file_path])
        self.assertEqual(u'''
0000   66 6F 6F 00 62 61 72                               foo.bar

'''.lstrip(), self.getoutput())

        xattr.tool.main(['prog', '-p', 'user.test-long', file_path])
        self.assertEqual(u'''
0000   73 6F 6D 65 20 72 61 74 68 65 72 20 6C 6F 6E 67    some rather long
0010   20 76 61 6C 75 65 20 77 69 74 68 00 6E 75 6C 00     value with.nul.
0020   63 68 61 72 73 20 69 6E 20 69 74                   chars in it

'''.lstrip(), self.getoutput())

        xattr.tool.main(['prog', '-l', file_path])
        self.assertIn(u'''
0000   66 6F 6F 00 62 61 72                               foo.bar

'''.lstrip(), self.getoutput())
