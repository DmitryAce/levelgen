import json, time
from pathlib import Path
import copy
from collections import namedtuple

class Directed:
    def __init__(self, **mapping):
        self.mapping = mapping
        self.rotations = dict(left='up', up='right', right='down', down='left')
        self.rotation = 'up'

    def __getitem__(self, action):
        match self.mapping[action]:
            case 'rotate':
                self.rotation = self.rotations[self.rotation]
                return 'pass'
            case 'move':
                return self.rotation
            case other:
                return other

s1 = dict(north='up', south='down', east='right', west='left', collect='take', trigger='pull', exit='escape')
s2 = dict(up='up', down='down', rigth='right', left='left', take='take', pull='pull', escape='escape')
s3 = Directed(turn='rotate', go='move', pick='take', switch='pull', flee='escape')

move = {
    "up": (0, -1),
    "down": (0, 1),
    "right": (1, 0),
    "left": (-1, 0),
}

def xorshift32(x):
    x ^= x << 13
    x ^= x >> 17
    x ^= x << 5
    return x & 0xffffffff


class Rand:
    def __init__(self, seed, algo=xorshift32, rand_max=0xffffffff):
        self.algo = algo
        self.rand_max = rand_max
        self.seed = seed

    def random(self):
        self.seed = self.algo(self.seed)
        return self.seed

    def set_seed(self, seed):
        self.seed = seed

    def randint(self, low, high):
        return low + self.random() % (high - low + 1)

    def choice(self, seq):
        return seq[self.randint(0, len(seq) - 1)]

    def randf(self):
        return self.random() / self.rand_max

    def uniform(self, low, high):
        return low + (high - low) * self.randf()


def options(i, j, count):
    """Генерирует возможные варианты координат,
    исходя из текущей позиции и количества."""
    x = [(i + k, j) for k in range(count)]
    y = [(i, j + k) for k in range(count)]
    return x, x[::-1], y, y[::-1]


def rule(before, after):
    """Создает правило замены символов на карте."""

    def apply(board):
        a, b = len(board), len(board[0])
        matches = []
        for i in range(a):
            for j in range(b):
                for option in options(i, j, len(before)):
                    if all(x < a and y < b for x, y in option):
                        if before == ''.join(board[x][y] for x, y in option):
                            matches.append(option)
        if matches:
            option = random.choice(matches)
            for (x, y), r in zip(option, after):
                board[x][y] = r
            return True
        return False

    return apply


def interp(board, init, rules):
    """Применяет заданные правила к карте."""
    a, b = len(board) // 2, len(board[0]) // 2
    board[a][b:b + len(init)] = init
    start_time = time.time()  # Запоминаем время начала выполнения цикла
    while rules:
        if time.time() - start_time >= 5:
            break
        for rule in rules:
            if rule(board):
                break

    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == 'B':
                board[y][x] = '#'
            elif board[y][x] in ['W', 'G', 'R', 'A']:
                board[y][x] = ' '


def addwalls(board, sizex, sizey):
    """Добавляет стены к карте"""
    # Верхняя граница
    for x in range(0, sizex):
        if board[0][x] != "#":
            board.insert(0, ["#"] * (sizex))
            sizey += 1
            break

    # Нижняя граница
    for x in range(0, sizex):
        if board[sizey - 1][x] != "#":
            board.append(["#"] * (sizex))
            sizey += 1
            break

    # левая граница
    for y in range(0, sizey):
        if board[y][0] != "#":
            for x in range(0, sizey):
                board[x].insert(0, "#")
            sizex += 1
            break

    # Правая граница
    for y in range(0, sizey):
        if board[y][-1] != "#":
            for x in range(0, sizey):
                board[x].append("#")
            sizex += 1
            break

    return board, sizex, sizey


def init_plot(difficulty):
    """Инициализация сюжета"""
    events = ["coins", "exit", "treasure"]
    gen_method = ["MazeBacktracker", "MazeGrowth", "NoDeadEnds"]
    plot = []


    gen_method = random.choice(gen_method)

    match difficulty:
        case 1:
            coin_chance = 0.5
        case 2:
            coin_chance = 0.35
        case 3:
            coin_chance = 0

    player_set = random.randint(1, 3)
    rooms = difficulty

    for i in range(0, difficulty):
        while True:
            temp = random.choice(events)
            if not (temp in plot):
                plot.append(temp)
                break

    return plot, player_set, rooms, coin_chance, gen_method


