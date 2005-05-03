#include "Python.h"
#include <sys/xattr.h>

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
        res = getxattr((const char *)path, (const char *)name, NULL, 0, position, options);
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
    res = getxattr((const char *)path, (const char *)name, (void *)PyString_AS_STRING(buffer), size, position, options);
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
        res = fgetxattr(fd, (const char *)name, NULL, 0, position, options);
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
    res = fgetxattr(fd, (const char *)name, (void *)PyString_AS_STRING(buffer), size, position, options);
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
    res = setxattr((const char *)path, (const char *)name, (void *)value, size, position, options);
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
    res = fsetxattr(fd, (const char *)name, (void *)value, size, position, options);
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
    res = removexattr((const char *)path, (const char *)name, options);
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
    res = fremovexattr(fd, (const char *)name, options);
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
    res = listxattr((const char *)path, NULL, 0, options);
    Py_END_ALLOW_THREADS
    if (res == -1) {    
        return xattr_error_with_filename(path);
    }
    buffer = PyString_FromStringAndSize((char *)NULL, (int)res);
    if (buffer == NULL) {
        return NULL;
    }
    Py_BEGIN_ALLOW_THREADS
    res = listxattr((const char *)path, (void *)PyString_AS_STRING(buffer), (size_t)PyString_GET_SIZE(buffer), options);
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
    res = flistxattr(fd, NULL, 0, options);
    Py_END_ALLOW_THREADS
    if (res == -1) {    
        return xattr_error();
    }
    buffer = PyString_FromStringAndSize((char *)NULL, (int)res);
    if (buffer == NULL) {
        return NULL;
    }
    Py_BEGIN_ALLOW_THREADS
    res = flistxattr(fd, (void *)PyString_AS_STRING(buffer), (size_t)PyString_GET_SIZE(buffer), options);
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
