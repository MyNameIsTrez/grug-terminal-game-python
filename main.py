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
        ("define_fn", ctypes.PYFUNCTYPE(None)),  # The None means it returns void
        # ("define_fn", ctypes.c_void_p),  # TODO: Add the old CFUNCTYPE thing back
        ("globals_size", ctypes.c_size_t),
        ("init_globals_fn", ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_uint64)),
        ("define_type", ctypes.c_char_p),
        ("on_fns", ctypes.c_void_p),
        ("resource_mtimes", ctypes.POINTER(ctypes.c_int64)),
    ]


# This is a forward declaration, needed due to it containing a pointer to itself
# See the `GrugModDir._fields_ = ` line later on for the implementation
class GrugModDir(ctypes.Structure):
    pass


GrugModDir._fields_ = [
    ("name", ctypes.c_char_p),
    ("dirs", ctypes.POINTER(GrugModDir)),
    ("dirs_size", ctypes.c_size_t),
    ("dirs_capacity", ctypes.c_size_t),
    ("files", ctypes.POINTER(GrugFile)),
    ("files_size", ctypes.c_size_t),
    ("files_capacity", ctypes.c_size_t),
]


class GrugModified(ctypes.Structure):
    _fields_ = [
        ("path", ctypes.c_char * 4096),
        ("old_dll", ctypes.c_void_p),
        ("file", ctypes.POINTER(GrugFile)),
    ]


class ToolOnFns(ctypes.Structure):
    _fields_ = [
        ("use", ctypes.CFUNCTYPE(None, ctypes.c_void_p)),
    ]


@dataclass
class Human:
    name: str
    health: int
    buy_gold_value: int
    kill_gold_value: int

    # These are not initialized by mods
    id: int = -1
    opponent_id: int = -1
    max_health: int = -1


@dataclass
class Tool:
    name: str = ""
    buy_gold_value: int = 0

    # These are not initialized by mods
    human_parent_id: int = 0
    on_fns = None


class State(Enum):
    PICKING_PLAYER = auto()
    PICKING_TOOLS = auto()
    PICKING_OPPONENT = auto()
    FIGHTING = auto()


@dataclass
class Data:
    humans: list[Human]
    human_dlls: list[ctypes.c_void_p]
    human_globals: list[ctypes.c_void_p]

    tools: list[Tool]
    tool_dlls: list[ctypes.c_void_p]
    tool_globals: list[ctypes.c_void_p]

    state: State = State.PICKING_PLAYER
    type_files: list[GrugFile] = field(default_factory=list)
    gold: int = 400

    player_has_human: bool = False
    player_has_tool: bool = False


PLAYER_INDEX = 0
OPPONENT_INDEX = 1

data = Data(
    humans=[None, None],
    human_dlls=[None, None],
    human_globals=[None, None],
    tools=[Tool(), Tool()],
    tool_dlls=[None, None],
    tool_globals=[None, None],
)

# TODO: Try simplifying these lines
human_definition: Human = None
foo = 42
tool_definition: Tool = None
grug_dll = None


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
    global foo
    print("game_fn_define_human() was called!")
    human_definition = Human(name, health, buy_gold_value, kill_gold_value)
    print(human_definition)
    print(foo)
    foo = 69
    print(foo)


def game_fn_define_tool(name, buy_gold_value):
    global tool_definition
    tool_definition = Tool(name, buy_gold_value)


def get_type_files_impl(dir: GrugModDir, define_type):
    for i in range(dir.dirs_size):
        get_type_files_impl(dir.dirs[i], define_type)

    for i in range(dir.files_size):
        if define_type == dir.files[i].define_type.decode():
            data.type_files.append(dir.files[i])


def get_type_files(define_type):
    data.type_files = []

    grug_mods = GrugModDir.in_dll(grug_dll, "grug_mods")

    get_type_files_impl(grug_mods, define_type)

    return data.type_files


def fight():
    pass


def read_size(prompt):
    try:
        age = int(input(prompt))
    except ValueError:
        print("You didn't enter a valid number", file=sys.stderr)
        return None

    if age < 0:
        print("You can't enter a negative number", file=sys.stderr)
        return None

    return age


def pick_opponent_humans(files_defining_human):
    pass


def pick_opponent():
    pass


def print_tools():
    pass


def pick_tools():
    pass


