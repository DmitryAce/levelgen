import random
import time


def save_map(game_map, filename):
    """ Сохраняем карту в txt"""
    with open(filename, 'w') as f:
        for row in game_map:
            f.write('"' + ''.join(row) + '",\n')


def gen_board(width, height, rooms):
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


def addcoins(board, height, width, coin_chance):
    for y in range(height):
        for x in range(width):
            if board[y][x] == ' ' and random.random() < coin_chance:
                board[y][x] = '1'
    return board


def addwalls1010(board, size):
    # Добавляем верхнюю и нижнюю стены
    board.insert(0, ["#"] * (size))
    board.append(["#"] * (size))

    return board


def main(seed):
    random.seed(seed)

    events = ["coins", "exit", "treasure"]
    gen_method = ["MazeBacktracker", "MazeGrowth", "NoDeadEnds"]
    N = random.randint(1, 3)
    plot = []
    task = []

    # ---MAP---
    gen_method = random.choice(gen_method)
    #size = random.randint(16, 32)
    size = 32 # Метод в процессе отладки

    filename = 'board.txt'  # Имя файла для сохранения карты
    coin_chance = random.uniform(0.1, 0.2)

    board = [['B' for _ in range(size)] for _ in range(size)]

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
    for y in range(size):
        for x in range(size):
            if board[y][x] == 'B':
                board[y][x] = '#'

    # Заменяем все символы 'W' на ' '
    for y in range(size):
        for x in range(size):
            if board[y][x] == 'W' or board[y][x] == 'G' or board[y][
                x] == 'R' or board[y][x] == 'A':
                board[y][x] = ' '

    #---TILES---
    """Сделал чтобы можно было проверить определьные точки 
    при создании сокровищ"""
    tiles = []
    for y in board:
        for x in y:
            # work in progress

    # ---PLOT---
    for i in range(0, N):
        while True:
            temp = random.choice(events)
            if not (temp in plot):
                plot.append(temp)
                break
    print(plot, " - ", N, ", ", gen_method)

    # --TREASURES--
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

        board = addwalls1010(board, size)

        # Создаем комнаты
        while rooms:
            x = random.randint(2, size - 3)  # Координаты сокровища
            y = random.randint(2, size - 3 + 2)
            #+2 к размеру Из-за добавления верхней и нижней стены

            # G fix
            if x == 3:
                x -= 1
            elif x == size - 4:
                x += 1
            # +2 к размеру Из-за добавления верхней и нижней стены
            if y == size - 4 + 2:
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
                board[y + 3][i] = ' '
                board[y - 3][i] = ' '

            # углы
            board[y - 3][x - 3] = ' '
            board[y - 3][x + 3] = ' '
            board[y + 3][x - 3] = ' '
            board[y + 3][x + 3] = ' '

            # Правая и левая границы
            for i in range(y - 2, y + 3):
                board[i][x + 2] = '#'
                board[i][x - 2] = '#'
                board[i][x - 3] = ' '
                board[i][x + 3] = ' '

            while True:
                # Расположение двери
                door = random.randint(1, 4)

                if door == 1 and y != 2:
                    k = random.randint(1, 3)
                    board[y - 2][x - 2 + k] = 'd'
                    break
                elif door == 2 and x != size - 3:
                    k = random.randint(1, 3)
                    board[y - 2 + k][x + 2] = 'd'
                    break
                elif door == 3 and y != size - 3:
                    k = random.randint(1, 3)
                    board[y + 2][x - 2 + k] = 'd'
                    break
                elif door == 2 and x != 2:
                    k = random.randint(1, 3)
                    board[y - 2 + k][x - 2] = 'd'
                    break

            # Создаем ключ
            while True:
                i = random.randint(1, size - 1)
                j = random.randint(1, size - 1)

                if i in range(x - 2, x + 3) and j in range(y - 2, y + 3):
                    continue
                else:
                    if board[j][i] != "1" and board[j][i] != "#":
                        board[j][i] = "k"
                        break

    print(task)
    addcoins(board, size, size, coin_chance)
    save_map(board, filename)


if __name__ == '__main__':
    main(131)
