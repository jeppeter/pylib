# include "Python.h" 
# include "sample.h" 

/* int gcd(int, int) */
static PyObject * py_add(PyObject * self, PyObject * args) 
{ 
	int x, y, result; 
	if (! PyArg_ParseTuple(args, "ii", &x, &y)) 
	{ 
		return NULL; 
	} 
	result = x + y; 
	return Py_BuildValue("i", result); 
} 

/* int divide(int, int, int *) */
static PyObject * py_divide(PyObject * self, PyObject * args) 
{ 
	int a, b, quotient, remainder; 
	if (! PyArg_ParseTuple(args, "ii", &a, &b)) 
	{ 
		return NULL; 
	} 
	quotient = a /b;
	remainder = a % b;
	return Py_BuildValue("(ii)", quotient, remainder); 
} 

/* Module method table */
static PyMethodDef SampleMethods[] = 
{ 
	{"add", py_add, METH_VARARGS, "add function"}, 
	{"divide", py_divide, METH_VARARGS, "Integer division"}, 
	{ NULL, NULL, 0, NULL} 
}; 

#if 0
/* Module structure */
static struct PyModuleDef samplemodule = 
{ 
	PyModuleDef_HEAD_INIT, 
	"sample", /* name of module */
	"A sample module", /* Doc string (may be NULL) */
	-1, /* Size of per-interpreter state or -1 */
	SampleMethods /* Method table */
}; 
#endif

/* Module initialization function */
PyMODINIT_FUNC 
initsample(void) 
{ 
	Py_InitModule("sample",SampleMethods);
	return;
} 
