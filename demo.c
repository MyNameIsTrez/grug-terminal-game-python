#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <assert.h>

int bar(float f) {
	PyObject *myModule = PyImport_ImportModule("main");
	assert(myModule);

	PyObject *myFunction = PyObject_GetAttrString(myModule, "bar");
	assert(myFunction);

	PyObject *args = PyTuple_Pack(0);
	assert(args);

	PyObject *myResult = PyObject_CallObject(myFunction, args);
	assert(myResult);

	// In newer versions of Python, this function is identical,
	// but doesn't start with an underscore:
	// https://github.com/python/cpython/commit/be436e08b8bd9fcd2202d6ce4d924bba7551e96f
	return f + _PyLong_AsInt(myResult);
}

int foo(float f) {
	// printf("i: %i\n", f);
	printf("f: %f\n", f);
	return bar(f);
}
