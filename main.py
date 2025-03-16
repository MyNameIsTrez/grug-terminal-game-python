import ctypes
import os
import random
import sys
import time
from dataclasses import dataclass, field, replace
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
        ("entity", ctypes.c_char_p),
        ("entity_type", ctypes.c_char_p),
        ("dll", ctypes.c_void_p),
        ("globals_size", ctypes.c_size_t),
        ("init_globals_fn", ctypes.PYFUNCTYPE(None, ctypes.c_void_p, ctypes.c_uint64)),
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
        ("file", GrugFile),
    ]


class HumanOnFns(ctypes.Structure):
    _fields_ = [
        ("spawn", ctypes.PYFUNCTYPE(None, ctypes.c_void_p)),
        ("despawn", ctypes.PYFUNCTYPE(None, ctypes.c_void_p)),
    ]


class ToolOnFns(ctypes.Structure):
    _fields_ = [
        ("spawn", ctypes.PYFUNCTYPE(None, ctypes.c_void_p)),
        ("despawn", ctypes.PYFUNCTYPE(None, ctypes.c_void_p)),
        ("use", ctypes.PYFUNCTYPE(None, ctypes.c_void_p)),
    ]


@dataclass
class Human:
    name: str = ""
    health: int = -1
    buy_gold_value: int = -1
    kill_gold_value: int = -1

    # These are not initialized by mods
    id: int = -1
    opponent_id: int = -1
    max_health: int = -1
    on_fns: HumanOnFns = None


@dataclass
class Tool:
    name: str = ""
    buy_gold_value: int = -1

    # These are not initialized by mods
    human_parent_id: int = 0
    on_fns: ToolOnFns = None


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
    humans=[Human(), Human()],
    human_dlls=[None, None],
    human_globals=[None, None],
    tools=[Tool(), Tool()],
    tool_dlls=[None, None],
    tool_globals=[None, None],
)

human_on_spawn_data = Human()
tool_on_spawn_data = Tool()
grug_dll = None
on_fn_name = None
on_fn_path = None


def game_fn_get_opponent(human_id):
    global on_fn_name, on_fn_path
    if human_id >= 2:
        print(
            f"grug runtime error in {on_fn_name.value.decode()}(): the human_id argument of get_opponent() was {human_id}, while the function only expects it to be up to 2, in {on_fn_path.value.decode()}",
            file=sys.stderr,
        )
        return -1
    return data.humans[human_id].opponent_id


def clamp(n, lowest, highest):
    return max(lowest, min(highest, n))


def game_fn_change_human_health(human_id, added_health):
    global on_fn_name, on_fn_path
    if human_id >= 2:
        print(
            f"grug runtime error in {on_fn_name.value.decode()}(): the human_id argument of change_human_health() was {human_id}, while the function only expects it to be up to 2, in {on_fn_path.value.decode()}",
            file=sys.stderr,
        )
        return -1
    if added_health == -42:
        print(
            f"grug runtime error in {on_fn_name.value.decode()}(): the added_health argument of change_human_health() was -42, while the function deems that number to be forbidden, in {on_fn_path.value.decode()}",
            file=sys.stderr,
        )
        return -1
    human = data.humans[human_id]
    human.health = clamp(human.health + added_health, 0, human.max_health)


def game_fn_get_human_parent(tool_id):
    global on_fn_name, on_fn_path
    if tool_id >= 2:
        print(
            f"grug runtime error in {on_fn_name.value.decode()}(): the tool_id argument of get_human_parent() was {tool_id}, while the function only expects it to be up to 2, in {on_fn_path.value.decode()}",
            file=sys.stderr,
        )
        return -1
    return data.tools[tool_id].human_parent_id


def game_fn_print_string(msg):
    print(msg)


set_human_kill_gold_value_called = False
set_human_buy_gold_value_called = False
set_human_health_called = False
set_human_name_called = False

set_tool_buy_gold_value_called = False
set_tool_name_called = False


def game_fn_set_human_kill_gold_value(kill_gold_value):
    global set_human_kill_gold_value_called
    if set_human_kill_gold_value_called:
        print(
            f"set_human_kill_gold_value() was called twice by on_spawn()",
            file=sys.stderr,
        )
        return
    set_human_kill_gold_value_called = True

    human_on_spawn_data.kill_gold_value = kill_gold_value


