#include "Python.h"
#include <sys/xattr.h>
#ifndef XATTR_NOFOLLOW
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
    if (options & XATTR_XATTR_NOFOLLOW) {
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
        return lremovexattr(path, name, value);
    } else {
        return removexattr(path, name, value);
    }
}


static ssize_t xattr_listxattr(const char *path, const char *namebuf, size_t size, int options) {
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
        return fremovexattr(fd, name, value);
    }
}


static ssize_t xattr_flistxattr(int fd, const char *namebuf, size_t size, int options) {
    if (!(options == 0 || options == XATTR_XATTR_NOFOLLOW)) {
        return -1;
    }
    if (options & XATTR_XATTR_NOFOLLOW) {
        return -1;
    } else {
        return flistxattr(fd, namebuf, size);
    }
}

#else
#define xattr_getxattr getxattr
#define xattr_fgetxattr fgetxattr
#define xattr_removexattr removexattr
#define xattr_fremovexattr fremovexattr
#define xattr_setxattr setxattr
#define xattr_fsetxattr fsetxattr
#define xattr_listxattr listxattr
#define xattr_flistxattr flistxattr
#endif

static PyObject *xattr_error(void);
static PyObject *xattr_error_with_filename(char *name);

static PyObject *
xattr_error(void)
{
    return PyErr_SetFromErrno(PyExc_IOError);
}

static PyObject *
xattr_error_with_filename(char *name)
{
    return PyErr_SetFromErrnoWithFilename(PyExc_IOError, name);
}

PyDoc_STRVAR(pydoc_getxattr,
    "getxattr(path, name, size=0, position=0, options=0) -> str\n"
    "\n"
    "..."
);
static PyObject*
py_getxattr(PyObject* self __attribute__((__unused__)), PyObject *args) /* , PyObject *kwds) */
{
    /* static char *keywords[] = { "path", "name", "size", "position", "options", NULL }; */
    char *path;
    char *name;
    PyObject *buffer;
    int options = 0;
    size_t size = 0;
    u_int32_t position = 0;
    ssize_t res;
    if (!PyArg_ParseTuple(args, /* AndKeywords(args, kwds, */
            "etet|IIi:getxattr", /* keywords, */
            Py_FileSystemDefaultEncoding, &path,
            Py_FileSystemDefaultEncoding, &name,
            &size,
            &position,
            &options)) {
        return NULL;
    }
    if (size == 0) {
        Py_BEGIN_ALLOW_THREADS
        res = xattr_getxattr((const char *)path, (const char *)name, NULL, 0, position, options);
        Py_END_ALLOW_THREADS
        if (res == -1) {    
            return xattr_error_with_filename(path);
        }
        size = res;
    }
    buffer = PyString_FromStringAndSize((char *)NULL, size);
    if (buffer == NULL) {
        return NULL;
    }
    Py_BEGIN_ALLOW_THREADS
    res = xattr_getxattr((const char *)path, (const char *)name, (void *)PyString_AS_STRING(buffer), size, position, options);
    Py_END_ALLOW_THREADS
    if (res == -1) {
        Py_DECREF(buffer);
        return xattr_error_with_filename(path);
    }
    if (res != size) {
        _PyString_Resize(&buffer, (int)res);
    }
    return buffer;
}

PyDoc_STRVAR(pydoc_fgetxattr,
    "fgetxattr(fd, name, size=0, position=0, options=0) -> str\n"
    "\n"
    "..."
);
static PyObject*
py_fgetxattr(PyObject* self __attribute__((__unused__)), PyObject *args) /* , PyObject *kwds) */
{
    /* static char *keywords[] = { "fd", "name", "size", "position", "options", NULL }; */
    int fd;
    char *name;
    PyObject *buffer;
    int options = 0;
    size_t size = 0;
    u_int32_t position = 0;
    ssize_t res;
    if (!PyArg_ParseTuple(args, /* AndKeywords(args, kwds, */
            "iet|IIi:fgetxattr", /* keywords, */
            &fd,
            Py_FileSystemDefaultEncoding, &name,
            &size,
            &position,
            &options)) {
        return NULL;
    }
    if (size == 0) {
        Py_BEGIN_ALLOW_THREADS
        res = xattr_fgetxattr(fd, (const char *)name, NULL, 0, position, options);
        Py_END_ALLOW_THREADS
        if (res == -1) {    
            return xattr_error();
        }
        size = res;
    }
    buffer = PyString_FromStringAndSize((char *)NULL, size);
    if (buffer == NULL) {
        return NULL;
    }
    Py_BEGIN_ALLOW_THREADS
    res = xattr_fgetxattr(fd, (const char *)name, (void *)PyString_AS_STRING(buffer), size, position, options);
    Py_END_ALLOW_THREADS
    if (res == -1) {
        Py_DECREF(buffer);
        return xattr_error();
    }
    if (res != size) {
        _PyString_Resize(&buffer, (int)res);
    }
    return buffer;
}

