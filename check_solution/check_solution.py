import json, time
from pathlib import Path
import copy

move = {
    "up": (0,-1),
    "down": (0,1),
    "right": (1,0),
    "left": (-1,0),
}

actions_dict = {
    "set1": {
        "go_north": "up",
        "go_south": "down",
        "go_east": "right",
        "go_west": "left",
        "take": "take",
        "pull_lever": "pull",
        "escape": "escape"
    },
    "set2": {
        "up": "up",
        "down": "down",
        "left": "left",
        "right":  "right",
        "pick_up": "take",
        "pull_lever": "pull",
        "exit": "escape"
    },
    "set3": {
        "go_up": "up",
        "go_down": "down",
        "go_right": "right",
        "go_left": "left",
        "collect": "take",
        "pull_lever": "pull",
        "leave": "escape"
    },
    "set4": {
        "north": "up",
        "south": "down",
        "east": "right",
        "west": "left",
        "take": "take",
        "pull_lever": "pull",
        "depart": "escape"
    },
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


def addwalls(board, sizex, sizey):
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


def map_generator(seed, difficulty, shift):
    for i in range(shift):
        random.random()

    events = ["coins", "exit", "treasure"]
    gen_method = ["MazeBacktracker", "MazeGrowth", "NoDeadEnds"]
    plot = []
    task = []

    # --- RANDOM GAMEPLAY ---
    N = difficulty
    gen_method = random.choice(gen_method)
    width = N*8
    match N:
        case 1:
            coin_chance = 0.5
        case 2:
            coin_chance = 0.35
        case 3:
            coin_chance = 0
    player_set = random.randint(1, 4)
    rooms = N


    # ---MAP---

    height = width

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

    # Заменяем все символы 'B' на '#'
    for y in range(height):
        for x in range(width):
            if board[y][x] == 'B':
                board[y][x] = '#'

    # Заменяем все символы 'W' на ' '
    for y in range(height):
        for x in range(width):
            if board[y][x] == 'W' or board[y][x] == 'G' or board[y][
                x] == 'R' or board[y][x] == 'A':
                board[y][x] = ' '

    board, width, height = addwalls(board, width, height)
    data_for_check = {}  # Создаем словарь для проверки решаемости

    # ---TILES---
    """Сделал чтобы можно было проверить определьные точки 
    при создании сокровищ"""
    tiles = []
    for y in range(1, len(board) - 1):
        for x in range(1, len(board[y]) - 1):
            tiles.append([x, y])

    # ---PLOT---
    for i in range(0, N):
        while True:
            temp = random.choice(events)
            if not (temp in plot):
                plot.append(temp)
                break

    print(seed, " ", plot, " - ", N, ", ", gen_method)

    # --TREASURES--
    # Создаем комнаты
    treasure_coordinates = []
    if "treasure" in plot:
        keys = rooms
        data_for_check["keys"] = rooms

        # Функция для правильного склонения слова "сокровище"
        def format_treasures(count):
            if count == 1:
                return f"{count} сокровище"
            else:
                return f"{count} сокровища"

        task.append(
            f"Необходимо найти {format_treasures(rooms)}, чтобы собирать " + \
            "сокровища нужно подбирать ключи.")

        while rooms:
            x = random.randint(2, width - 3)  # Координаты сокровища
            y = random.randint(2, height - 3)

            # Подбираем точку для сокровища
            if not ([x, y] in treasure_coordinates):
                flag = True
                for center in treasure_coordinates:
                    # Перебираем все клеточки прошлых сокровищниц
                    # Чтобы не наложить их друг на друга
                    for i in range(center[0] - 5, center[0] + 6):
                        for j in range(center[1] - 5, center[1] + 6):
                            if [x, y] == [i, j]:
                                flag = False
                if flag:
                    treasure_coordinates.append([x, y])
                    rooms -= 1
                else:
                    continue
            else:
                continue

            # G fix
            if x == 3:
                x -= 1
            elif x == width - 4:
                x += 1
            if y == height - 4:
                y += 1
            elif y == 3:
                y -= 1

            # Отчищаем комнату
            for i in range(x - 1, x + 2):
                for j in range(y - 1, y + 2):
                    board[j][i] = ' '

            board[y][x] = 't'

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

        # Создаем ключ
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

    # --COINS--
    if "coins" in plot:
        total_space = sum(row.count(' ') for row in board)
        coins_goal = random.randint(int(total_space * 0.10), int(total_space * 0.20))
        data_for_check["coins"] = coins_goal
        task.append(
            f"Необходимо собрать {coins_goal} *.")

        # Увеличиваем кол-во монет на карте, чтобы боло с запасом
        coins_goal += int(coins_goal * coin_chance)

        while coins_goal:
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)

            if board[y][x] == " ":
                board[y][x] = "1"
                coins_goal -= 1

    # --EXIT--
    if "exit" in plot:
        # Вариация сюжета с выходами
        mode = random.randint(1, 2)
        # Случайное количество выходов на карте
        match mode:
            # Выход с рычагом
            case 1:
                data_for_check["escape2"] = True
                task.append(
                    f"Сбегите с локации. Чтобы активировать выход нужно переключить рычаг.")

                while True:
                    x = random.randint(0, width - 1)
                    y = random.randint(0, height - 1)

                    if board[y][x] == " ":
                        board[y][x] = "x"
                        break

                while True:
                    x = random.randint(0, width - 1)
                    y = random.randint(0, height - 1)

                    if board[y][x] == " ":
                        board[y][x] = "l"
                        break

            # 1-3 Выхода, есть фейковые
            case 2:
                exits = random.randint(1, 3)
                data_for_check["escape1"] = exits
                while exits:
                    direction = random.randint(1, 4)

                    # Много проверок учитывают чтобы выход не появился внутри сокровищницы
                    match direction:
                        case 1:
                            x = random.randint(1, width - 2)
                            if board[0][x] == "#" and board[1][x] != "#":
                                flag = True
                                for center in treasure_coordinates:
                                    if (center[0] - 2 < x < center[0] + 2) and (center[1] == 2 or center[1] == 3):
                                        flag = False
                                        break
                                if not flag:
                                    continue
                                else:
                                    board[0][x] = "E"
                                    exits -= 1
                        case 2:
                            y = random.randint(1, height - 2)
                            if board[y][-1] == "#" and board[y][-2] != "#":
                                flag = True
                                for center in treasure_coordinates:
                                    if (center[0] > width - 4) and (center[1] - 2 < y < center[1] + 2):
                                        flag = False
                                        break
                                if not flag:
                                    continue
                                else:
                                    board[y][-1] = "E"
                                    exits -= 1
                        case 3:
                            x = random.randint(1, width - 2)
                            if board[-1][x] == "#" and board[-2][x] != "#":
                                flag = True
                                for center in treasure_coordinates:
                                    if (center[0] - 2 < x < center[0] + 2) and (
                                            center[1] == height - 2 or center[1] == height - 3):
                                        flag = False
                                        break
                                if not flag:
                                    continue
                                else:
                                    board[-1][x] = "E"
                                    exits -= 1
                        case 4:
                            y = random.randint(1, height - 2)
                            if board[y][0] == "#" and board[y][1] != "#":
                                flag = True
                                for center in treasure_coordinates:
                                    if (center[0] < 4) and (center[1] - 2 < y < center[1] + 2):
                                        flag = False
                                        break
                                if not flag:
                                    continue
                                else:
                                    board[y][0] = "E"
                                    exits -= 1

                task.append(
                    f"Escape from DandyBot.")

    # --SPAWNPOINT--
    spawnpoint = []
    while True:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)

        if not ([x, y] in treasure_coordinates):
            flag = True
            for center in treasure_coordinates:
                # Перебираем все клеточки прошлых сокровищниц
                # Чтобы не наложить их друг на друга
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


