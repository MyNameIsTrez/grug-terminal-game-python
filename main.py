# clang demo.c -shared -o demo.so -I/usr/include/python3.12 -lpython3.12 -fPIE -g && python3 main.py

import ctypes


def bar():
    return 42

def foo(dll, f):
    proto = ctypes.PYFUNCTYPE(ctypes.c_int, ctypes.c_float)
    params = (1, "f"),
    fn = proto(("foo", dll), params)
    return fn(f)

def main():
    dll = ctypes.PyDLL("./demo.so")
    # print(dll.foo(42)) # This can't pass floats, so gets printed as "0.0"
    print(foo(dll, 42))

if __name__ == "__main__":
    main()
