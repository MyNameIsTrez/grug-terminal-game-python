# clang mod.c -o mod.so -shared -fPIE -g && clang adapter.c -o adapter.so -shared -I/usr/include/python3.12 -lpython3.12 -fPIE -g && python3 main.py

import ctypes
import os


def main():
    adapter_dll = ctypes.PyDLL("./adapter.so", os.RTLD_GLOBAL)

    adapter_dll.init()

    mod_dll = ctypes.PyDLL("./mod.so")

    mod_dll.on_foo()


def game_fn_magic():
    print("Magic!")
    return 42


if __name__ == "__main__":
    main()