def bfs(board, source_point, point_type, restritions):
    queue, reached, parents = [source_point], {source_point}, {}
    while queue:
        current = queue.pop(0)
        if board[current[1]][current[0]] == point_type:
            return current
        # Окрестность фон Неймана
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            p = (current[0] + dx, current[1] + dy)
            if 0 <= p[1] < len(board) and 0 <= p[0] < len(board[0]) and not board[p[1]][p[
                0]] in restritions and p not in reached:
                queue.append(p)
                reached.add(p)
                parents[p] = current
    return []


def check_level(board, spawn, plot):
    spawn = tuple(spawn)

    # Проходимость уровня
    playability = True

    # Цикл проверки
    for P, v in plot.items():
        if not playability:
            break

        match P:
            case "keys":
                if v > 1:
                    # Найдём первый ключ (из условия генерации точно находится вне сокровищниц)
                    point = bfs(board, spawn, "k", ["#", "d"])
                    if point:
                        # Подобрали ключ
                        board[point[1]][point[0]] = " "  # Заменяем "k" на " "
                        v -= 1
                        # Пока ключи есть на карте
                        while v:
                            point = bfs(board, spawn, "k", ["#"])
                            if point:
                                board[point[1]][point[0]] = " "  # Заменяем "k" на " "
                                v -= 1
                            else:
                                playability = False
                                break
                    else:
                        playability = False

                else:
                    if not bfs(board, spawn, "k", ["#", "d"]):
                        playability = False

            case "coins":
                while v:
                    point = bfs(board, spawn, "1", ["#"])
                    if point:
                        board[point[1]][point[0]] = " "  # Заменяем "1" на " "
                        v -= 1
                    else:
                        playability = False
                        break

            case "escape2":
                point = bfs(board, spawn, "l", ["#"])
                if point:
                    board[point[1]][point[0]] = " "  # Заменяем "l" на " "
                else:
                    playability = False
                    break
                point = bfs(board, spawn, "x", ["#"])
                if point:
                    board[point[1]][point[0]] = " "  # Заменяем "x" на " "
                else:
                    playability = False
                    break

            case "escape1":
                while v:
                    point = bfs(board, spawn, "E", ["#"])
                    if point:
                        board[point[1]][point[0]] = " "  # Заменяем "E" на " "
                        v -= 1
                    else:
                        playability = False
                        break

    return playability


