// clang demo.c -shared -o demo.so -I/usr/include/python3.10 -lpython3.10 -fPIE -g

#define PY_SSIZE_T_CLEAN
#include <Python.h>

int bar(void) {
  // This works
  printf("Py_GetPath(): %ls\n", Py_GetPath());

  // This segfaults
  PyObject *myModuleString = PyUnicode_FromString("a");

  // printf("myModuleString: %p\n", (void *)myModuleString);

  // printf("Calling PyObject_Print()...\n");
  // int flags = Py_PRINT_RAW;
  // PyObject_Print(myModuleString, stderr, flags);
  // printf("Called PyObject_Print()!\n");

  // PyObject *myModule = PyImport_Import(myModuleString);
  // PyObject *myFunction = PyObject_GetAttrString(myModule, "bar");
  // PyObject *args = PyTuple_Pack(0);
  // PyObject *myResult = PyObject_CallObject(myFunction, args);
  // return PyFloat_AsDouble(myResult);

  // return 42;
  return 0;
}

int foo(void) {
  return bar();
}