def init_map(difficulty, gen_method):
    """Инициализация карты"""

    height, width = difficulty * 8, difficulty * 8
    board = [['B' for _ in range(width)] for _ in range(height)]

    # Gen Map Based on NAM
    match gen_method:
        case "MazeGrowth":
            interp(board, 'BWG', [
                rule('WBB', 'WAW')
            ])
        case "MazeBacktracker":
            interp(board, 'BRGW', [
                rule('RBB', 'GGR'),
                rule('RGG', 'WWR'),
            ])
        case "NoDeadEnds":
            interp(board, 'BRWA', [
                rule('RBB', 'WAR'),
                rule('WBB', 'WAR'),
                rule('RBR', 'WAW'),
                rule('RBW', 'WAW'),
            ])

    board, width, height = addwalls(board, width, height)

    tiles = []
    for y in range(1, len(board) - 1):
        for x in range(1, len(board[y]) - 1):
            tiles.append([x, y])

    return board, width, height, tiles


def get_size(board):
    width = len(board[0])
    height = len(board)
    return width, height


def format_treasures(count):
    return f"{count} сокровище" if count == 1 else f"{count} сокровища"


def generate_treasures(board, rooms, tiles):
    width, height = get_size(board)

    treasure_coordinates = []
    while rooms:
        x = random.randint(2, width - 3)
        y = random.randint(2, height - 3)

        # G fix
        if x == 3:
            x -= 1
        elif x == width - 4:
            x += 1
        if y == height - 4:
            y += 1
        elif y == 3:
            y -= 1

        if not any(abs(x - tx) < 6 and abs(y - ty) < 6 for tx, ty in treasure_coordinates):
            treasure_coordinates.append([x, y])
            board = clear_room(board, x, y)
            board[y][x] = "t"
            rooms -= 1

            # Верхняя и нижняя границы
            for i in range(x - 2, x + 3):
                board[y - 2][i] = '#'
                board[y + 2][i] = '#'
                if [i, y + 3] in tiles:
                    board[y + 3][i] = ' '
                if [i, y - 3] in tiles:
                    board[y - 3][i] = ' '

            # углы
            if [x - 3, y - 3] in tiles:
                board[y - 3][x - 3] = ' '
            if [x + 3, y - 3] in tiles:
                board[y - 3][x + 3] = ' '
            if [x - 3, y + 3] in tiles:
                board[y + 3][x - 3] = ' '
            if [x + 3, y + 3] in tiles:
                board[y + 3][x + 3] = ' '

            # Правая и левая границы
            for i in range(y - 2, y + 3):
                board[i][x + 2] = '#'
                board[i][x - 2] = '#'
                if [x - 3, i] in tiles:
                    board[i][x - 3] = ' '
                if [x + 3, i] in tiles:
                    board[i][x + 3] = ' '

    return treasure_coordinates, board


def clear_room(board, x, y):
    for i in range(x - 1, x + 2):
        for j in range(y - 1, y + 2):
            board[j][i] = ' '
    return board


def generate_keys(board, treasure_coordinates, keys):
    width, height = get_size(board)

    check = True
    while keys:
        x = random.randint(1, width - 1)
        y = random.randint(1, height - 1)

        flag = True

        if check:
            for center in treasure_coordinates:
                # Гарантируем хотя бы 1 ключ вне сокровищниц
                for i in range(center[0] - 2, center[0] + 2):
                    for j in range(center[1] - 2, center[1] + 2):
                        if [x, y] == [i, j]:
                            flag = False
        if flag:
            if board[y][x] == " ":
                board[y][x] = "k"
                keys -= 1
                check = False
        else:
            continue

    return board


