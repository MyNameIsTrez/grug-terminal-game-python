#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <assert.h>

static PyObject *module;

static PyObject *game_fn_magic_handle;
static PyObject *game_fn_magic_args;

void init(void) {
	module = PyImport_ImportModule("main");
	assert(module);

	game_fn_magic_handle = PyObject_GetAttrString(module, "game_fn_magic");
	assert(game_fn_magic_handle);
	game_fn_magic_args = PyTuple_Pack(0);
	assert(game_fn_magic_args);
}

void game_fn_magic(void) {
	PyObject_CallObject(game_fn_magic_handle, game_fn_magic_args);
}
