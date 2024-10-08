# clang mod.c -o mod.so -shared -fPIE -g && clang adapter.c -o adapter.so -shared -I/usr/include/python3.10 -lpython3.10 -fPIE -g && python3 main.py

import ctypes


def main():
    dll = ctypes.PyDLL("./adapter.so")

    dll.init()
    print(dll.run(ctypes.c_float(42)))

    # init(dll)
    # print(run(dll, ctypes.c_float(42)))


def bar():
    return 42


# TODO: I'm not sure when we'd want to use this approach, instead of `dll.init()`
# def init(dll):
#     proto = ctypes.PYFUNCTYPE(None)
#     fn = proto(("init", dll))
#     fn()


# TODO: I'm not sure when we'd want to use this approach, instead of `dll.run()`
# def run(dll, f):
#     proto = ctypes.PYFUNCTYPE(ctypes.c_int, ctypes.c_float)
#     params = (1, "f"),
#     fn = proto(("run", dll), params)
#     fn(f)

if __name__ == "__main__":
    main()
