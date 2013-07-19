import os
import sys

import cffi

ffi = cffi.FFI()
ffi.cdef("""
#define XATTR_NOFOLLOW ...
#define XATTR_CREATE ...
#define XATTR_REPLACE ...
#define XATTR_NOSECURITY ...
#define XATTR_MAXNAMELEN ...

ssize_t xattr_getxattr(const char *, const char *, void *, ssize_t, uint32_t, int);
ssize_t xattr_fgetxattr(int, const char *, void *, ssize_t, uint32_t, int);

ssize_t xattr_setxattr(const char *, const char *, void *, ssize_t, uint32_t, int);
ssize_t xattr_fsetxattr(int, const char *, void *, ssize_t, uint32_t, int);

ssize_t xattr_removexattr(const char *, const char *, int);
ssize_t xattr_fremovexattr(int, const char *, int);

ssize_t xattr_listxattr(const char *, char *, size_t, int);
ssize_t xattr_flistxattr(int, char *, size_t, int);

""")

lib = ffi.verify("""
#include "Python.h"
#ifdef __FreeBSD__
#include <sys/extattr.h>
#elif defined(__SUN__) || defined(__sun__) || defined(sun)
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <dirent.h>
#else
#include <sys/xattr.h>
#endif

#ifdef __FreeBSD__

/* FreeBSD compatibility API */
#define XATTR_XATTR_NOFOLLOW 0x0001
#define XATTR_XATTR_CREATE 0x0002
#define XATTR_XATTR_REPLACE 0x0004
#define XATTR_XATTR_NOSECURITY 0x0008


/* Converts a freebsd format attribute list into a NULL terminated list.
 * While the man page on extattr_list_file says it is NULL terminated,
 * it is actually the first byte that is the length of the
 * following attribute.
 */
static void convert_bsd_list(char *namebuf, size_t size)
{
    size_t offset = 0;
    while(offset < size) {
        int length = (int) namebuf[offset];
        memmove(namebuf+offset, namebuf+offset+1, length);
        namebuf[offset+length] = '\0';
        offset += length+1;
    }
}

static ssize_t xattr_getxattr(const char *path, const char *name,
                              void *value, ssize_t size, u_int32_t position,
                              int options)
{
    if (position != 0 ||
        !(options == 0 || options == XATTR_XATTR_NOFOLLOW)) {
        return -1;
    }

    if (options & XATTR_XATTR_NOFOLLOW) {
        return extattr_get_link(path, EXTATTR_NAMESPACE_USER,
                                name, value, size);
    }
    else {
        return extattr_get_file(path, EXTATTR_NAMESPACE_USER,
                                name, value, size);
    }
}

static ssize_t xattr_setxattr(const char *path, const char *name,
                              void *value, ssize_t size, u_int32_t position,
                              int options)
{
    int rv = 0;
    int nofollow;

    if (position != 0) {
        return -1;
    }

    nofollow = options & XATTR_XATTR_NOFOLLOW;
    options &= ~XATTR_XATTR_NOFOLLOW;

    if (options == XATTR_XATTR_CREATE ||
        options == XATTR_XATTR_REPLACE) {

        /* meh. FreeBSD doesn't really have this in it's
         * API... Oh well.
         */
    }
    else if (options != 0) {
        return -1;
    }

    if (nofollow) {
        rv = extattr_set_link(path, EXTATTR_NAMESPACE_USER,
                                name, value, size);
    }
    else {
        rv = extattr_set_file(path, EXTATTR_NAMESPACE_USER,
                                name, value, size);
    }

    /* freebsd returns the written length on success, not zero. */
    if (rv >= 0) {
        return 0;
    }
    else {
        return rv;
    }
}

static ssize_t xattr_removexattr(const char *path, const char *name,
                                 int options)
{
    if (!(options == 0 ||
          options == XATTR_XATTR_NOFOLLOW)) {
        return -1;
    }

    if (options & XATTR_XATTR_NOFOLLOW) {
        return extattr_delete_link(path, EXTATTR_NAMESPACE_USER, name);
    }
    else {
        return extattr_delete_file(path, EXTATTR_NAMESPACE_USER, name);
    }
}


static ssize_t xattr_listxattr(const char *path, char *namebuf,
                               size_t size, int options)
{
    ssize_t rv = 0;
    if (!(options == 0 ||
          options == XATTR_XATTR_NOFOLLOW)) {
        return -1;
    }

    if (options & XATTR_XATTR_NOFOLLOW) {
        rv = extattr_list_link(path, EXTATTR_NAMESPACE_USER, namebuf, size);
    }
    else {
        rv = extattr_list_file(path, EXTATTR_NAMESPACE_USER, namebuf, size);
    }

    if (rv > 0 && namebuf) {
        convert_bsd_list(namebuf, rv);
    }

    return rv;
}

static ssize_t xattr_fgetxattr(int fd, const char *name, void *value,
                               ssize_t size, u_int32_t position, int options)
{
    if (position != 0 ||
        !(options == 0 || options == XATTR_XATTR_NOFOLLOW)) {
        return -1;
    }

    if (options & XATTR_XATTR_NOFOLLOW) {
        return -1;
    }
    else {
        return extattr_get_fd(fd, EXTATTR_NAMESPACE_USER, name, value, size);
    }
}

static ssize_t xattr_fsetxattr(int fd, const char *name, void *value,
                               ssize_t size, u_int32_t position, int options)
{
    int rv = 0;
    int nofollow;

    if (position != 0) {
        return -1;
    }

    nofollow = options & XATTR_XATTR_NOFOLLOW;
    options &= ~XATTR_XATTR_NOFOLLOW;

    if (options == XATTR_XATTR_CREATE ||
        options == XATTR_XATTR_REPLACE) {
        /* freebsd noop */
    }
    else if (options != 0) {
        return -1;
    }

    if (nofollow) {
        return -1;
    }
    else {
        rv = extattr_set_fd(fd, EXTATTR_NAMESPACE_USER,
                            name, value, size);
    }

    /* freebsd returns the written length on success, not zero. */
    if (rv >= 0) {
        return 0;
    }
    else {
        return rv;
    }
}

static ssize_t xattr_fremovexattr(int fd, const char *name, int options)
{

    if (!(options == 0 ||
          options == XATTR_XATTR_NOFOLLOW)) {
        return -1;
    }

    if (options & XATTR_XATTR_NOFOLLOW) {
        return -1;
    }
    else {
        return extattr_delete_fd(fd, EXTATTR_NAMESPACE_USER, name);
    }
}


static ssize_t xattr_flistxattr(int fd, char *namebuf, size_t size, int options)
{
    ssize_t rv = 0;

    if (!(options == 0 ||
          options == XATTR_XATTR_NOFOLLOW)) {
        return -1;
    }

    if (options & XATTR_XATTR_NOFOLLOW) {
        return -1;
    }
    else {
        rv = extattr_list_fd(fd, EXTATTR_NAMESPACE_USER, namebuf, size);
    }

    if (rv > 0 && namebuf) {
        convert_bsd_list(namebuf, rv);
    }

    return rv;
}

#elif defined(__SUN__) || defined(__sun__) || defined(sun)

/* Solaris 9 and later compatibility API */
#define XATTR_XATTR_NOFOLLOW 0x0001
#define XATTR_XATTR_CREATE 0x0002
#define XATTR_XATTR_REPLACE 0x0004
#define XATTR_XATTR_NOSECURITY 0x0008

#ifndef u_int32_t
#define u_int32_t uint32_t
#endif

static ssize_t xattr_fgetxattr(int fd, const char *name, void *value,
                               ssize_t size, u_int32_t position, int options)
{
    int xfd;
    ssize_t bytes;
    struct stat statbuf;

    /* XXX should check that name does not have / characters in it */
    xfd = openat(fd, name, O_RDONLY | O_XATTR);
    if (xfd == -1) {
    return -1;
    }
    if (lseek(xfd, position, SEEK_SET) == -1) {
    close(xfd);
    return -1;
    }
    if (value == NULL) {
        if (fstat(xfd, &statbuf) == -1) {
        close(xfd);
        return -1;
        }
    close(xfd);
    return statbuf.st_size;
    }
    /* XXX should keep reading until the buffer is exhausted or EOF */
    bytes = read(xfd, value, size);
    close(xfd);
    return bytes;
}

static ssize_t xattr_getxattr(const char *path, const char *name,
                              void *value, ssize_t size, u_int32_t position,
                              int options)
{
    int fd;
    ssize_t bytes;

    if (position != 0 ||
        !(options == 0 || options == XATTR_XATTR_NOFOLLOW)) {
        return -1;
    }

    fd = open(path,
          O_RDONLY |
          ((options & XATTR_XATTR_NOFOLLOW) ? O_NOFOLLOW : 0));
    if (fd == -1) {
    return -1;
    }
    bytes = xattr_fgetxattr(fd, name, value, size, position, options);
    close(fd);
    return bytes;
}

static ssize_t xattr_fsetxattr(int fd, const char *name, void *value,
                               ssize_t size, u_int32_t position, int options)
{
    int xfd;
    ssize_t bytes = 0;

    /* XXX should check that name does not have / characters in it */
    xfd = openat(fd, name, O_XATTR | O_TRUNC |
         ((options & XATTR_XATTR_CREATE) ? O_EXCL : 0) |
         ((options & XATTR_XATTR_NOFOLLOW) ? O_NOFOLLOW : 0) |
         ((options & XATTR_XATTR_REPLACE) ? O_RDWR : O_WRONLY|O_CREAT),
         0644);
    if (xfd == -1) {
    return -1;
    }
    while (size > 0) {
    bytes = write(xfd, value, size);
    if (bytes == -1) {
        close(xfd);
        return -1;
    }
    size -= bytes;
    value += bytes;
    }
    close(xfd);
    return 0;
}

static ssize_t xattr_setxattr(const char *path, const char *name,
                              void *value, ssize_t size, u_int32_t position,
                              int options)
{
    int fd;
    ssize_t bytes;

    if (position != 0) {
        return -1;
    }

    fd = open(path,
          O_RDONLY | (options & XATTR_XATTR_NOFOLLOW) ? O_NOFOLLOW : 0);
    if (fd == -1) {
    return -1;
    }
    bytes = xattr_fsetxattr(fd, name, value, size, position, options);
    close(fd);
    return bytes;
}

static ssize_t xattr_fremovexattr(int fd, const char *name, int options)
{
  int xfd, status;
    /* XXX should check that name does not have / characters in it */
    if (!(options == 0 || options == XATTR_XATTR_NOFOLLOW)) {
        return -1;
    }
    if (options & XATTR_XATTR_NOFOLLOW) {
        return -1;
    }
    xfd = openat(fd, ".", O_XATTR, 0644);
    if (xfd == -1) {
    return -1;
    }
    status = unlinkat(xfd, name, 0);
    close(xfd);
    return status;
}

static ssize_t xattr_removexattr(const char *path, const char *name,
                                 int options)
{
    int fd;
    ssize_t status;

    fd = open(path,
          O_RDONLY | ((options & XATTR_XATTR_NOFOLLOW) ? O_NOFOLLOW : 0));
    if (fd == -1) {
    return -1;
    }
    status =  xattr_fremovexattr(fd, name, options);
    close(fd);
    return status;
}

static ssize_t xattr_xflistxattr(int xfd, char *namebuf, size_t size, int options)
{
    int esize;
    DIR *dirp;
    struct dirent *entry;
    ssize_t nsize = 0;

    dirp = fdopendir(xfd);
    if (dirp == NULL) {
        return (-1);
    }
    while (entry = readdir(dirp)) {
        if (strcmp(entry->d_name, ".") == 0 ||
                strcmp(entry->d_name, "..") == 0)
            continue;
        esize = strlen(entry->d_name);
        if (nsize + esize + 1 <= size) {
            snprintf((char *)(namebuf + nsize), esize + 1,
                    entry->d_name);
        }
        nsize += esize + 1; /* +1 for \0 */
    }
    closedir(dirp);
    return nsize;
}
static ssize_t xattr_flistxattr(int fd, char *namebuf, size_t size, int options)
{
    int xfd;

    xfd = openat(fd, ".", O_RDONLY);
    return xattr_xflistxattr(xfd, namebuf, size, options);
}

static ssize_t xattr_listxattr(const char *path, char *namebuf,
                               size_t size, int options)
{
    int xfd;

    xfd = attropen(path, ".", O_RDONLY);
    return xattr_xflistxattr(xfd, namebuf, size, options);
}

#elif !defined(XATTR_NOFOLLOW)
/* Linux compatibility API */
#define XATTR_XATTR_NOFOLLOW 0x0001
#define XATTR_XATTR_CREATE 0x0002
#define XATTR_XATTR_REPLACE 0x0004
#define XATTR_XATTR_NOSECURITY 0x0008
static ssize_t xattr_getxattr(const char *path, const char *name, void *value, ssize_t size, u_int32_t position, int options) {
    if (position != 0 || !(options == 0 || options == XATTR_XATTR_NOFOLLOW)) {
        return -1;
    }
    if (options & XATTR_XATTR_NOFOLLOW) {
        return lgetxattr(path, name, value, size);
    } else {
        return getxattr(path, name, value, size);
    }
}

static ssize_t xattr_setxattr(const char *path, const char *name, void *value, ssize_t size, u_int32_t position, int options) {
    int nofollow;
    if (position != 0) {
        return -1;
    }
    nofollow = options & XATTR_XATTR_NOFOLLOW;
    options &= ~XATTR_XATTR_NOFOLLOW;
    if (options == XATTR_XATTR_CREATE) {
        options = XATTR_CREATE;
    } else if (options == XATTR_XATTR_REPLACE) {
        options = XATTR_REPLACE;
    } else if (options != 0) {
        return -1;
    }
    if (nofollow) {
        return lsetxattr(path, name, value, size, options);
    } else {
        return setxattr(path, name, value, size, options);
    }
}

static ssize_t xattr_removexattr(const char *path, const char *name, int options) {
    if (!(options == 0 || options == XATTR_XATTR_NOFOLLOW)) {
        return -1;
    }
    if (options & XATTR_XATTR_NOFOLLOW) {
        return lremovexattr(path, name);
    } else {
        return removexattr(path, name);
    }
}


static ssize_t xattr_listxattr(const char *path, char *namebuf, size_t size, int options) {
    if (!(options == 0 || options == XATTR_XATTR_NOFOLLOW)) {
        return -1;
    }
    if (options & XATTR_XATTR_NOFOLLOW) {
        return llistxattr(path, namebuf, size);
    } else {
        return listxattr(path, namebuf, size);
    }
}

static ssize_t xattr_fgetxattr(int fd, const char *name, void *value, ssize_t size, u_int32_t position, int options) {
    if (position != 0 || !(options == 0 || options == XATTR_XATTR_NOFOLLOW)) {
        return -1;
    }
    if (options & XATTR_XATTR_NOFOLLOW) {
        return -1;
    } else {
        return fgetxattr(fd, name, value, size);
    }
}

static ssize_t xattr_fsetxattr(int fd, const char *name, void *value, ssize_t size, u_int32_t position, int options) {
    int nofollow;
    if (position != 0) {
        return -1;
    }
    nofollow = options & XATTR_XATTR_NOFOLLOW;
    options &= ~XATTR_XATTR_NOFOLLOW;
    if (options == XATTR_XATTR_CREATE) {
        options = XATTR_CREATE;
    } else if (options == XATTR_XATTR_REPLACE) {
        options = XATTR_REPLACE;
    } else if (options != 0) {
        return -1;
    }
    if (options & XATTR_XATTR_NOFOLLOW) {
        return -1;
    } else {
        return fsetxattr(fd, name, value, size, options);
    }
}

static ssize_t xattr_fremovexattr(int fd, const char *name, int options) {
    if (!(options == 0 || options == XATTR_XATTR_NOFOLLOW)) {
        return -1;
    }
    if (options & XATTR_XATTR_NOFOLLOW) {
        return -1;
    } else {
        return fremovexattr(fd, name);
    }
}


static ssize_t xattr_flistxattr(int fd, char *namebuf, size_t size, int options) {
    if (!(options == 0 || options == XATTR_XATTR_NOFOLLOW)) {
        return -1;
    }
    if (options & XATTR_XATTR_NOFOLLOW) {
        return -1;
    } else {
        return flistxattr(fd, namebuf, size);
    }
}

#else /* Mac OS X assumed */
#define xattr_getxattr getxattr
#define xattr_fgetxattr fgetxattr
#define xattr_removexattr removexattr
#define xattr_fremovexattr fremovexattr
#define xattr_setxattr setxattr
#define xattr_fsetxattr fsetxattr
#define xattr_listxattr listxattr
#define xattr_flistxattr flistxattr
#endif
""")

