#define XATTR_XATTR_NOFOLLOW ...
#define XATTR_XATTR_CREATE ...
#define XATTR_XATTR_REPLACE ...
#define XATTR_XATTR_NOSECURITY ...
#define XATTR_MAXNAMELEN ...

ssize_t xattr_getxattr(const char *, const char *, void *, ssize_t, uint32_t, int);
ssize_t xattr_fgetxattr(int, const char *, void *, ssize_t, uint32_t, int);

ssize_t xattr_setxattr(const char *, const char *, void *, ssize_t, uint32_t, int);
ssize_t xattr_fsetxattr(int, const char *, void *, ssize_t, uint32_t, int);

ssize_t xattr_removexattr(const char *, const char *, int);
ssize_t xattr_fremovexattr(int, const char *, int);

ssize_t xattr_listxattr(const char *, char *, size_t, int);
ssize_t xattr_flistxattr(int, char *, size_t, int);
