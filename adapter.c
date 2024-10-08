#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <assert.h>

static PyObject *module;
static PyObject *bar;
static PyObject *bar_args;

void init(void) {
	module = PyImport_ImportModule("main");
	assert(module);

	bar = PyObject_GetAttrString(module, "bar");
	assert(bar);

	bar_args = PyTuple_Pack(0);
	assert(bar_args);
}

int run(float f) {
	PyObject *result = PyObject_CallObject(bar, bar_args);
	assert(result);

	// In newer versions of Python, this function is identical,
	// but doesn't start with an underscore:
	// https://github.com/python/cpython/commit/be436e08b8bd9fcd2202d6ce4d924bba7551e96f
	return f + _PyLong_AsInt(result);
}