def game_fn_set_human_buy_gold_value(buy_gold_value):
    global set_human_buy_gold_value_called
    if set_human_buy_gold_value_called:
        print(
            f"set_human_buy_gold_value() was called twice by on_spawn()",
            file=sys.stderr,
        )
        return
    set_human_buy_gold_value_called = True

    human_on_spawn_data.buy_gold_value = buy_gold_value


def game_fn_set_human_health(health):
    global set_human_health_called
    if set_human_health_called:
        print(
            f"set_human_health() was called twice by on_spawn()",
            file=sys.stderr,
        )
        return
    set_human_health_called = True

    human_on_spawn_data.health = health


def game_fn_set_human_name(name):
    global set_human_name_called
    if set_human_name_called:
        print(
            f"set_human_name() was called twice by on_spawn()",
            file=sys.stderr,
        )
        return
    set_human_name_called = True

    human_on_spawn_data.name = name


def game_fn_set_tool_buy_gold_value(buy_gold_value):
    global set_tool_buy_gold_value_called
    if set_tool_buy_gold_value_called:
        print(
            f"set_tool_buy_gold_value() was called twice by on_spawn()",
            file=sys.stderr,
        )
        return
    set_tool_buy_gold_value_called = True

    tool_on_spawn_data.buy_gold_value = buy_gold_value


def game_fn_set_tool_name(name):
    global set_tool_name_called
    if set_tool_name_called:
        print(
            f"set_tool_name() was called twice by on_spawn()",
            file=sys.stderr,
        )
        return
    set_tool_name_called = True

    tool_on_spawn_data.name = name


def get_type_files_impl(dir: GrugModDir, entity_type):
    for i in range(dir.dirs_size):
        get_type_files_impl(dir.dirs[i], entity_type)

    for i in range(dir.files_size):
        if dir.files[i].entity_type.decode() == entity_type:
            data.type_files.append(dir.files[i])


def get_type_files(entity_type):
    data.type_files = []

    grug_mods = GrugModDir.in_dll(grug_dll, "grug_mods")

    get_type_files_impl(grug_mods, entity_type)

    return data.type_files


def call_human_on_despawn(on_fns, globals):
    if on_fns.despawn:
        on_fns.despawn(globals)


def call_tool_on_despawn(on_fns, globals):
    if on_fns.despawn:
        on_fns.despawn(globals)


def fight():
    player = data.humans[PLAYER_INDEX]
    opponent = data.humans[OPPONENT_INDEX]

    player_tool = data.tools[PLAYER_INDEX]
    opponent_tool = data.tools[OPPONENT_INDEX]

    opponent_human_globals = data.human_globals[OPPONENT_INDEX]

    player_tool_globals = data.tool_globals[PLAYER_INDEX]
    opponent_tool_globals = data.tool_globals[OPPONENT_INDEX]

    print(f"You have {player.health} health")
    print(f"The opponent has {opponent.health} health\n")

    use = player_tool.on_fns.use
    if use:
        print(f"You use your {player_tool.name}")
        use(player_tool_globals)
        time.sleep(1)
    else:
        print(f"You don't know what to do with your {player_tool.name}")
        time.sleep(1)

    if opponent.health <= 0:
        print("The opponent died!")
        call_human_on_despawn(opponent.on_fns, opponent_human_globals)
        time.sleep(1)
        data.state = State.PICKING_PLAYER
        data.gold += opponent.kill_gold_value
        player.health = player.max_health
        return

    use = opponent_tool.on_fns.use
    if use:
        print(f"The opponent uses their {opponent_tool.name}")
        use(opponent_tool_globals)
        time.sleep(1)
    else:
        print(f"The opponent doesn't know what to do with their {opponent_tool.name}")
        time.sleep(1)

    if player.health <= 0:
        print("You died!")
        time.sleep(1)
        data.state = State.PICKING_PLAYER
        player.health = player.max_health


