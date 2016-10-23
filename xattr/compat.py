"""Python 3 compatibility shims
"""
import sys
if sys.version_info[0] < 3:
    integer_types = (int, long)
    text_type = unicode
    binary_type = str
else:
    integer_types = (int,)
    text_type = str
    binary_type = bytes
