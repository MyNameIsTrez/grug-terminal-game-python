#!/usr/bin/python3

import ctypes
import os


def game_fn_define_human(name, health, buy_gold_value, kill_gold_value):
    print("game_fn_define_human() was called!")


def main():
    adapter_dll = ctypes.PyDLL("./adapter.so", os.RTLD_GLOBAL)

    adapter_dll.init.restype = None
    adapter_dll.init()

    dll = ctypes.PyDLL("mod_dlls/magic/mage.so", os.RTLD_NOW)

    define = dll.define
    define.restype = None
    print("a")
    define()
    print("b")


if __name__ == "__main__":
    main()