def read_size(prompt):
    text = input(prompt)

    if text == "f":
        grug_dll.grug_toggle_on_fns_mode()
        print(
            f"Toggled grug to {"safe" if grug_dll.grug_are_on_fns_in_safe_mode() else "fast"} mode"
        )
        return None

    try:
        age = int(text)
    except ValueError:
        print("You didn't enter a valid number", file=sys.stderr)
        return None

    if age < 0:
        print("You can't enter a negative number", file=sys.stderr)
        return None

    return age


def call_human_on_spawn(entity, on_fns, globals):
    global set_human_name_called
    global set_human_health_called
    global set_human_buy_gold_value_called
    global set_human_kill_gold_value_called

    if not on_fns.spawn:
        print(f"{entity.decode()} is missing on_spawn()", file=sys.stderr)
        return True

    set_human_name_called = False
    set_human_health_called = False
    set_human_buy_gold_value_called = False
    set_human_kill_gold_value_called = False

    on_fns.spawn(globals)

    if not set_human_name_called:
        print(
            f"{entity.decode()} its on_spawn() did not call set_human_name()",
            file=sys.stderr,
        )
        return True
    if not set_human_health_called:
        print(
            f"{entity.decode()} its on_spawn() did not call set_human_health()",
            file=sys.stderr,
        )
        return True
    if not set_human_buy_gold_value_called:
        print(
            f"{entity.decode()} its on_spawn() did not call set_human_buy_gold_value()",
            file=sys.stderr,
        )
        return True
    if not set_human_kill_gold_value_called:
        print(
            f"{entity.decode()} its on_spawn() did not call set_human_kill_gold_value()",
            file=sys.stderr,
        )
        return True

    return False


def call_tool_on_spawn(entity, on_fns, globals):
    global set_tool_name_called
    global set_tool_buy_gold_value_called

    if not on_fns.spawn:
        print(f"{entity.decode()} is missing on_spawn()", file=sys.stderr)
        return True

    set_tool_name_called = False
    set_tool_buy_gold_value_called = False

    on_fns.spawn(globals)

    if not set_tool_name_called:
        print(
            f"{entity.decode()} its on_spawn() did not call set_tool_name()",
            file=sys.stderr,
        )
        return True
    if not set_tool_buy_gold_value_called:
        print(
            f"{entity.decode()} its on_spawn() did not call set_tool_buy_gold_value()",
            file=sys.stderr,
        )
        return True

    return False


def print_opponent_humans(human_files):
    global human_on_spawn_data

    for i, file in enumerate(human_files):
        globals = (ctypes.c_byte * file.globals_size)()
        file.init_globals_fn(globals, 0)

        on_fns = HumanOnFns.from_address(file.on_fns)

        if call_human_on_spawn(file.entity, on_fns, globals):
            return True

        human = human_on_spawn_data

        print(f"{i + 1}. {human.name}, worth {human.kill_gold_value} gold when killed")

        call_human_on_despawn(on_fns, globals)

    print("")
    return False


def pick_opponent():
    print(f"You have {data.gold} gold\n")

    human_files = get_type_files("human")

    if print_opponent_humans(human_files):
        return

    opponent_number = read_size(
        f"Type the number next to the human you want to fight:\n"
    )
    if opponent_number == None:
        return

    if opponent_number == 0:
        print("The minimum number you can enter is 1", file=sys.stderr)
        return

    if opponent_number > len(human_files):
        print(
            f"The maximum number you can enter is {len(human_files)}",
            file=sys.stderr,
        )
        return

    opponent_index = opponent_number - 1

    file = human_files[opponent_index]

    data.human_globals[OPPONENT_INDEX] = (ctypes.c_byte * file.globals_size)()
    file.init_globals_fn(data.human_globals[OPPONENT_INDEX], OPPONENT_INDEX)

    on_fns = HumanOnFns.from_address(file.on_fns)

    if call_human_on_spawn(file.entity, on_fns, data.human_globals[OPPONENT_INDEX]):
        return

    human = replace(human_on_spawn_data)

    human.on_fns = on_fns

    human.id = OPPONENT_INDEX
    human.opponent_id = PLAYER_INDEX

    human.max_health = human.health

    data.humans[OPPONENT_INDEX] = human
    data.human_dlls[OPPONENT_INDEX] = file.dll

    # Give the opponent a random tool
    tool_files = get_type_files("tool")
    tool_index = random.randrange(len(tool_files))

    file = tool_files[tool_index]

    data.tool_globals[OPPONENT_INDEX] = (ctypes.c_byte * file.globals_size)()
    file.init_globals_fn(data.tool_globals[OPPONENT_INDEX], OPPONENT_INDEX)

    on_fns = ToolOnFns.from_address(file.on_fns)

    if call_tool_on_spawn(file.entity, on_fns, data.tool_globals[OPPONENT_INDEX]):
        return

    tool = replace(tool_on_spawn_data)

    tool.on_fns = on_fns

    tool.human_parent_id = OPPONENT_INDEX

    data.tools[OPPONENT_INDEX] = tool
    data.tool_dlls[OPPONENT_INDEX] = file.dll

    data.state = State.FIGHTING


