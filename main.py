# clang demo.c -shared -o demo.so -I/usr/include/python3.12 -lpython3.12 -fPIE -g && python3 main.py

import ctypes


def bar():
    return 42

# def foo(dll):
#     proto = ctypes.PYFUNCTYPE(ctypes.c_int)
#     params = ()
#     fn = proto(("foo", dll), params)
#     return fn()

def main():
    dll = ctypes.PyDLL("./demo.so")
    print(dll.foo())
    # print(foo(dll))

if __name__ == "__main__":
    main()