PyDoc_STRVAR(pydoc_setxattr,
    "setxattr(path, name, value, position=0, options=0) -> None\n"
    "\n"
    "..."
);
static PyObject*
py_setxattr(PyObject* self __attribute__((__unused__)), PyObject *args) /* , PyObject *kwds) */
{
    /* static char *keywords[] = { "path", "name", "value", "position", "options", NULL }; */
    char *path;
    char *name;
    int options = 0;
    char *value;
    int size;
    u_int32_t position = 0;
    int res;
    if (!PyArg_ParseTuple(args, /* AndKeywords(args, kwds, */
            "etets#|Ii:setxattr", /* keywords, */
            Py_FileSystemDefaultEncoding, &path,
            Py_FileSystemDefaultEncoding, &name,
            &value, &size,
            &position,
            &options)) {
        return NULL;
    }
    Py_BEGIN_ALLOW_THREADS
    res = xattr_setxattr((const char *)path, (const char *)name, (void *)value, size, position, options);
    Py_END_ALLOW_THREADS
    if (res) {
        return xattr_error_with_filename(path);
    }
    Py_INCREF(Py_None);
    return Py_None;
}

PyDoc_STRVAR(pydoc_fsetxattr,
    "fsetxattr(fd, name, value, position=0, options=0) -> None\n"
    "\n"
    "..."
);
static PyObject*
py_fsetxattr(PyObject* self __attribute__((__unused__)), PyObject *args) /* , PyObject *kwds) */
{
    /* static char *keywords[] = { "fd", "name", "value", "position", "options", NULL }; */
    int fd;
    char *name;
    int options = 0;
    char *value;
    int size;
    u_int32_t position = 0;
    int res;
    if (!PyArg_ParseTuple(args, /* AndKeywords(args, kwds, */
            "iets#|Ii:fsetxattr", /* keywords, */
            &fd,
            Py_FileSystemDefaultEncoding, &name,
            &value, &size,
            &position,
            &options)) {
        return NULL;
    }
    Py_BEGIN_ALLOW_THREADS
    res = xattr_fsetxattr(fd, (const char *)name, (void *)value, size, position, options);
    Py_END_ALLOW_THREADS
    if (res) {
        return xattr_error();
    }
    Py_INCREF(Py_None);
    return Py_None;
}

PyDoc_STRVAR(pydoc_removexattr,
    "removexattr(path, name, options=0) -> None\n"
    "\n"
    "..."
);
static PyObject*
py_removexattr(PyObject* self __attribute__((__unused__)), PyObject *args) /* , PyObject *kwds) */
{
    /* static char *keywords[] = { "path", "name", "options", NULL }; */
    char *path;
    char *name;
    int options = 0;
    int res;
    if (!PyArg_ParseTuple(args, /* AndKeywords(args, kwds, */
            "etet|i:removexattr", /* keywords, */
            Py_FileSystemDefaultEncoding, &path,
            Py_FileSystemDefaultEncoding, &name,
            &options)) {
        return NULL;
    }
    Py_BEGIN_ALLOW_THREADS
    res = xattr_removexattr((const char *)path, (const char *)name, options);
    Py_END_ALLOW_THREADS
    if (res) {
        return xattr_error_with_filename(path);
    }
    Py_INCREF(Py_None);
    return Py_None;
}

