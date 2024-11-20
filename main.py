import ctypes
import os
import sys
import time
from dataclasses import dataclass


@dataclass
class Human:
    name: str
    health: int
    buy_gold_value: int
    kill_gold_value: int


class GrugError(ctypes.Structure):
    _fields_ = [
        ("msg", ctypes.c_char * 420),
        ("path", ctypes.c_char * 4096),
        ("grug_c_line_number", ctypes.c_int),
        ("has_changed", ctypes.c_bool),
    ]


def game_fn_magic():
    print("Magic!")


# TODO: Try simplifying this line
human_definition: Human = None


def game_fn_define_human(name, health, buy_gold_value, kill_gold_value):
    global human_definition
    human_definition = Human(name, health, buy_gold_value, kill_gold_value)


@ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p)
def runtime_error_handler(reason, type, on_fn_name, on_fn_path):
    print(
        f"grug runtime error in {on_fn_name}(): {reason}, in {on_fn_path}",
        file=sys.stderr,
    )


def main():
    # RTLD_GLOBAL here allows mods to call functions from adapter.c
    adapter_dll = ctypes.PyDLL("./adapter.so", os.RTLD_GLOBAL)
    adapter_dll.init()

    # RTLD_GLOBAL here mods to access grug_runtime_error_type from grug.c
    grug_dll = ctypes.PyDLL("./grug/grug.so", os.RTLD_GLOBAL)

    grug_dll.grug_set_runtime_error_handler.restype = None

    grug_dll.grug_set_runtime_error_handler(runtime_error_handler)

    grug_dll.grug_regenerate_modified_mods.restype = ctypes.c_bool

    if grug_dll.grug_regenerate_modified_mods():
        # TODO: Try getting a ptr to this global only once,
        # before this while-loop
        error = GrugError.in_dll(grug_dll, "grug_error")

        if error.has_changed:
            print(
                f"grug loading error: {error.msg.decode()}, in {error.path.decode()} (detected in grug.c:{error.grug_c_line_number})",
                file=sys.stderr,
            )

        # TODO: Add back!
        # time.sleep(1)

        # TODO: Add back!
        # continue

    # TODO: Remove the mod.c and mod.so files!
    # mod_dll = ctypes.PyDLL("./mod.so")
    # mod_dll.on_foo()


if __name__ == "__main__":
    main()
