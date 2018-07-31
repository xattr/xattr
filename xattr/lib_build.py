import sys
import os
from cffi import FFI

platforms = {
    'linux': 'xattr_linux.c',
    'darwin': 'xattr_darwin.c',
    'freebsd': 'xattr_freebsd.c',
    'sunos': 'xattr_sunos.c'
}

source_file = None
sys_platform = sys.platform.lower()
for platform in platforms:
    if platform in sys_platform:
        source_file = platforms[platform]
if not source_file:
    print('Error: Platform `%s` is not supported.' % sys_platform)
    sys.exit(1)

source_dir = os.path.join(os.path.dirname(__file__), 'lib_src')
with open(os.path.join(source_dir, 'xattr.h')) as hf:
    c_header = hf.read()
with open(os.path.join(source_dir, source_file)) as cf:
    c_source = cf.read()

ffi = FFI()
ffi.cdef(c_header)
ffi.set_source('_lib', c_source)

if __name__ == '__main__':
    ffi.compile()
