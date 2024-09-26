# gdb --args python3 demo.py

import ctypes

def bar():
    return 42

dll = ctypes.PyDLL("./demo.so")

def foo():
    proto = ctypes.CFUNCTYPE(ctypes.c_int)
    params = ()
    api = proto(("foo", dll), params)

    return api()

print(dll)

print(foo())