PyDoc_STRVAR(pydoc_fremovexattr,
    "fremovexattr(fd, name, options=0) -> None\n"
    "\n"
    "..."
);
static PyObject*
py_fremovexattr(PyObject* self __attribute__((__unused__)), PyObject *args) /* , PyObject *kwds) */
{
    /* static char *keywords[] = { "fd", "name", "options", NULL }; */
    int fd;
    char *name;
    int options = 0;
    int res;
    if (!PyArg_ParseTuple(args, /* AndKeywords(args, kwds, */
            "iet|i:fremovexattr", /* keywords, */
            &fd,
            Py_FileSystemDefaultEncoding, &name,
            &options)) {
        return NULL;
    }
    Py_BEGIN_ALLOW_THREADS
    res = xattr_fremovexattr(fd, (const char *)name, options);
    Py_END_ALLOW_THREADS
    if (res) {
        return xattr_error();
    }
    Py_INCREF(Py_None);
    return Py_None;
}

PyDoc_STRVAR(pydoc_listxattr,
    "listxattr(path, options=0) -> str\n"
    "\n"
    "..."
);
static PyObject*
py_listxattr(PyObject* self __attribute__((__unused__)), PyObject *args) /* , PyObject *kwds) */
{
    /* static char *keywords[] = { "path", "options", NULL }; */
    PyObject *buffer;
    char *path;
    int options = 0;
    ssize_t res;
    if (!PyArg_ParseTuple(args, /* AndKeywords(args, kwds, */
            "et|i:listxattr", /* keywords, */
            Py_FileSystemDefaultEncoding, &path,
            &options)) {
        return NULL;
    }
    Py_BEGIN_ALLOW_THREADS
    res = xattr_listxattr((const char *)path, NULL, 0, options);
    Py_END_ALLOW_THREADS
    if (res == -1) {    
        return xattr_error_with_filename(path);
    }
    buffer = PyString_FromStringAndSize((char *)NULL, (int)res);
    if (buffer == NULL) {
        return NULL;
    }
    Py_BEGIN_ALLOW_THREADS
    res = xattr_listxattr((const char *)path, (void *)PyString_AS_STRING(buffer), (size_t)PyString_GET_SIZE(buffer), options);
    Py_END_ALLOW_THREADS
    if (res == -1) {
        Py_DECREF(buffer);
        return xattr_error_with_filename(path);
    }
    if (res != (ssize_t)PyString_GET_SIZE(buffer)) {
        _PyString_Resize(&buffer, (int)res);
    }
    return buffer;
}

PyDoc_STRVAR(pydoc_flistxattr,
    "flistxattr(fd, options=0) -> str\n"
    "\n"
    "..."
);
static PyObject*
py_flistxattr(PyObject* self __attribute__((__unused__)), PyObject *args) /* , PyObject *kwds) */
{
    /* static char *keywords[] = { "fd", "options", NULL }; */
    PyObject *buffer;
    int fd;
    int options = 0;
    ssize_t res;
    if (!PyArg_ParseTuple(args, /* AndKeywords(args, kwds, */
            "i|i:flistxattr", /* keywords, */
            &fd,
            &options)) {
        return NULL;
    }
    Py_BEGIN_ALLOW_THREADS
    res = xattr_flistxattr(fd, NULL, 0, options);
    Py_END_ALLOW_THREADS
    if (res == -1) {    
        return xattr_error();
    }
    buffer = PyString_FromStringAndSize((char *)NULL, (int)res);
    if (buffer == NULL) {
        return NULL;
    }
    Py_BEGIN_ALLOW_THREADS
    res = xattr_flistxattr(fd, (void *)PyString_AS_STRING(buffer), (size_t)PyString_GET_SIZE(buffer), options);
    Py_END_ALLOW_THREADS
    if (res == -1) {
        Py_DECREF(buffer);
        return xattr_error();
    }
    if (res != (ssize_t)PyString_GET_SIZE(buffer)) {
        _PyString_Resize(&buffer, (int)res);
    }
    return buffer;
}


#define DEFN(n) \
    {  \
        #n, \
        (PyCFunction)py_ ##n, \
        METH_VARARGS /* | METH_KEYWORDS */, \
        pydoc_ ##n \
    }
static PyMethodDef xattr_methods[] = {
    DEFN(getxattr),
    DEFN(fgetxattr),
    DEFN(setxattr),
    DEFN(fsetxattr),
    DEFN(removexattr),
    DEFN(fremovexattr),
    DEFN(listxattr),
    DEFN(flistxattr),
    {}
};
#undef DEFN

void init_xattr(void);

void
init_xattr(void)
{
    PyObject *m;
    m = Py_InitModule4("_xattr", xattr_methods, NULL, NULL, PYTHON_API_VERSION);
}