def generate_doors(board, tiles, x, y):
    width, height = get_size(board)

    while True:
        # Расположение двери
        door = random.randint(1, 4)
        # Выбор стороны для двери и проверка что вход не находится на краю карты (внутри блока)
        if door == 1 and y != 2:
            k = random.randint(1, 3)
            if not ([x - 2 + k, y - 2] in tiles): continue
            board[y - 2][x - 2 + k] = 'd'
            break
        elif door == 2 and x != width - 3:
            k = random.randint(1, 3)
            if not ([x + 2, y - 2 + k] in tiles): continue
            board[y - 2 + k][x + 2] = 'd'
            break
        elif door == 3 and y != height - 3:
            k = random.randint(1, 3)
            if not ([x - 2 + k, y + 2] in tiles): continue
            board[y + 2][x - 2 + k] = 'd'
            break
        elif door == 4 and x != 2:
            k = random.randint(1, 3)
            if not ([x - 2, y - 2 + k] in tiles): continue
            board[y - 2 + k][x - 2] = 'd'
            break
    return board


def generate_coins(board, coin_chance):
    width, height = get_size(board)
    total_space = sum(row.count(' ') for row in board)
    coins_goal = random.randint(int(total_space * 0.10), int(total_space * 0.20))
    to_task = coins_goal

    # Увеличиваем кол-во монет на карте, чтобы боло с запасом
    coins_goal += int(coins_goal * coin_chance)

    while coins_goal:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)

        if board[y][x] == " ":
            board[y][x] = "1"
            coins_goal -= 1

    return board, to_task

def generate_exit(board, width, height):
    while True:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)

        if board[y][x] == " ":
            return x, y


def check_treasure_proximity(x, treasure_coordinates):
    flag = True
    for center in treasure_coordinates:
        if (center[0] - 2 < x < center[0] + 2) and (center[1] == 2 or center[1] == 3):
            flag = False
            break
    return flag


def case1(board):
    width, height = get_size(board)

    x, y = generate_exit(board, width, height)
    board[y][x] = "x"

    x, y = generate_exit(board, width, height)
    board[y][x] = "l"

    return board


def case2(board, treasure_coordinates):
    width, height = get_size(board)
    exits = random.randint(1, 3)
    to_task = exits

    while exits:
        direction = random.randint(1, 4)

        # Большое количество проверок для того, чтобы выход не появился внутри сокровищницы
        match direction:
            case 1:
                x = random.randint(1, width - 2)
                if board[0][x] == "#" and board[1][x] != "#":
                    if check_treasure_proximity(x, treasure_coordinates):
                        board[0][x] = "E"
                        exits -= 1
            case 2:
                y = random.randint(1, height - 2)
                if board[y][-1] == "#" and board[y][-2] != "#":
                    if check_treasure_proximity(x, treasure_coordinates):
                        board[y][-1] = "E"
                        exits -= 1
            case 3:
                x = random.randint(1, width - 2)
                if board[-1][x] == "#" and board[-2][x] != "#":
                    if check_treasure_proximity(x, treasure_coordinates):
                        board[-1][x] = "E"
                        exits -= 1
            case 4:
                y = random.randint(1, height - 2)
                if board[y][0] == "#" and board[y][1] != "#":
                    if check_treasure_proximity(x, treasure_coordinates):
                        board[y][0] = "E"
                        exits -= 1
    return board, to_task


def make_task(rooms, exit_task, coins_task = 0):
    task = []
    data_for_check = {}  # Создаем словарь для проверки решаемости

    if rooms > 0:
        data_for_check["keys"] = rooms
        task.append(
            f"Необходимо найти {format_treasures(rooms)}, чтобы собирать " + \
            "сокровища нужно подбирать ключи.")
    if coins_task > 0:
        data_for_check["coins"] = coins_task
        task.append(f"Необходимо собрать {coins_task} *.")
    if exit_task == 100:
        data_for_check["escape2"] = True
        task.append("Сбегите с локации. Чтобы активировать выход нужно переключить рычаг.")
    elif exit_task != 0:
        task.append("Escape from DandyBot.")
        data_for_check["escape1"] = exit_task

    return task, data_for_check


