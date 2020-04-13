#include <Python.h>
#include "structmember.h"

#define DEBUG(...)  do{fprintf(stderr,"[%s:%d]:",__FILE__,__LINE__); fprintf(stderr, __VA_ARGS__); fprintf(stderr,"\n");}while(0)

typedef struct {
    PyObject_HEAD
    PyObject *first; /* first name */
    PyObject *last;  /* last name */
    PyObject *callfunc; /*call function*/
    PyObject *callargs; /*call args*/
} Noddy;

static void Noddy_dealloc(Noddy* self)
{
    Py_XDECREF(self->first);
    self->first = NULL;
    Py_XDECREF(self->last);
    self->last = NULL;
    Py_XDECREF(self->callfunc);
    self->callfunc = NULL;
    Py_XDECREF(self->callargs);
    self->callargs = NULL;
    Py_TYPE(self)->tp_free((PyObject*)self);
    DEBUG("Noddy_dealloc");
}

static PyObject *Noddy_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Noddy *self;

    self = (Noddy *)type->tp_alloc(type, 0);
    if (self != NULL) {
#if PY_MAJOR_VERSION >= 3
        self->first = PyUnicode_FromString("");
#else        
        self->first = PyString_FromString("");
#endif
        if (self->first == NULL) {
            Py_DECREF(self);
            return NULL;
        }

#if PY_MAJOR_VERSION >= 3
        self->last = PyUnicode_FromString("");
#else
        self->last = PyString_FromString("");
#endif
        if (self->last == NULL) {
            Py_DECREF(self);
            return NULL;
        }
        self->callfunc = Py_None;
        Py_XINCREF(self->callfunc);
        self->callargs = Py_None;
        Py_XINCREF(self->callargs);
    }

    return (PyObject *)self;
}

static int Noddy_init(Noddy *self, PyObject *args, PyObject *kwds)
{
    PyObject *first=NULL, *last=NULL , *callback=NULL,*argval=NULL, *tmp;

    static char *kwlist[] = {"first", "last","callback","args",NULL};

    if (! PyArg_ParseTupleAndKeywords(args, kwds, "|OOOO", kwlist,
                                      &first, &last,&callback,&argval))
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

    if (callback) {
        tmp = self->callfunc;
        Py_INCREF(callback);
        self->callfunc = callback;
        Py_XDECREF(tmp);
    }

    if (argval) {
        tmp = self->callargs;
        Py_INCREF(argval);
        self->callargs = argval;
        Py_XDECREF(tmp);        
    }

    return 0;
}


static PyMemberDef Noddy_members[] = {
    {"first", T_OBJECT_EX, offsetof(Noddy, first), 0,
     "first name"},
    {"last", T_OBJECT_EX, offsetof(Noddy, last), 0,
     "last name"},
    {"callback",T_OBJECT_EX,offsetof(Noddy,callfunc),0,
     "callback function"},
    {"args", T_OBJECT_EX,offsetof(Noddy,callargs),0,
     "call args"},
    {NULL}  /* Sentinel */
};

static PyObject *Noddy_name(Noddy* self)
{
    PyObject *result;

    if (self->first == NULL) {
        PyErr_SetString(PyExc_AttributeError, "first");
        return NULL;
    }

    if (self->last == NULL) {
        PyErr_SetString(PyExc_AttributeError, "last");
        return NULL;
    }


#if PY_MAJOR_VERSION >= 3
    result = PyUnicode_FromFormat("%S %S", self->first,self->last);
#else
    result = PyString_FromFormat("%s %s", PyString_AS_STRING(self->first), PyString_AS_STRING(self->last));
#endif

    return result;
}

static PyObject *Noddy_call(Noddy* self)
{
    PyObject *result=Py_None;
    PyObject *arglist = NULL;

    if (self->callfunc != Py_None && 
        self->callfunc != NULL) {
        if (PyErr_Occurred()) {
            DEBUG(" ");
        }
        arglist = Py_BuildValue("(O)",self->callargs != NULL ? self->callargs : Py_None);
        if (PyErr_Occurred()) {
            DEBUG(" ");
        }
        if (arglist == NULL) {
            return NULL;
        }        
        result = PyEval_CallObject(self->callfunc,arglist);
        if (PyErr_Occurred()) {
            DEBUG(" ");
        }
    }

    return result;
}


static PyMethodDef Noddy_methods[] = {
    {"name", (PyCFunction)Noddy_name, METH_NOARGS,
     "Return the name, combining the first and last name"
    },
    {"call",(PyCFunction)Noddy_call, METH_NOARGS,
     "call callback functions"},
    {NULL}  /* Sentinel */
};

static PyTypeObject NoddyType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "noddy.Noddy",             /* tp_name */
    sizeof(Noddy),             /* tp_basicsize */
    0,                         /* tp_itemsize */
    (destructor)Noddy_dealloc, /* tp_dealloc */
    0,                         /* tp_print */
    0,                         /* tp_getattr */
    0,                         /* tp_setattr */
    0,                         /* tp_compare */
    0,                         /* tp_repr */
    0,                         /* tp_as_number */
    0,                         /* tp_as_sequence */
    0,                         /* tp_as_mapping */
    0,                         /* tp_hash */
    0,                         /* tp_call */
    0,                         /* tp_str */
    0,                         /* tp_getattro */
    0,                         /* tp_setattro */
    0,                         /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT |
        Py_TPFLAGS_BASETYPE,   /* tp_flags */
    "Noddy objects",           /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */
    0,                         /* tp_richcompare */
    0,                         /* tp_weaklistoffset */
    0,                         /* tp_iter */
    0,                         /* tp_iternext */
    Noddy_methods,             /* tp_methods */
    Noddy_members,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Noddy_init,      /* tp_init */
    0,                         /* tp_alloc */
    Noddy_new,                 /* tp_new */
};


#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif

#if PY_MAJOR_VERSION >= 3

static PyModuleDef noddymodule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "noddy",
    .m_doc = "Example module that creates an extension type.",
    .m_size = -1,
};

PyMODINIT_FUNC
PyInit_noddy(void)
{
    PyObject *m;
    if (PyType_Ready(&NoddyType) < 0)
        return NULL;

    m = PyModule_Create(&noddymodule);
    if (m == NULL)
        return NULL;

    Py_INCREF(&NoddyType);
    PyModule_AddObject(m, "Noddy", (PyObject *) &NoddyType);
    return m;
}


#else

static PyMethodDef module_methods[] = {
    {NULL}  /* Sentinel */
};

PyMODINIT_FUNC
initnoddy(void)
{
    PyObject* m;

    if (PyType_Ready(&NoddyType) < 0)
        return;

    m = Py_InitModule3("noddy", module_methods,
                       "Example module that creates an extension type.");

    if (m == NULL)
        return;

    Py_INCREF(&NoddyType);
    PyModule_AddObject(m, "Noddy", (PyObject *)&NoddyType);
}
#endif