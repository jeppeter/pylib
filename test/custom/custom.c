#include <Python.h>
#include "structmember.h"

typedef struct {
    PyObject_HEAD
    PyObject *first; /* first name */
    PyObject *last;  /* last name */
    PyObject *callback;
    PyObject *args;
    int gpio;
    int number;
} CustomObject;

static PyTypeObject CustomType;

static void
Custom_dealloc(CustomObject *self)
{
    Py_XDECREF(self->first);
    Py_XDECREF(self->last);
    Py_XDECREF(self->callback);
    Py_XDECREF(self->args);
    puts("deallocating weird pointer");
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyObject *
Custom_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    CustomObject *self;
    //self = (CustomObject *) type->tp_alloc(type, 0);
    self = PyObject_New(CustomObject, &CustomType);
    if (self != NULL) {
        self->first = NULL;
        self->last = NULL;
        self->callback = NULL;
        self->args = NULL;
        self->number = 0;

        self->first = PyUnicode_FromString("");
        if (self->first == NULL) {
            Py_DECREF(self);
            return NULL;
        }
        self->last = PyUnicode_FromString("");
        if (self->last == NULL) {
            Py_DECREF(self);
            return NULL;
        }
        self->number = 0;
    }
    return (PyObject *) self;
}

static int
Custom_init(CustomObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"first", "last", "number", NULL};
    PyObject *first = NULL, *last = NULL, *tmp;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|OOi", kwlist,
                                     &first, &last,
                                     &self->number))
        return -1;

    if (first) {
        tmp = self->first;
        Py_INCREF(first);
        self->first = first;
        Py_XDECREF(tmp);
    }
    if (last) {
        tmp = self->last;
        Py_INCREF(last);
        self->last = last;
        Py_XDECREF(tmp);
    }
    return 0;
}

static PyMemberDef Custom_members[] = {
    {"first", T_OBJECT_EX, offsetof(CustomObject, first), 0,
     "first name"},
    {"last", T_OBJECT_EX, offsetof(CustomObject, last), 0,
     "last name"},
    {"number", T_INT, offsetof(CustomObject, number), 0,
     "custom number"},
    {NULL}  /* Sentinel */
};

static PyObject *
Custom_name(CustomObject *self, PyObject *ignored)
{
    if (self->first == NULL) {
        PyErr_SetString(PyExc_AttributeError, "first");
        return NULL;
    }
    if (self->last == NULL) {
        PyErr_SetString(PyExc_AttributeError, "last");
        return NULL;
    }
#if PY_MAJOR_VERSION >= 3    
    return PyUnicode_FromFormat("%S %S", self->first, self->last);
#else
    return PyString_FromFormat("%s %s", PyString_AS_STRING(self->first), PyString_AS_STRING(self->last));
#endif
}

static PyObject* Custom_set_callback(PyObject* self1, PyObject* args,PyObject *kwargs)
{
    static char *kwlist[] = {"callback", "args", NULL};
    int gpio=0;
    int ret;
    CustomObject* self = (CustomObject*) self1;
    PyObject* oldcallback=NULL;
    PyObject* oldarg=NULL;
    PyObject* callback=NULL,*argval = NULL;
    ret = PyArg_ParseTupleAndKeywords(args,kwargs,"i|OO:set_callback",kwlist,&gpio,&callback,&argval);
    if (ret == 0) {
        return NULL;
    }
    /*now to set for */
    oldcallback = self->callback;
    self->callback = callback;
    Py_XDECREF(oldcallback);
    Py_XINCREF(self->callback);

    oldarg = self->args;
    self->args = argval;
    Py_XDECREF(oldarg);
    Py_XINCREF(self->args);
    return NULL;
}

static PyObject* Custom_call(PyObject* self1, PyObject* args,PyObject* kwargs)
{
    PyObject* retval = Py_None;
    PyObject* arglist = NULL;
    CustomObject* self = (CustomObject*) self1;

    if (self->callback != NULL) {
        arglist = Py_BuildValue("iO",self->gpio,self->args ? self->args : Py_None);
        if (arglist == NULL) {
            PyErr_SetString(PyErr_NoMemory(),"no memory for arglist");
            return NULL;
        }

        retval = PyEval_CallObject(self->callback,arglist);
        Py_XDECREF(arglist);
    }
    return retval;
}

static PyMethodDef Custom_methods[] = {
    {"name", (PyCFunction) Custom_name, METH_NOARGS,
     "Return the name, combining the first and last name"
    },
    {"setcall",(PyCFunction)Custom_set_callback,METH_VARARGS | METH_KEYWORDS,"set call back functions"},
    {"call", (PyCFunction)Custom_call, METH_NOARGS,"call callback"},
    {NULL}  /* Sentinel */
};

static PyTypeObject CustomType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "custom.Custom",
    .tp_doc = "Custom objects",
    .tp_basicsize = sizeof(CustomObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = Custom_new,
    .tp_init = (initproc) Custom_init,
    .tp_dealloc = (destructor) Custom_dealloc,
    .tp_members = Custom_members,
    .tp_methods = Custom_methods,
};


#if PY_MAJOR_VERSION >= 3
static PyModuleDef custommodule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "custom",
    .m_doc = "Example module that creates an extension type.",
    .m_size = -1,
};

PyMODINIT_FUNC
PyInit_custom(void)
{
    PyObject *m;
    if (PyType_Ready(&CustomType) < 0)
        return NULL;

    m = PyModule_Create(&custommodule);
    if (m == NULL)
        return NULL;

    Py_INCREF(&CustomType);
    PyModule_AddObject(m, "Custom", (PyObject *) &CustomType);
    return m;
}

#else

PyMODINIT_FUNC  initcustom(void)
{
    PyObject* m=NULL;
    m = Py_InitModule3("custom",Custom_methods,"custom init document");
    if (m == NULL) {
        return;
    }

    CustomType.tp_free = _PyObject_GC_Del;
    if (PyType_Ready(&CustomType) < 0) {
        return;
    }
    Py_INCREF(&CustomType);
    PyModule_AddObject(m,"Custom",(PyObject*)&CustomType);
    return;
}
#endif