def map_generator(difficulty):
    plot, player_set, rooms, coin_chance, gen_method = init_plot(difficulty)
    board, width, height, tiles = init_map(difficulty, gen_method)

    if "treasure" in plot:
        treasure_coordinates, board = generate_treasures(board, rooms, tiles)
        board = generate_keys(board, treasure_coordinates, rooms)
        for x, y in treasure_coordinates:
            board = generate_doors(board, tiles, x, y)
    if "coins" in plot:
        board, coins_task = generate_coins(board, coin_chance)
    if "exit" in plot:
        # Вариация сюжета с выходами
        mode = random.randint(1, 2)
        match mode:
            # Выход с рычагом
            case 1:
                board = case1(board)
                exit_task = 100
            # 1-3 Выхода, есть фейковые
            case 2:
                board, exit_task = case2(board, treasure_coordinates)

    task, data_for_check = make_task(rooms, exit_task, coins_task)
    print(task, data_for_check)

    # --SPAWNPOINT--
    spawnpoint = []
    while True:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)

        if not ([x, y] in treasure_coordinates):
            flag = True
            for center in treasure_coordinates:
                for i in range(center[0] - 3, center[0] + 3):
                    for j in range(center[1] - 3, center[1] + 3):
                        if [x, y] == [i, j]:
                            flag = False
            if flag:
                if board[y][x] == " ":
                    spawnpoint = [x, y]
                    break
            else:
                continue
        else:
            continue

    return board, task, spawnpoint, data_for_check, player_set


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


def escapeE(state, board, x, y, spawn_point):
    if state.escaped in [1, 2]:
        return state._replace(x=x, y=y)
    if len(find_E_locations(board, spawn_point)) > 1 and (x, y) != \
            find_E_locations(board, spawn_point)[0][0]:
        return state._replace(x=x, y=y, escaped=2)
    return state._replace(x=x, y=y, escaped=1)


def go(board, state, spawn_point, x=0, y=0):
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
        return escapeE(state, board, x, y, spawn_point)
    return state._replace(x=x, y=y)


def collect(board, state, mark, name):
    x, y = state.x, state.y
    exists = board[y][x] == mark
    collected = (x, y) in getattr(state, name)
    if exists and not collected:
        new = getattr(state, name).union({(x, y)})
        return state._replace(**{name: new})
    return state


def make_dandybot_model(board, start, is_goal, spawn_point):
    def act(state):
        state = collect(board, state, '1', 'money')
        state = collect(board, state, 'k', 'keys')
        state = collect(board, state, 't', 'treasures')
        state = collect(board, state, 'l', 'lever')
        return state

    return make_model({}, start, is_goal, [
        lambda state: act(go(board, state, spawn_point, y=-1)),
        lambda state: act(go(board, state, spawn_point, y=+1)),
        lambda state: act(go(board, state, spawn_point, x=-1)),
        lambda state: act(go(board, state, spawn_point, x=+1)),
    ])


def analyze(board, init, goal, spawn_point):
    model = make_dandybot_model(board, init, goal, spawn_point)
    states = list(model)
    for i, state in enumerate(states):
        if goal(state):
            return True
    return False


def check_level(board, spawn, plot):
    simple_puzzle = []
    if "treasures" in plot:
        term1 = plot["treasures"]
    else:
        term1 = 0

    if "coins" in plot:
        term2 = plot["coins"]
    else:
        term2 = 0

    if "escape2" in plot:
        termL = 1
        term3 = 1
    elif "escape1" in plot:
        term3 = plot["escape1"]
        termL = 0
    else:
        term3 = 0
        termL = 0

    for z in board:
        simple_puzzle.append("".join(z))
    simple_puzzle_goal = lambda state: len(state.treasures) == term1 and len(state.money) == term2 and (
                len(state.lever) == termL) and state.escaped == term3
    playability = analyze(simple_puzzle, init(spawn[0], spawn[1]), simple_puzzle_goal, spawn)
    return playability