def check_solution(group, task, variant, code):
    seed = sum([ord(i) for i in list(group)]) + task + variant
    random.set_seed(seed)
    shift = 0
    board, task, spawnpoint, data_for_check, player_set = map_generator(seed, difficulty, shift)
    board_temp = copy.deepcopy(board)

    playability = not (check_level(board_temp, spawnpoint, data_for_check))

    print("INIT: ")
    for i in board:
        print(i)
    print(data_for_check)

    # Если уровень невалиден, то запускаем генерацию заново
    while playability:
        shift += 100
        board, task, spawnpoint, data_for_check, player_set = map_generator(seed, difficulty, shift)
        board_temp = copy.deepcopy(board)
        playability = not (check_level(board_temp, spawnpoint, data_for_check))

    print("\nSHIFT: ", shift, spawnpoint)
    for i in board:
        print('"'+"".join(i)+'",',)
    print(data_for_check)

    # Проверка скрипта студента
    player_pos = spawnpoint
    turns = 10000
    player_keys = 0
    coins = 0
    treasures = 0
    opened = 0
    escaped = 0

    while turns:
        if escaped:
            break
        turns -= 1
        if not play_game(board,  player_pos) in actions_dict["set"+str(player_set)]:
            # Здесь можно уведомлять что неверное действие
            continue
        act = actions_dict["set"+str(player_set)][play_game(board,  player_pos)]
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
                    case "x":
                        board[player_pos[1]][player_pos[0]] = "X"
                        opened += 1
                        continue
                continue
            case "escape":
                match type:
                    case "E":
                        # Просчитать какие выходы фейковые если > 1
                        escaped = 1
                        continue
                    case "L":
                        if opened:
                            escaped = 1
                        continue
                continue

        # Движение
        if (board[player_pos[1]+move[act][1]][player_pos[0]+move[act][0]] != "#"  and  0 <= player_pos[0] +
            move[act][0] <= len(board[0])) and  0 <= player_pos[1]+move[act][1] <= len(board):
            if (board[player_pos[1]+move[act][1]][player_pos[0]+move[act][0]] == "d"):
                if player_keys:
                    player_keys -= 1
                    board[player_pos[1]+move[act][1]][player_pos[0]+move[act][0]] = " "
                    player_pos = (player_pos[0]+move[act][0], player_pos[1]+move[act][1])
                else:
                    continue
            else:
                player_pos = (player_pos[0] + move[act][0], player_pos[1] + move[act][1])
        else:
            continue

    win = True


def play_game(board,  player_pos):
    return "left"

difficulty = 1
random = Rand(1)

if __name__ == '__main__':
    TESTS = [{"ИКБО-03-22": [list(range(40)), list(range(40))]}]
    GROUPS, TASKS = ["ИКБО-03-22"], [0, 1]

    check_solution("ИКБО-03-22", 13, 4, "left")



