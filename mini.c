// clang mini.c -o mini.out -I/usr/include/python3.10 -lpython3.10 && ./mini.out

#define PY_SSIZE_T_CLEAN
#include <Python.h>

void exec_pycode(const char *code) {
	Py_Initialize();

	PyRun_SimpleString(code);

	PyObject *myModuleString = PyUnicode_FromString((char *)"a");
	int flags = Py_PRINT_RAW;
	PyObject_Print(myModuleString, stderr, flags);

	Py_Finalize();
}

int main(void) {
	exec_pycode("print(42)");
}
