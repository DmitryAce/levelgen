import time


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

    def randint(self, low, high):
        return low + self.random() % (high - low + 1)

    def choice(self, seq):
        return seq[self.randint(0, len(seq) - 1)]

    def randf(self):
        return self.random() / self.rand_max

    def uniform(self, low, high):
        return low + (high - low) * self.randf()


def save_map(game_map, filename):
    """ Сохраняем карту в txt"""
    with open(filename, 'w') as f:
        for row in game_map:
            f.write('"' + ''.join(row) + '",\n')


def gen_board_with_caves(width, height, rooms):
    """Генератор начальной карты с пещерами"""
    # Создаем пустую карту
    game_map = [['B' for _ in range(width)] for _ in range(height)]

    # Создаем помещения
    for _ in range(rooms):
        # Выбираем случайное место и размер для помещения
        room_width = random.randint(3, 5)
        room_height = random.randint(3, 5)
        start_x = random.randint(1, width - room_width - 1)
        start_y = random.randint(1, height - room_height - 1)

        # Создаем помещение
        for x in range(start_x, start_x + room_width):
            for y in range(start_y, start_y + room_height):
                game_map[y][x] = 'W'

    # Возвращаем карту в виде списка строк
    return game_map


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
        if board[sizey-1][x] != "#":
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


def main():
    events = ["coins", "exit", "treasure"]
    gen_method = ["MazeBacktracker", "MazeGrowth", "NoDeadEnds"]
    N = random.randint(1, 3)
    plot = []
    task = []

    # ---MAP---
    gen_method = random.choice(gen_method)
    width = random.randint(16, 32)
    height = width

    filename = 'board.txt'  # Имя файла для сохранения карты
    coin_chance = random.uniform(0.4, 0.7)

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
    print(plot, " - ", N, ", ", gen_method)

    # --TREASURES--
    # Создаем комнаты
    treasure_coordinates = []
    if "treasure" in plot:
        rooms = random.randint(1, 3)

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
                elif door == 2 and x != 2:
                    k = random.randint(1, 3)
                    if not ([x - 2, y - 2 + k] in tiles): continue
                    board[y - 2 + k][x - 2] = 'd'
                    break

            # Создаем ключ
            while True:
                i = random.randint(1, width - 1)
                j = random.randint(1, height - 1)

                if i in range(x - 2, x + 3) and j in range(y - 2, y + 3):
                    continue
                else:
                    if board[j][i] != "1" and board[j][i] != "#":
                        board[j][i] = "k"
                        break

    # --COINS--
    if "coins" in plot:
        coins_goal = random.randint(10, 40)
        task.append(
            f"Необходимо собрать {coins_goal} *.")

        # Увеличиваем кол-во монет на карте, чтобы боло с запасом
        coins_goal += int(coin_chance * coins_goal)

        while coins_goal:
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)

            if board[y][x] == " ":
                board[y][x] = "1"
                coins_goal -= 1

    # --EXIT--
    if "exit" in plot:
        # Случайное количество выходов на карте
        exits = random.randint(1,3)

        while exits:
            direction = random.randint(1,4)

            # Много проверок учитывают чтобы выход не появился внутри сокровищницы
            match direction:
                case 1:
                    x = random.randint(1,width-2)
                    if board[0][x] == "#" and board[1][x] != "#":
                        flag = True
                        for center in treasure_coordinates:
                            if (center[0]-2 < x < center[0]+2) and (center[1] == 2 or center[1] == 3):
                                flag = False
                                break
                    if not flag: continue
                    else:
                        board[0][x] = "E"
                        exits -= 1
                case 2:
                    y = random.randint(1, height - 2)
                    if board[y][-1] == "#" and board[y][-2] != "#":
                        flag = True
                        for center in treasure_coordinates:
                            if (center[0] > width-4) and (center[1]-2 < y < center[1]+2):
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
                            if (center[0] - 2 < x < center[0] + 2) and (center[1] == height - 2 or center[1] == height - 3):
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

    print(task)
    save_map(board, filename)


if __name__ == '__main__':
    random = Rand(252151)
    main()