XATTR_NOFOLLOW = lib.XATTR_NOFOLLOW
XATTR_CREATE = lib.XATTR_CREATE
XATTR_REPLACE = lib.XATTR_REPLACE
XATTR_NOSECURITY = lib.XATTR_NOSECURITY
XATTR_MAXNAMELEN = lib.XATTR_MAXNAMELEN

XATTR_FINDERINFO_NAME = "com.apple.FinderInfo"
XATTR_RESOURCEFORK_NAME = "com.apple.ResourceFork"


def fs_encode(val):
    if isinstance(val, bytes):
        return val.encode(sys.getfilesystemencoding())
    else:
        return val


def error(path=None):
    errno = ffi.errno
    strerror = os.strerror(ffi.errno)
    if path:
        raise IOError(errno, strerror, path)
    else:
        raise IOError(errno, strerror)


def _getxattr(path, name, size=0, position=0, options=0):
    """
    getxattr(path, name, size=0, position=0, options=0) -> str
    """
    path = fs_encode(path)
    name = fs_encode(name)
    if size == 0:
        res = lib.xattr_getxattr(path, name, ffi.NULL, 0, position, options)
        if res == -1:
            raise error(path)
        size = res
    buf = ffi.new("char[]", size)
    res = lib.xattr_getxattr(path, name, buf, size, position, options)
    if res == -1:
        raise error(path)
    return ffi.buffer(buf)[:res]


