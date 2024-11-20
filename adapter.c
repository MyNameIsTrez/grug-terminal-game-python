#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <assert.h>

typedef char* string;
typedef int32_t i32;
typedef uint64_t id;

static PyObject *module;

static PyObject *game_fn_magic_handle;
static PyObject *game_fn_get_opponent_handle;
static PyObject *game_fn_define_human_handle;

void init(void) {
	module = PyImport_ImportModule("main");
	assert(module);

	game_fn_magic_handle = PyObject_GetAttrString(module, "game_fn_magic");
	assert(game_fn_magic_handle);

	game_fn_get_opponent_handle = PyObject_GetAttrString(module, "game_fn_get_opponent");
	assert(game_fn_get_opponent_handle);

	game_fn_define_human_handle = PyObject_GetAttrString(module, "game_fn_define_human");
	assert(game_fn_define_human_handle);
}

void game_fn_magic(void) {
	PyObject *args = PyTuple_Pack(0);
	assert(args);
	PyObject_CallObject(game_fn_magic_handle, args);
}

id game_fn_get_opponent(id human_id) {
	PyObject *args = PyTuple_Pack(1, PyLong_FromLong(human_id));
	assert(args);

	PyObject *result = PyObject_CallObject(game_fn_define_human_handle, args);
	assert(result);

	return PyLong_AsUnsignedLongLong(result);
}

void game_fn_define_human(string name, i32 health, i32 buy_gold_value, i32 kill_gold_value) {
	// TODO: Try only creating the args tuples once in init()
	// TODO: This might be faster, assuming we use smth like PyTuple_SET_ITEM() to set arg values
	PyObject *args = PyTuple_Pack(4, PyBytes_FromString(name), PyLong_FromLong(health), PyLong_FromLong(buy_gold_value), PyLong_FromLong(kill_gold_value));
	assert(args);

	PyObject_CallObject(game_fn_define_human_handle, args);
}
