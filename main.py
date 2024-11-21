import ctypes
import os
import sys
import time
from dataclasses import dataclass, field
from enum import Enum, auto


class GrugError(ctypes.Structure):
    _fields_ = [
        ("msg", ctypes.c_char * 420),
        ("path", ctypes.c_char * 4096),
        ("grug_c_line_number", ctypes.c_int),
        ("has_changed", ctypes.c_bool),
    ]


class GrugFile(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("dll", ctypes.c_void_p),
        (
            "define_fn",
            ctypes.PYFUNCTYPE(None),
        ),  # The first None means return void, the second None means no args
        ("globals_size", ctypes.c_size_t),
        ("init_globals_fn", ctypes.PYFUNCTYPE(None, ctypes.c_void_p, ctypes.c_uint64)),
        ("define_type", ctypes.c_char_p),
        ("on_fns", ctypes.c_void_p),
        ("resource_mtimes", ctypes.POINTER(ctypes.c_int64)),
    ]


@dataclass
class Human:
    name: str
    health: int
    buy_gold_value: int
    kill_gold_value: int

    # These are not initialized by mods
    id: int
    opponent_id: int
    max_health: int


@dataclass
class Tool:
    name: str
    buy_gold_value: int

    # These are not initialized by mods
    human_parent_id: int
    # TODO: Add `tool_on_fns *on_fns;`


class State(Enum):
    STATE_PICKING_PLAYER = auto()
    STATE_PICKING_TOOLS = auto()
    STATE_PICKING_OPPONENT = auto()
    STATE_FIGHTING = auto()


@dataclass
class Data:
    state: State = State.STATE_PICKING_PLAYER
    type_files: list[GrugFile] = field(default_factory=list)
    gold: int = 400

    humans: list[Human] = field(default_factory=list)
    human_dlls: list[ctypes.c_void_p] = field(default_factory=list)
    human_globals: list[ctypes.c_void_p] = field(default_factory=list)

    tools: list[Tool] = field(default_factory=list)
    tool_dlls: list[ctypes.c_void_p] = field(default_factory=list)
    tool_globals: list[ctypes.c_void_p] = field(default_factory=list)

    player_has_human: bool = False
    player_has_tool: bool = False


data = Data()

# TODO: Try simplifying these lines
human_definition: Human = None
tool_definition: Tool = None


def game_fn_magic():
    print("Magic!")


def game_fn_get_opponent(human_id):
    assert human_id < 2
    return data.humans[human_id].opponent_id


def clamp(n, lowest, highest):
    return max(lowest, min(highest, n))


def game_fn_change_human_health(id, added_health):
    assert id < 2
    human = data.humans[id]
    human.health = clamp(human.health + added_health, 0, human.max_health)


def game_fn_get_human_parent(tool_id):
    assert tool_id < 2
    return data.tools[tool_id].human_parent_id


def game_fn_define_human(name, health, buy_gold_value, kill_gold_value):
    global human_definition
    human_definition = Human(name, health, buy_gold_value, kill_gold_value)


def game_fn_define_tool(name, buy_gold_value):
    global tool_definition
    tool_definition = Tool(name, buy_gold_value)


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
