import random
import time

from Plot import Plot
from Board import Board, Tile


def options(i, j, count):
    """
    Генерирует возможные варианты координат,
    исходя из текущей позиции и количества.
    """
    x = [(i + k, j) for k in range(count)]
    y = [(i, j + k) for k in range(count)]
    return x, x[::-1], y, y[::-1]


def rule(before, after):
    """
    Создает правило замены символов на карте.
    """

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


def init_map(difficulty, gen_method):
    """
    Инициализация карты
    """

    height, width = difficulty * 8, difficulty * 8
    matrix = [['B' for _ in range(width)] for _ in range(height)]

    # Gen Map Based on NAM
    match gen_method:
        case "MazeGrowth":
            interp(matrix, 'BWG', [
                rule('WBB', 'WAW')
            ])
        case "MazeBacktracker":
            interp(matrix, 'BRGW', [
                rule('RBB', 'GGR'),
                rule('RGG', 'WWR'),
            ])
        case "NoDeadEnds":
            interp(matrix, 'BRWA', [
                rule('RBB', 'WAR'),
                rule('WBB', 'WAR'),
                rule('RBR', 'WAW'),
                rule('RBW', 'WAW'),
            ])

    board = Board.from_matrix(matrix)
    board.add_border()
    return board


def generate_treasures(board: Board, plot: Plot):
    width, height = board.get_shape()
    rooms = plot.rooms
    t_width, t_height = 3, 3

    treasure_coordinates = []

    while rooms:
        x = set(range(0, width - t_width - 1)).difference({1, width - t_width - 2})
        y = set(range(0, width - t_height - 1)).difference({1, width - t_width - 2})

        x = random.choice(list(x))
        y = random.choice(list(y))

        if not any(abs(x - tx) < t_width + 1 and abs(y - ty) < t_height + 1 for tx, ty in treasure_coordinates):
            rooms -= 1

            treasure_coordinates.append([x, y])

            board.clear_room(x, y, x + t_width, y + t_height)
            board.set_tile((x + t_width) // 2, (y + t_height) // 2, Tile.TREASURE)

            # Верхняя и нижняя границы
            for i in range(x, x + t_width):
                board.set_tile(i, y, Tile.WALL)
                board.set_tile(i, y + t_height, Tile.WALL)

            # Правая и левая границы
            for i in range(y, y + t_height):
                board.set_tile(x, i, Tile.WALL)
                board.set_tile(x + t_width, i, Tile.WALL)

            # Очистка
            for i in range(x - 1, x + t_width + 1):
                if 1 < y - 1:
                    board.set_tile(i, y - 1, Tile.NONE)
                if y + t_width + 1 < height:
                    board.set_tile(i, y + t_height + 1, Tile.NONE)

            for i in range(y - 1, y + t_height + 1):
                if 1 < x - 1:
                    board.set_tile(x - 1, i, Tile.NONE)
                if x + t_width + 1 < width:
                    board.set_tile(x + t_width + 1, i, Tile.NONE)

    return treasure_coordinates, board