def _fgetxattr(fd, name, size=0, position=0, options=0):
    """
    fgetxattr(fd, name, size=0, position=0, options=0) -> str
    """
    name = fs_encode(name)
    if size == 0:
        res = lib.xattr_fgetxattr(fd, name, ffi.NULL, 0, position, options)
        if res == -1:
            raise error()
        size = res
    buf = ffi.new("char[]", size)
    res = lib.xattr_fgetxattr(fd, name, buf, size, position, options)
    if res == -1:
        raise error()
    return ffi.buffer(buf)[:res]


def _setxattr(path, name, value, position=0, options=0):
    """
    setxattr(path, name, value, position=0, options=0) -> None
    """
    path = fs_encode(path)
    name = fs_encode(name)
    res = lib.xattr_setxattr(path, name, value, len(value), position, options)
    if res:
        raise error(path)


def _fsetxattr(fd, name, value, position=0, options=0):
    """
    fsetxattr(fd, name, value, position=0, options=0) -> None
    """
    name = fs_encode(name)
    res = lib.xattr_fsetxattr(fd, name, value, len(value), position, options)
    if res:
        raise error()


def _removexattr(path, name, options=0):
    """
    removexattr(path, name, options=0) -> None
    """
    path = fs_encode(path)
    name = fs_encode(name)
    res = lib.xattr_removexattr(path, name, options)
    if res:
        raise error(path)


def _fremovexattr(fd, name, options=0):
    """
    fremovexattr(fd, name, options=0) -> None
    """
    name = fs_encode(name)
    res = lib.xattr_fremovexattr(fd, name, options)
    if res:
        raise error()


def _listxattr(path, options=0):
    """
    listxattr(path, options=0) -> str
    """
    path = fs_encode(path)
    res = lib.xattr_listxattr(path, ffi.NULL, 0, options)
    if res == -1:
        raise error(path)
    elif res == 0:
        return b""
    buf = ffi.new("char[]", res)
    res = lib.xattr_listxattr(path, buf, res, options)
    if res == -1:
        raise error(path)
    return ffi.buffer(buf)[:res]


def _flistxattr(fd, options=0):
    """
    flistxattr(fd, options=0) -> str
    """
    res = lib.xattr_flistxattr(fd, ffi.NULL, 0, options)
    if res == 1:
        raise error()
    buf = ffi.new("char[]", res)
    res = lib.xattr_flistxattr(fd, buf, res, options)
    if res == -1:
        raise error()
    return ffi.buffer(buf)[:res]