def check_solution(group, task, variant, code):
    seed = sum([ord(i) for i in list(group)]) + task + variant
    random.set_seed(seed)
    board, task, spawnpoint, data_for_check, player_set = map_generator(difficulty)
    board_temp = copy.deepcopy(board)

    playability = not (check_level(board_temp, spawnpoint, data_for_check))

    # Если уровень невалиден, то запускаем генерацию заново
    while playability:
        board, task, spawnpoint, data_for_check, player_set = map_generator(difficulty)
        board_temp = copy.deepcopy(board)
        playability = not (check_level(board_temp, spawnpoint, data_for_check))

    for h in board:
        print('"' + ''.join(h) + '",')
    print("spawnpoint = " + str(spawnpoint))

    # Проверка скрипта студента
    player_pos = spawnpoint
    turns = 10000
    player_keys = 0
    coins = 0
    treasures = 0
    opened = 0
    escaped = 0
    player_script = dict()
    exec(code, player_script)
    print(player_set)

    while turns:
        if escaped:
            break
        turns -= 1
        match player_set:
            case 1:
                act = s1[player_script["play_game"](board, player_pos)]
            case 2:
                act = s2[player_script["play_game"](board, player_pos)]
            case 3:
                act = s3[player_script["play_game"](board, player_pos)]
            case 4:
                continue

        type = board[player_pos[1]][player_pos[0]]

        match act:
            case "take":
                match type:
                    case "k":
                        player_keys += 1
                        board[player_pos[1]][player_pos[0]] = " "
                        continue
                    case "1":
                        coins += 1
                        board[player_pos[1]][player_pos[0]] = " "
                        continue
                    case "t":
                        treasures += 1
                        board[player_pos[1]][player_pos[0]] = " "
                        continue
                continue
            case "pull":
                match type:
                    case "l":
                        board[player_pos[1]][player_pos[0]] = "L"
                        opened += 1
                        continue
                continue
            case "escape":
                match type:
                    case "E":
                        # Проверка на ложные выходы
                        if len(find_E_locations(board, spawnpoint)) > 1 and player_pos != \
                                find_E_locations(board, spawnpoint)[0][0]:
                            return False
                        escaped = 1
                        continue
                    case "x":
                        if opened:
                            escaped = 1
                        continue
                continue

        # Движение
        if (board[player_pos[1] + move[act][1]][player_pos[0] + move[act][0]] != "#" and 0 <= player_pos[0] +
            move[act][0] <= len(board[0])) and 0 <= player_pos[1] + move[act][1] <= len(board):
            if (board[player_pos[1] + move[act][1]][player_pos[0] + move[act][0]] == "d"):
                if player_keys:
                    player_keys -= 1
                    board[player_pos[1] + move[act][1]][player_pos[0] + move[act][0]] = " "
                    player_pos = (player_pos[0] + move[act][0], player_pos[1] + move[act][1])
                else:
                    continue
            else:
                player_pos = (player_pos[0] + move[act][0], player_pos[1] + move[act][1])
        else:
            continue

    for h in board:
        print('"' + ''.join(h) + '",')
    print("spawnpoint = " + str(spawnpoint))

    win = True
    if "coins" in data_for_check:
        if coins < int(data_for_check["coins"]): win = False
    if "exit" in data_for_check:
        if escaped != 1: win = False
    if "treasure" in data_for_check:
        if treasures != int(data_for_check["treasure"]): win = False
    return win
 

difficulty = 3
random = Rand(1)

if __name__ == '__main__':
    TESTS = [{"ИКБО-03-22": [list(range(40)), list(range(40))]}]
    GROUPS, TASKS = ["ИКБО-03-22"], [0, 1]

    code = """
def play_game(board, player_pos):
    if board[player_pos[1]][player_pos[0]] == "1":
        return "take"
    else:
        return width_search((player_pos[0], player_pos[1]), board)[0]
    
def get_directions(path_points):
    directions = {
        (1, 0): "go_east",
        (-1, 0): "go_west",
        (0, 1): "go_south",
        (0, -1): "go_north"
    }
    return [directions[(p[0]-path_points[i][0], p[1]-path_points[i][1])] for i, p in enumerate(path_points[1:])]

def width_search(source_point, board):
    queue, reached, parents = [source_point], {source_point}, {}

    while queue:
        current = queue.pop(0)
        if board[current[1]][current[0]] == "1":
            path_points = [current]
            while path_points[-1] in parents:
                path_points.append(parents[path_points[-1]])
            return get_directions(path_points[::-1])
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            p = (current[0] + dx, current[1] + dy)
            if 0 < p[0] < len(board[0]) and 0 < p[1] < len(board) and (not (board[p[1]][p[0]] in ["#", "d"])) and p not in reached:
                queue.append(p)
                reached.add(p) 
                parents[p] = current  
    return "pass"
"""

    check_solution("ИКБО-03-22", 13, 4, code)
