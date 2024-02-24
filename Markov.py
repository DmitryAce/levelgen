import random
import os
import time
import sys
from mapsaver import save_map


def gen_board(width, height, rooms):
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
    x = [(i + k, j) for k in range(count)]
    y = [(i, j + k) for k in range(count)]
    return x, x[::-1], y, y[::-1]


def rule(before, after):
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


def render(board):
    o, b = '#+. -', 'BRGWA'
    for row in board:
        for cell in row:
            print(o[b.index(cell)], end='')
        print()


def interp(board, init, rules):
    a, b = len(board) // 2, len(board[0]) // 2
    board[a][b:b + len(init)] = init
    start_time = time.time()  # Запоминаем время начала выполнения цикла
    while rules:
        if time.time() - start_time >= 5:
            break
        for rule in rules:
            if rule(board):
                break
        os.system('cls')
        render(board)


def addcoins(board, height, width, coin_chance):
    for y in range(height):
        for x in range(width):
            if board[y][x] == ' ' and random.random() < coin_chance:
                board[y][x] = '1'
    return board


if __name__ == "__main__":

    width, height = 21, 21
    filename = 'Markov.txt'  # Имя файла для сохранения карты
    coin_chance = 0.1  # Вероятность появления монетки

    # Генерация карты до НАМ
    # board = gen_board(21, 21, 10)
    board = [['B' for _ in range(width)] for _ in range(height)]

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
            if board[y][x] == 'W' or board[y][x] == 'G' or board[y][x] == 'R' or board[y][x] == 'A':
                board[y][x] = ' '

    addcoins(board, height, width, coin_chance)

    save_map(board, filename)

# Интерпретация НАМ: MazeBacktracker
#    interp(board, 'BRGW', [
#        rule('RBB', 'GGR'),
#        rule('RGG', 'WWR'),
#    ])


# Интерпретация НАМ: MazeGrowth
# interp(board, 'BWG', [
#     rule('WBB', 'WAW')
# ])

# Интерпретация НАМ: Digger
# interp(board, 'BRW', [
#     rule('RB', 'WR'),
#     rule('RW', 'WR'),
# ])

# Интерпретация НАМ: NoDeadEnds
# interp(board, 'BRWA', [
#     rule('RBB', 'WAR'),
#     rule('WBB', 'WAR'),
#     rule('RBR', 'WAW'),
#     rule('RBW', 'WAW'),
# ])