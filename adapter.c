#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <assert.h>

typedef char* string;
typedef int32_t i32;
typedef uint64_t id;

static PyObject *main_module;

static PyObject *game_fn_get_opponent_handle;
static PyObject *game_fn_change_human_health_handle;
static PyObject *game_fn_get_human_parent_handle;
static PyObject *game_fn_define_human_handle;
static PyObject *game_fn_define_tool_handle;

#define CHECK_PYTHON_ERROR() {\
	if (PyErr_Occurred()) {\
		PyErr_Print();\
		fprintf(stderr, "Error detected in adapter.c:%d\n", __LINE__);\
		exit(EXIT_FAILURE);\
	}\
}

void init(void) {
	PyObject *modules = PySys_GetObject("modules");
    CHECK_PYTHON_ERROR();
	assert(modules);

	main_module = PyDict_GetItemString(modules, "__main__");
	CHECK_PYTHON_ERROR();
	assert(main_module);

	game_fn_get_opponent_handle = PyObject_GetAttrString(main_module, "game_fn_get_opponent");
	CHECK_PYTHON_ERROR();
	assert(game_fn_get_opponent_handle);

	game_fn_change_human_health_handle = PyObject_GetAttrString(main_module, "game_fn_change_human_health");
	CHECK_PYTHON_ERROR();
	assert(game_fn_change_human_health_handle);

	game_fn_get_human_parent_handle = PyObject_GetAttrString(main_module, "game_fn_get_human_parent");
	CHECK_PYTHON_ERROR();
	assert(game_fn_get_human_parent_handle);

	game_fn_define_human_handle = PyObject_GetAttrString(main_module, "game_fn_define_human");
	CHECK_PYTHON_ERROR();
	assert(game_fn_define_human_handle);

	game_fn_define_tool_handle = PyObject_GetAttrString(main_module, "game_fn_define_tool");
	CHECK_PYTHON_ERROR();
	assert(game_fn_define_tool_handle);
}

id game_fn_get_opponent(id human_id) {
	PyObject *args = PyTuple_Pack(1, PyLong_FromLong(human_id));
	assert(args);

	PyObject *result = PyObject_CallObject(game_fn_get_opponent_handle, args);
	assert(result);

	return PyLong_AsUnsignedLongLong(result);
}

void game_fn_change_human_health(id id, i32 added_health) {
	PyObject *args = PyTuple_Pack(2, PyLong_FromLong(id), PyLong_FromLong(added_health));
	assert(args);

	PyObject *result = PyObject_CallObject(game_fn_change_human_health_handle, args);
	assert(result);
}

id game_fn_get_human_parent(id tool_id) {
	PyObject *args = PyTuple_Pack(1, PyLong_FromLong(tool_id));
	assert(args);

	PyObject *result = PyObject_CallObject(game_fn_get_human_parent_handle, args);
	assert(result);

	return PyLong_AsUnsignedLongLong(result);
}

void game_fn_define_human(string name, i32 health, i32 buy_gold_value, i32 kill_gold_value) {
	// TODO: Try only creating the args tuples once in init()
	// TODO: This might be faster, assuming we use smth like PyTuple_SET_ITEM() to set arg values
	PyObject *arg1 = PyBytes_FromString(name);
	CHECK_PYTHON_ERROR();
	assert(arg1);
	PyObject *arg2 = PyLong_FromLong(health);
	CHECK_PYTHON_ERROR();
	assert(arg2);
	PyObject *arg3 = PyLong_FromLong(buy_gold_value);
	CHECK_PYTHON_ERROR();
	assert(arg3);
	PyObject *arg4 = PyLong_FromLong(kill_gold_value);
	CHECK_PYTHON_ERROR();
	assert(arg4);

	PyObject *args = PyTuple_Pack(4, arg1, arg2, arg3, arg4);
	CHECK_PYTHON_ERROR();
	assert(args);

	PyObject *result = PyObject_CallObject(game_fn_define_human_handle, args);
	CHECK_PYTHON_ERROR();
	assert(result);
}

void game_fn_define_tool(string name, i32 buy_gold_value) {
	PyObject *args = PyTuple_Pack(2, PyBytes_FromString(name), PyLong_FromLong(buy_gold_value));
	assert(args);

	PyObject *result = PyObject_CallObject(game_fn_define_tool_handle, args);
	assert(result);
}