def print_playable_humans(files_defining_human):
    # global human_definition
    # print(human_definition)

    for i in range(len(data.type_files)):
        # TODO: REMOVE!
        # mage_dll = ctypes.PyDLL("mod_dlls/magic/mage.so")
        # define = mage_dll.define
        # define.restype = None
        # define()

        # TODO: REMOVE
        # parent = ctypes.CDLL(None)
        # dlopen = parent.dlopen
        # dlopen.restype = ctypes.c_void_p
        # dlsym = parent.dlsym
        # dlsym.restype = ctypes.c_void_p
        # print(ctypes.c_char_p(parent.dlerror()).value)
        # lib = dlopen(b"mod_dlls/magic/mage.so", os.RTLD_NOW)
        # if not lib:
        #     print(ctypes.c_char_p(parent.dlerror()).value)
        #     sys.exit(1)
        # define = parent.dlsym(lib, b"define")
        # if not define:
        #     print(ctypes.c_char_p(parent.dlerror()).value)
        #     sys.exit(1)
        # FUNKY = ctypes.PYFUNCTYPE(None)
        # # TODO: It is very strange that calling this crashes after printing 'x1'!
        # # TODO: I suspect the issue has to do with the GIL?
        # FUNKY(define)()

        # TODO: This does not work, for some reason
        # asd = ctypes.PYFUNCTYPE(None)(files_defining_human[i].define_fn)
        # asd()

        files_defining_human[i].define_fn()
        print("lmao")
        global human_definition
        print(human_definition)
        global foo
        # TODO: This printing 42 instead of 123 seems to be caused by
        # TODO: adapter.c re-importing main, which maybe instances a new Python interpreter?
        print(foo)
        human = human_definition
        print(f"{i + 1}. {human.name}, costing {human.buy_gold_value} gold")

    print("")


def pick_player():
    print(f"You have {data.gold}\n")

    files_defining_human = get_type_files("human")

    print_playable_humans(files_defining_human)

    player_number = read_size(
        f"Type the number next to the human you want to play as{" (type 0 to skip)" if data.player_has_human else ""}:\n"
    )
    if player_number == None:
        return

    if player_number == 0:
        if data.player_has_human:
            data.state = State.PICKING_TOOLS
            return

        print("The minimum number you can enter is 1", file=sys.stderr)
        return

    if player_number > data.type_files_size:
        print(
            f"The maximum number you can enter is {len(data.type_files)}",
            file=sys.stderr,
        )
        return

    player_index = player_number - 1

    file = files_defining_human[player_index]

    file.define_fn()
    human = human_definition

    if human.buy_gold_value > data.gold:
        print("You don't have enough gold to pick that human", file=sys.stderr)
        return

    data.gold -= human.buy_gold_value

    human.id = PLAYER_INDEX
    human.opponent_id = OPPONENT_INDEX

    human.max_health = human.health

    data.humans[PLAYER_INDEX] = human
    data.human_dlls[PLAYER_INDEX] = file.dll

    data.human_globals[PLAYER_INDEX] = (ctypes.c_byte * file.globals_size)()
    file.init_globals_fn(data.human_globals[PLAYER_INDEX], PLAYER_INDEX)

    data.player_has_human = True

    data.state = State.PICKING_TOOLS


def update():
    match data.state:
        case State.PICKING_PLAYER:
            pick_player()
        case State.PICKING_TOOLS:
            pick_tools()
        case State.PICKING_OPPONENT:
            pick_opponent()
        case State.FIGHTING:
            fight()


def reload_modified_entities():
    reloads_size = ctypes.c_size_t.in_dll(grug_dll, "grug_reloads_size").value
    reloads_type = GrugModified * 6969
    reloads = reloads_type.in_dll(grug_dll, "grug_reloads")

    for i in range(reloads_size):
        reload = reloads[i]

        file = reload.file.contents

        for i in range(2):
            if reload.old_dll == data.human_dlls[i]:
                data.human_dlls[i] = file.dll

                data.human_globals[i] = (ctypes.c_byte * file.globals_size)()
                file.init_globals_fn(data.human_globals[i], i)

        for i in range(2):
            if reload.old_dll == data.tool_dlls[i]:
                data.tool_dlls[i] = file.dll

                data.tool_globals[i] = (ctypes.c_byte * file.globals_size)()
                file.init_globals_fn(data.tool_globals[i], i)

                data.tools[i].on_fns = file.on_fns


@ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p)
def runtime_error_handler(reason, type, on_fn_name, on_fn_path):
    print(
        f"grug runtime error in {on_fn_name}(): {reason}, in {on_fn_path}",
        file=sys.stderr,
    )


def main():
    global grug_dll

    # TODO: REMOVE
    global foo
    foo = 123

    # RTLD_GLOBAL here allows mods to call functions from adapter.c
    adapter_dll = ctypes.PyDLL("./adapter.so", os.RTLD_GLOBAL)

    adapter_dll.init.restype = None
    adapter_dll.init()

    # RTLD_GLOBAL here mods to access grug_runtime_error_type from grug.c
    grug_dll = ctypes.PyDLL("./grug/grug.so", os.RTLD_GLOBAL)

    grug_dll.grug_set_runtime_error_handler.restype = None

    grug_dll.grug_set_runtime_error_handler(runtime_error_handler)

    grug_dll.grug_regenerate_modified_mods.restype = ctypes.c_bool

    while True:
        if grug_dll.grug_regenerate_modified_mods():
            # TODO: Try getting a ptr to this global only once,
            # before this while-loop
            error = GrugError.in_dll(grug_dll, "grug_error")

            if error.has_changed:
                print(
                    f"grug loading error: {error.msg.decode()}, in {error.path.decode()} (detected in grug.c:{error.grug_c_line_number})",
                    file=sys.stderr,
                )

            time.sleep(1)

            continue

        reload_modified_entities()

        # Since this is a simple terminal game, there are no PNGs/MP3s/etc.
        # reload_modified_resources();

        update()

        print()

        time.sleep(1)


if __name__ == "__main__":
    main()
