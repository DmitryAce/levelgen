import random


def generate_map_maze(width, height, coin_chance):
    """
    Генерирует лабиринт с монетами.

    :param width: Ширина лабиринта.
    :type width: int
    :param height: Высота лабиринта.
    :type height: int
    :param coin_chance: Вероятность появления монеты в каждой клетке лабиринта
    (в диапазоне от 0 до 1).
    :type coin_chance: float
    :return: Сгенерированный лабиринт с монетами в виде двумерного массива.
    :rtype: list[list[str]]
    """
    # Инициализация двумерного массива для хранения лабиринта
    gm_map = [['#' for _ in range(width)] for _ in range(height)]

    def recursive_backtracking(x, y):
        """
        Рекурсивная функция для создания лабиринта методом
        "обратного отслеживания".

        :param x: Текущая координата x.
        :type x: int
        :param y: Текущая координата y.
        :type y: int
        """
        # Устанавливаем текущую клетку как проходимую
        gm_map[y][x] = ' '

        # Список возможных направлений
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        # Перемешиваем направления для случайного выбора
        random.shuffle(directions)

        # Проходим по каждому направлению
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            # Проверяем, находится ли клетка в пределах лабиринта и ?стена?
            if 0 <= nx < width and 0 <= ny < height and gm_map[ny][nx] == '#':
                # Отмечаем клетку как проходимую
                gm_map[ny - dy // 2][nx - dx // 2] = ' '
                # Рекурсивно вызываем функцию для новой клетки
                recursive_backtracking(nx, ny)

    # Начинаем генерацию лабиринта с координат (1, 1)
    recursive_backtracking(1, 1)

    # Добавляем монеты в случайные клетки согласно заданной вероятности
    for y in range(height):
        for x in range(width):
            if gm_map[y][x] == ' ' and random.random() < coin_chance:
                gm_map[y][x] = '1'

    return gm_map


def save_map_to_file(game_map, filename):
    with open(filename, 'w') as f:
        for row in game_map:
            f.write('"' + ''.join(row) + '",\n')


if __name__ == "__main__":
    # Пример использования:
    width = 100
    height = 100
    coin_chance = 0.1  # Вероятность появления монетки
    filename = 'map_maze.txt'  # Имя файла для сохранения карты

    map = generate_map_maze(width, height, coin_chance)
    save_map_to_file(map, filename)
