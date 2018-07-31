/**
 * Solaris 9 and later compatibility API.
 */

#include "Python.h"
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <dirent.h>
#include <alloca.h>

#define XATTR_XATTR_NOFOLLOW    0x0001
#define XATTR_XATTR_CREATE      0x0002
#define XATTR_XATTR_REPLACE     0x0004
#define XATTR_XATTR_NOSECURITY  0x0008
#define XATTR_CREATE            0x1
#define XATTR_REPLACE           0x2

// TODO Determine if this definition is still required.
// This may now be redundant due to the inclusion of `sys/types.h`.
#ifndef u_int32_t
#define u_int32_t uint32_t
#endif

static ssize_t xattr_fgetxattr(int fd, const char *name, void *value,
                               ssize_t size, u_int32_t position, int options) {
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
                              int options) {
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
                               ssize_t size, u_int32_t position, int options) {
    int xfd;
    ssize_t bytes = 0;

    /* XXX should check that name does not have / characters in it */
    xfd = openat(fd, name, O_XATTR | O_TRUNC |
                           ((options & XATTR_XATTR_CREATE) ? O_EXCL : 0) |
                           ((options & XATTR_XATTR_NOFOLLOW) ? O_NOFOLLOW : 0) |
                           ((options & XATTR_XATTR_REPLACE) ? O_RDWR :
                            O_WRONLY | O_CREAT),
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
                              int options) {
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

static ssize_t xattr_fremovexattr(int fd, const char *name, int options) {
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
                                 int options) {
    int fd;
    ssize_t status;

    fd = open(path,
              O_RDONLY | ((options & XATTR_XATTR_NOFOLLOW) ? O_NOFOLLOW : 0));
    if (fd == -1) {
        return -1;
    }
    status = xattr_fremovexattr(fd, name, options);
    close(fd);
    return status;
}

static ssize_t
xattr_xflistxattr(int xfd, char *namebuf, size_t size, int options) {
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
            snprintf((char *) (namebuf + nsize), esize + 1,
                     entry->d_name);
        }
        nsize += esize + 1; /* +1 for \0 */
    }
    closedir(dirp);
    return nsize;
}

static ssize_t
xattr_flistxattr(int fd, char *namebuf, size_t size, int options) {
    int xfd;

    xfd = openat(fd, ".", O_RDONLY | O_XATTR);
    return xattr_xflistxattr(xfd, namebuf, size, options);
}

static ssize_t xattr_listxattr(const char *path, char *namebuf,
                               size_t size, int options) {
    int xfd;

    xfd = attropen(path, ".", O_RDONLY);
    return xattr_xflistxattr(xfd, namebuf, size, options);
}

#ifndef XATTR_MAXNAMELEN
#define XATTR_MAXNAMELEN 127
#endif
