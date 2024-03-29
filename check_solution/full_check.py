from collections import namedtuple


def make_model(graph, state, is_goal, actions):
    if state in graph:
        return
    graph[state] = set()
    if is_goal(state):
        return
    for action in actions:
        new = action(state)
        if new != state:
            graph[state].add(new)
            make_model(graph, new, is_goal, actions)
    return graph


State = namedtuple('State', 'x y money treasures keys doors lever escaped')


def init(x, y):
    empty = frozenset()
    return State(x, y, empty, empty, empty, empty, empty, 0)


def open(state, x, y):
    if (x, y) in state.doors:
        return state._replace(x=x, y=y)
    keys = len(state.keys)
    open = len(state.doors)
    if keys - open > 0:
        doors = state.doors.union({(x, y)})
        return state._replace(x=x, y=y, doors=doors)
    return state


def escapeX(state, x, y):
    if state.escaped in [1, 2]:
        return state._replace(x=x, y=y)
    if len(state.lever) == 0:
        return state._replace(x=x, y=y)
    return state._replace(x=x, y=y, escaped=1)


def find_E_locations(grid, start):
    distances = {}
    a_x, a_y = start

    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == 'E':
                distance = abs(a_x - i) + abs(a_y - j)
                distances[(i, j)] = distance

    sorted_distances = sorted(distances.items(), key=lambda x: x[1], reverse=True)
    return sorted_distances


def escapeE(state, board, x, y):
    if state.escaped in [1, 2]:
        return state._replace(x=x, y=y)
    if len(find_E_locations(board, spawn_point)) > 1 and (x, y) != \
            find_E_locations(board, spawn_point)[0][0]:
        return state._replace(x=x, y=y, escaped=2)
    return state._replace(x=x, y=y, escaped=1)


def go(board, state, x=0, y=0):
    mx = len(board[0]) - 1
    my = len(board) - 1
    x = max(min(state.x + x, mx), 0)
    y = max(min(state.y + y, my), 0)
    if board[y][x] == '#':
        return state
    if board[y][x] == 'd':
        return open(state, x, y)
    if board[y][x] == 'x':
        return escapeX(state, x, y)
    if board[y][x] == 'E':
        return escapeE(state, board, x, y)
    return state._replace(x=x, y=y)


def collect(board, state, mark, name):
    x, y = state.x, state.y
    exists = board[y][x] == mark
    collected = (x, y) in getattr(state, name)
    if exists and not collected:
        new = getattr(state, name).union({(x, y)})
        return state._replace(**{name: new})
    return state


def make_dandybot_model(board, start, is_goal):
    def act(state):
        state = collect(board, state, '1', 'money')
        state = collect(board, state, 'k', 'keys')
        state = collect(board, state, 't', 'treasures')
        state = collect(board, state, 'l', 'lever')
        return state

    return make_model({}, start, is_goal, [
        lambda state: act(go(board, state, y=-1)),
        lambda state: act(go(board, state, y=+1)),
        lambda state: act(go(board, state, x=-1)),
        lambda state: act(go(board, state, x=+1)),
    ])


def make_detailed_dandybot_model(board, start, is_goal):
    return make_model({}, start, is_goal, [
        lambda state: go(board, state, y=-1),
        lambda state: go(board, state, y=+1),
        lambda state: go(board, state, x=-1),
        lambda state: go(board, state, x=+1),
        lambda state: collect(board, state, '1', 'money'),
        lambda state: collect(board, state, 'k', 'keys'),
        lambda state: collect(board, state, 't', 'treasures'),
        lambda state: collect(board, state, 'l', 'lever')
    ])


def make_simplified_dandybot_model(board, start, is_goal):
    graph = make_dandybot_model(board, start, is_goal)
    merged = {}
    for state in graph:
        key = state._replace(x=0, y=0)
        merged.setdefault(key, set())
        for target in graph[state]:
            merged[key].add(target._replace(x=0, y=0))
    return merged


def analyze(board, init, goal):
    model = make_simplified_dandybot_model(board, init, goal)
    states = list(model)
    for i, state in enumerate(states):
        if goal(state):
            return True
    return False


spawn_point = (1, 1)
simple_puzzle_init = init(1, 1)
simple_puzzle_goal = lambda state: len(state.treasures) == 2 and len(state.money) == 1 and (
            len(state.lever) == 0) and state.escaped == 1
simple_puzzle = [
    "#########",
    "E   d  t#",
    "#   #####",
    "# 1   dk#",
    "#  #k #t#",
    "#########"
]

print(analyze(simple_puzzle, simple_puzzle_init, simple_puzzle_goal))