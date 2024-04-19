from collections import namedtuple


def make_model(graph, fstate, is_goal, actions):
    queue = [fstate]
    while queue:
        state = queue.pop(0)

        if state in graph:
            continue

        graph[state] = set()

        if is_goal(state):
            continue

        for action in actions:
            new = action(state)
            if new != state:
                graph[state].add(new)
                queue.append(new)

    return graph


State = namedtuple('State', 'cords money treasures keys doors exits')

def init(x, y):
    empty = frozenset()
    return State(((x, y),), empty, empty, empty, empty, empty)

def open(state, x, y):
    if (x, y) in state.doors:
        cords = state.cords + ((x,y),)
        return state._replace(cords=cords)
    keys = len(state.keys)
    open = len(state.doors)
    if keys - open > 0:
        doors = state.doors.union({(x, y)})
        return state._replace(cords=((x,y),), doors=doors)
    return state

def go(board, state, x=0, y=0):
    mx = len(board[0]) - 1
    my = len(board) - 1
    x = max(min(state.cords[-1][0] + x, mx), 0)
    y = max(min(state.cords[-1][1] + y, my), 0)
    if board[y][x] == '#':
        return state
    if board[y][x] == 'd':
        return open(state, x, y)
    cords = state.cords + ((x,y),)
    return state._replace(cords=cords)

def collect(board, state, mark, name):
    x, y = state.cords[-1][0], state.cords[-1][1]
    exists = board[y][x] == mark
    collected = (x, y) in getattr(state, name)
    if exists and not collected:
        new = getattr(state, name).union({(x, y)})
        return state._replace(cords=((x,y),), **{name: new})
    return state

def make_dandybot_model(board, start, is_goal):
    def act(state):
        state = collect(board, state, '1', 'money')
        state = collect(board, state, 'k', 'keys')
        state = collect(board, state, 't', 'treasures')
        state = collect(board, state, 'E', 'exits')
        return state
    return make_model({}, start, is_goal, [
        lambda state: act(go(board, state, y=-1)),
        lambda state: act(go(board, state, y=+1)),
        lambda state: act(go(board, state, x=-1)),
        lambda state: act(go(board, state, x=+1)),
    ])

def make_simplified_dandybot_model(board, start, is_goal):
    graph = make_dandybot_model(board, start, is_goal)
    merged = {}
    for state in graph:
        key = state._replace(cords= ((0,0),))
        merged.setdefault(key, set())
        for target in graph[state]:
            merged[key].add(target._replace(cords=((0,0),)))
    return merged

def analyze(board, init, goal):
    regular = make_dandybot_model(board, init, goal)
    simple = make_simplified_dandybot_model(board, init, goal)
    print(f'Regular: {len(regular)}, simple: {len(simple)}')


simple_puzzle_init = init(2, 1)
simple_puzzle_goal = lambda state: len(state.money) == 19 and len(state.exits) == 2
simple_puzzle = [
    "#################",
    "#     #     #  1#",
    "# ### # ### # #1#",
    "#      11   # # #",
    "# ####### ### # #",
    "#  1      #   # #",
    "# # ##### # ### #",
    "# #     #   #1  #",
    "# ### #1##### ###",
    "# 1   #1#   #   #",
    "### ### #  ####1#",
    "#  1#  11     # #",
    "#1#1# ####  # # #",
    "#   # 1 1  1# # #",
    "# ###1###1 1#1# #",
    "#1 1      1     #",
    "##########E##E###"
]
simple_puzzle_init = init(2, 1)
simple_puzzle_goal = lambda state: len(state.money) == 4 and len(state.exits) == 1
simple_puzzle = [
    "#################",
    "#     #     #  1#",
    "# ### # ### # #1#",
    "#      11   # # #",
    "# ##   ## ### # #",
    "#E###############"
]

analyze(simple_puzzle, simple_puzzle_init, simple_puzzle_goal)