def print_tools(tool_files):
    global tool_on_spawn_data

    for i, file in enumerate(tool_files):
        globals = (ctypes.c_byte * file.globals_size)()
        file.init_globals_fn(globals, 0)

        on_fns = ToolOnFns.from_address(file.on_fns)

        if call_tool_on_spawn(file.entity, on_fns, globals):
            return True

        tool = tool_on_spawn_data

        print(f"{i + 1}. {tool.name}, costing {tool.buy_gold_value} gold")

        call_tool_on_despawn(on_fns, globals)

    print("")
    return False


def pick_tools():
    print(f"You have {data.gold} gold\n")

    tool_files = get_type_files("tool")

    if print_tools(tool_files):
        return

    tool_number = read_size(
        f"Type the number next to the tool you want to buy{" (type 0 to skip)" if data.player_has_tool else ""}:\n"
    )
    if tool_number == None:
        return

    if tool_number == 0:
        if data.player_has_tool:
            data.state = State.PICKING_OPPONENT
            return

        print("The minimum number you can enter is 1", file=sys.stderr)
        return

    if tool_number > len(tool_files):
        print(
            f"The maximum number you can enter is {len(tool_files)}",
            file=sys.stderr,
        )
        return

    if data.tools[PLAYER_INDEX].on_fns:
        call_tool_on_despawn(
            data.tools[PLAYER_INDEX].on_fns, data.tool_globals[PLAYER_INDEX]
        )

    tool_index = tool_number - 1

    file = tool_files[tool_index]

    data.tool_globals[PLAYER_INDEX] = (ctypes.c_byte * file.globals_size)()
    file.init_globals_fn(data.tool_globals[PLAYER_INDEX], PLAYER_INDEX)

    on_fns = ToolOnFns.from_address(file.on_fns)

    if call_tool_on_spawn(file.entity, on_fns, data.tool_globals[PLAYER_INDEX]):
        return

    tool = replace(tool_on_spawn_data)

    if tool.buy_gold_value > data.gold:
        print("You don't have enough gold to pick that tool", file=sys.stderr)
        return
    data.gold -= tool.buy_gold_value

    tool.on_fns = on_fns

    tool.human_parent_id = PLAYER_INDEX

    data.tools[PLAYER_INDEX] = tool
    data.tool_dlls[PLAYER_INDEX] = file.dll

    data.player_has_tool = True

    data.state = State.PICKING_OPPONENT


def print_playable_humans(human_files):
    global human_on_spawn_data

    for i, file in enumerate(human_files):
        globals = (ctypes.c_byte * file.globals_size)()
        file.init_globals_fn(globals, 0)

        on_fns = HumanOnFns.from_address(file.on_fns)

        if call_human_on_spawn(file.entity, on_fns, globals):
            return True

        human = human_on_spawn_data

        print(f"{i + 1}. {human.name}, costing {human.buy_gold_value} gold")

        call_human_on_despawn(on_fns, globals)

    print("")
    return False


