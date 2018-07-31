/**
 * FreeBSD compatibility API.
 */

#include "Python.h"
#include <sys/types.h>
#include <sys/extattr.h>

#define XATTR_XATTR_NOFOLLOW    0x0001
#define XATTR_XATTR_CREATE      0x0002
#define XATTR_XATTR_REPLACE     0x0004
#define XATTR_XATTR_NOSECURITY  0x0008
#define XATTR_CREATE            0x1
#define XATTR_REPLACE           0x2

/* Converts a FreeBSD format attribute list into a NULL terminated list.
 * The first byte is the length of the following attribute.
 */
static void convert_bsd_list(char *namebuf, size_t size) {
    size_t offset = 0;
    while (offset < size) {
        int length = (int) (unsigned char) namebuf[offset];
        memmove(namebuf + offset, namebuf + offset + 1, length);
        namebuf[offset + length] = '\0';
        offset += length + 1;
    }
}

static ssize_t xattr_getxattr(const char *path, const char *name,
                              void *value, ssize_t size, u_int32_t position,
                              int options) {
    if (position != 0 ||
        !(options == 0 || options == XATTR_XATTR_NOFOLLOW)) {
        return -1;
    }

    if (options & XATTR_XATTR_NOFOLLOW) {
        return extattr_get_link(path, EXTATTR_NAMESPACE_USER,
                                name, value, size);
    } else {
        return extattr_get_file(path, EXTATTR_NAMESPACE_USER,
                                name, value, size);
    }
}

static ssize_t xattr_setxattr(const char *path, const char *name,
                              void *value, ssize_t size, u_int32_t position,
                              int options) {
    int rv = 0;
    int nofollow;

    if (position != 0) {
        return -1;
    }

    nofollow = options & XATTR_XATTR_NOFOLLOW;
    options &= ~XATTR_XATTR_NOFOLLOW;

    if (options == XATTR_XATTR_CREATE ||
        options == XATTR_XATTR_REPLACE) {

        /* meh. FreeBSD doesn't really have this in its
         * API... Oh well.
         */
    } else if (options != 0) {
        return -1;
    }

    if (nofollow) {
        rv = extattr_set_link(path, EXTATTR_NAMESPACE_USER,
                              name, value, size);
    } else {
        rv = extattr_set_file(path, EXTATTR_NAMESPACE_USER,
                              name, value, size);
    }

    /* freebsd returns the written length on success, not zero. */
    if (rv >= 0) {
        return 0;
    } else {
        return rv;
    }
}

static ssize_t xattr_removexattr(const char *path, const char *name,
                                 int options) {
    if (!(options == 0 ||
          options == XATTR_XATTR_NOFOLLOW)) {
        return -1;
    }

    if (options & XATTR_XATTR_NOFOLLOW) {
        return extattr_delete_link(path, EXTATTR_NAMESPACE_USER, name);
    } else {
        return extattr_delete_file(path, EXTATTR_NAMESPACE_USER, name);
    }
}

static ssize_t xattr_listxattr(const char *path, char *namebuf,
                               size_t size, int options) {
    ssize_t rv = 0;
    if (!(options == 0 ||
          options == XATTR_XATTR_NOFOLLOW)) {
        return -1;
    }

    if (options & XATTR_XATTR_NOFOLLOW) {
        rv = extattr_list_link(path, EXTATTR_NAMESPACE_USER, namebuf, size);
    } else {
        rv = extattr_list_file(path, EXTATTR_NAMESPACE_USER, namebuf, size);
    }

    if (rv > 0 && namebuf) {
        convert_bsd_list(namebuf, rv);
    }

    return rv;
}

static ssize_t xattr_fgetxattr(int fd, const char *name, void *value,
                               ssize_t size, u_int32_t position, int options) {
    if (position != 0 ||
        !(options == 0 || options == XATTR_XATTR_NOFOLLOW)) {
        return -1;
    }

    if (options & XATTR_XATTR_NOFOLLOW) {
        return -1;
    } else {
        return extattr_get_fd(fd, EXTATTR_NAMESPACE_USER, name, value, size);
    }
}

static ssize_t xattr_fsetxattr(int fd, const char *name, void *value,
                               ssize_t size, u_int32_t position, int options) {
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
    } else if (options != 0) {
        return -1;
    }

    if (nofollow) {
        return -1;
    } else {
        rv = extattr_set_fd(fd, EXTATTR_NAMESPACE_USER,
                            name, value, size);
    }

    /* freebsd returns the written length on success, not zero. */
    if (rv >= 0) {
        return 0;
    } else {
        return rv;
    }
}

static ssize_t xattr_fremovexattr(int fd, const char *name, int options) {

    if (!(options == 0 ||
          options == XATTR_XATTR_NOFOLLOW)) {
        return -1;
    }

    if (options & XATTR_XATTR_NOFOLLOW) {
        return -1;
    } else {
        return extattr_delete_fd(fd, EXTATTR_NAMESPACE_USER, name);
    }
}


static ssize_t
xattr_flistxattr(int fd, char *namebuf, size_t size, int options) {
    ssize_t rv = 0;

    if (!(options == 0 ||
          options == XATTR_XATTR_NOFOLLOW)) {
        return -1;
    }

    if (options & XATTR_XATTR_NOFOLLOW) {
        return -1;
    } else {
        rv = extattr_list_fd(fd, EXTATTR_NAMESPACE_USER, namebuf, size);
    }

    if (rv > 0 && namebuf) {
        convert_bsd_list(namebuf, rv);
    }

    return rv;
}

#ifndef XATTR_MAXNAMELEN
#define XATTR_MAXNAMELEN 127
#endif
