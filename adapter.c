#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <assert.h>

typedef char* string;
typedef int32_t i32;
typedef uint64_t id;

static PyObject *module;

static PyObject *game_fn_magic_handle;
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
	module = PyImport_ImportModule("main");
	assert(module);

	// game_fn_magic_handle = PyObject_GetAttrString(module, "game_fn_magic");
	// assert(game_fn_magic_handle);

	// game_fn_change_human_health_handle = PyObject_GetAttrString(module, "game_fn_change_human_health");
	// assert(game_fn_change_human_health_handle);

	// game_fn_get_opponent_handle = PyObject_GetAttrString(module, "game_fn_get_opponent");
	// assert(game_fn_get_opponent_handle);

	printf("Saved game_fn_define_human_handle\n"); // TODO: REMOVE
	game_fn_define_human_handle = PyObject_GetAttrString(module, "game_fn_define_human");
	assert(game_fn_define_human_handle);

	// game_fn_define_tool_handle = PyObject_GetAttrString(module, "game_fn_define_tool");
	// assert(game_fn_define_tool_handle);

	// TODO: REMOVE
	void game_fn_define_human(string name, i32 health, i32 buy_gold_value, i32 kill_gold_value);
	#pragma GCC diagnostic push
	#pragma GCC diagnostic ignored "-Wpedantic"
	printf("game_fn_define_human: %p\n", (void *)game_fn_define_human);
	#pragma GCC diagnostic pop
}

void game_fn_magic(void) {
	PyObject *args = PyTuple_Pack(0);
	assert(args);

	PyObject *result = PyObject_CallObject(game_fn_magic_handle, args);
	assert(result);
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
	printf("name: %s\n", name);
	printf("health: %d\n", health);
	printf("buy_gold_value: %d\n", buy_gold_value);
	printf("kill_gold_value: %d\n", kill_gold_value);

	printf("Py_IsInitialized(): %d\n", Py_IsInitialized());

	// TODO: Try only creating the args tuples once in init()
	// TODO: This might be faster, assuming we use smth like PyTuple_SET_ITEM() to set arg values
	printf("x1\n");
	PyObject *arg1 = PyBytes_FromString(name);
	printf("x2\n");
	PyObject *arg2 = PyLong_FromLong(health);
	printf("x3\n");
	PyObject *arg3 = PyLong_FromLong(buy_gold_value);
	printf("x4\n");
	PyObject *arg4 = PyLong_FromLong(kill_gold_value);

	printf("x5\n");
	PyObject *args = PyTuple_Pack(4, arg1, arg2, arg3, arg4);
	printf("y\n");
	assert(args);

	module = PyImport_ImportModule("main");
	CHECK_PYTHON_ERROR();

	game_fn_define_human_handle = PyObject_GetAttrString(module, "game_fn_define_human");
	CHECK_PYTHON_ERROR();

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