def pick_player():
    print(f"You have {data.gold} gold\n")

    human_files = get_type_files("human")

    if print_playable_humans(human_files):
        return

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

    if player_number > len(human_files):
        print(
            f"The maximum number you can enter is {len(human_files)}",
            file=sys.stderr,
        )
        return

    if data.humans[PLAYER_INDEX].on_fns:
        call_human_on_despawn(
            data.humans[PLAYER_INDEX].on_fns, data.human_globals[PLAYER_INDEX]
        )

    player_index = player_number - 1

    file = human_files[player_index]

    data.human_globals[PLAYER_INDEX] = (ctypes.c_byte * file.globals_size)()
    file.init_globals_fn(data.human_globals[PLAYER_INDEX], PLAYER_INDEX)

    on_fns = HumanOnFns.from_address(file.on_fns)

    if call_human_on_spawn(file.entity, on_fns, data.human_globals[PLAYER_INDEX]):
        return

    human = replace(human_on_spawn_data)

    if human.buy_gold_value > data.gold:
        print("You don't have enough gold to pick that human", file=sys.stderr)
        return
    data.gold -= human.buy_gold_value

    human.on_fns = on_fns

    human.id = PLAYER_INDEX
    human.opponent_id = OPPONENT_INDEX

    human.max_health = human.health

    data.humans[PLAYER_INDEX] = human
    data.human_dlls[PLAYER_INDEX] = file.dll

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

    for reload_index in range(reloads_size):
        reload = reloads[reload_index]

        file = reload.file

        for i in range(2):
            if reload.old_dll == data.human_dlls[i]:
                data.human_dlls[i] = file.dll

                data.human_globals[i] = (ctypes.c_byte * file.globals_size)()
                file.init_globals_fn(data.human_globals[i], i)

                data.humans[i].on_fns = (
                    HumanOnFns.from_address(file.on_fns) if file.on_fns else None
                )

        for i in range(2):
            if reload.old_dll == data.tool_dlls[i]:
                data.tool_dlls[i] = file.dll

                data.tool_globals[i] = (ctypes.c_byte * file.globals_size)()
                file.init_globals_fn(data.tool_globals[i], i)

                data.tools[i].on_fns = (
                    ToolOnFns.from_address(file.on_fns) if file.on_fns else None
                )


@ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p)
def runtime_error_handler(reason, type, on_fn_name, on_fn_path):
    print(
        f"grug runtime error in {on_fn_name.decode()}(): {reason.decode()}, in {on_fn_path.decode()}",
        file=sys.stderr,
    )


def main():
    global grug_dll, on_fn_name, on_fn_path

    # RTLD_GLOBAL here allows mods to call functions from adapter.c
    adapter_dll = ctypes.PyDLL("./adapter.so", os.RTLD_GLOBAL)

    adapter_dll.init.restype = None
    adapter_dll.init()

    # RTLD_GLOBAL here allows mods to access grug_runtime_error_type from grug.c
    grug_dll = ctypes.PyDLL("./grug/grug.so", os.RTLD_GLOBAL)

    error = GrugError.in_dll(grug_dll, "grug_error")

    grug_dll.grug_init.restype = ctypes.c_bool

    if grug_dll.grug_init(runtime_error_handler, b"mod_api.json", b"mods"):
        raise Exception(
            f"grug_init() error: {error.msg.decode()} (detected by grug.c:{error.grug_c_line_number})"
        )

    grug_dll.grug_regenerate_modified_mods.restype = ctypes.c_bool

    grug_dll.grug_toggle_on_fns_mode.restype = None
    grug_dll.grug_are_on_fns_in_safe_mode.restype = ctypes.c_bool

    loading_error_in_grug_file = ctypes.c_bool.in_dll(
        grug_dll, "grug_loading_error_in_grug_file"
    )

    on_fn_name = ctypes.c_char_p.in_dll(grug_dll, "grug_on_fn_name")

    on_fn_path = ctypes.c_char_p.in_dll(grug_dll, "grug_on_fn_path")

    while True:
        if grug_dll.grug_regenerate_modified_mods():
            if error.has_changed:
                if loading_error_in_grug_file:
                    print(
                        f"grug loading error: {error.msg.decode()}, in {error.path.decode()} (detected by grug.c:{error.grug_c_line_number})",
                        file=sys.stderr,
                    )
                else:
                    print(
                        f"grug loading error: {error.msg.decode()} (detected by grug.c:{error.grug_c_line_number})",
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
