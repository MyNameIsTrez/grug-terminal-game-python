# clang demo.c -shared -o demo.so -I/usr/include/python3.12 -lpython3.12 -fPIE -g && python3 main.py

import ctypes


def main():
    dll = ctypes.PyDLL("./demo.so")
    print(dll.foo(ctypes.c_float(42)))
    # print(foo(dll, 42))


def bar():
    return 42


# TODO: I'm not sure when we'd want to use this approach, instead of `dll.foo()`
# def foo(dll, f):
#     proto = ctypes.PYFUNCTYPE(ctypes.c_int, ctypes.c_float)
#     params = (1, "f"),
#     fn = proto(("foo", dll), params)
#     return fn(f)

if __name__ == "__main__":
    main()
