/**
 * OSX compatibility API.
 */

#include "Python.h"
#include <sys/types.h>
#include <sys/xattr.h>

#define xattr_getxattr      getxattr
#define xattr_fgetxattr     fgetxattr
#define xattr_removexattr   removexattr
#define xattr_fremovexattr  fremovexattr
#define xattr_setxattr      setxattr
#define xattr_fsetxattr     fsetxattr
#define xattr_listxattr     listxattr
#define xattr_flistxattr    flistxattr

/* define these for use in python (see below) */
#define XATTR_XATTR_NOFOLLOW    XATTR_NOFOLLOW
#define XATTR_XATTR_CREATE      XATTR_CREATE
#define XATTR_XATTR_REPLACE     XATTR_REPLACE
#define XATTR_XATTR_NOSECURITY  XATTR_NOSECURITY

#ifndef XATTR_MAXNAMELEN
#define XATTR_MAXNAMELEN 127
#endif
