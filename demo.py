# python3 demo.py
# gdb --args python3 demo.py

import ctypes

def bar():
    return 42

dll = ctypes.CDLL("./demo.so")

def foo():
    proto = ctypes.CFUNCTYPE(ctypes.c_int)
    params = ()
    api = proto(("foo", dll), params)

    return api()

print(foo())
