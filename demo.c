// clang demo.c -shared -o demo.so -I/usr/include/python3.10 -lpython3.10 -fPIE -g

int bar(void);

int foo(void) { return bar(); }

///////

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdbool.h>

int bar(void) {
  printf("%ls\n", Py_GetPath());
  PyObject *myModuleString = PyUnicode_FromString((char *)"foo");
  printf("%p\n", (void *)myModuleString);
  int flags = Py_PRINT_RAW;
  PyObject_Print(myModuleString, stderr, flags);
  PyObject *myModule = PyImport_Import(myModuleString);
  PyObject *myFunction = PyObject_GetAttrString(myModule, (char *)"bar");
  PyObject *args = PyTuple_Pack(0);
  PyObject *myResult = PyObject_CallObject(myFunction, args);
  return PyFloat_AsDouble(myResult);
  return 0;
}
