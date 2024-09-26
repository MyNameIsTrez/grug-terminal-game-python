#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <assert.h>

int bar(float f) {
	PyObject *module = PyImport_ImportModule("main");
	assert(module);

	PyObject *fn = PyObject_GetAttrString(module, "bar");
	assert(fn);

	PyObject *args = PyTuple_Pack(0);
	assert(args);

	PyObject *result = PyObject_CallObject(fn, args);
	assert(result);

	// In newer versions of Python, this function is identical,
	// but doesn't start with an underscore:
	// https://github.com/python/cpython/commit/be436e08b8bd9fcd2202d6ce4d924bba7551e96f
	return f + _PyLong_AsInt(result);
}

int foo(float f) {
	// printf("i: %i\n", f);
	printf("f: %f\n", f);
	return bar(f);
}
