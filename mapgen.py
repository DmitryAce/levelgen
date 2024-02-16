import random as rand


def generate_map(width, height, coin_chance):
    """
    Генерирует карту игрового уровня.

    :param width: Ширина карты.
    :type width: int
    :param height: Высота карты.
    :type height: int
    :param coin_chance: Вероятность появления монет на карте (в процентах).
    :type coin_chance: float

    :return: Сгенерированная карта в виде двумерного массива.
    :rtype: list[list[str]]
    """
    # Создание двумерного массива для карты, заполненного символами '#'
    gm_map = [['#' for _ in range(width)] for _ in range(height)]
    # Генерация случайной точки старта на карте
    start_x, start_y = rand.randint(0, width - 1), rand.randint(0, height - 1)
    # Установка стартовой позиции на карте
    gm_map[start_y][start_x] = ' '
    # Создание списка для хранения фронтира
    frontier = [(start_x, start_y)]
    # Пока есть точки во фронтире
    while frontier:
        # Выбор случайной точки из фронтира
        x, y = rand.choice(frontier)
        # Удаление выбранной точки из фронтира
        frontier.remove((x, y))
        # Случайный порядок направлений
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        rand.shuffle(directions)
        # Проверка соседних клеток
        for dx, dy in directions:
            nx, ny = x + dx * 2, y + dy * 2
            # Если соседняя клетка находится в пределах карты и является стеной
            if (0 <= nx < width) and (0 <= ny < height) and \
                    gm_map[ny][nx] == '#':
                # Открывается стена между текущей и соседней клетками
                gm_map[y + dy][x + dx] = ' '
                gm_map[ny][nx] = ' '
                # Добавление соседней клетки во фронтир
                frontier.append((nx, ny))
    # Размещение монет на карте в соответствии с вероятностью
    for y in range(height):
        for x in range(width):
            if gm_map[y][x] == ' ' and rand.random() < coin_chance:
                gm_map[y][x] = '1'
    return gm_map  # Возвращение сгенерированной карты


def save_map_to_file(game_map, filename):
    """
    Сохраняет карту игрового уровня в текстовый файл.

    :param game_map: Карта игрового уровня для сохранения.
    :type game_map: list[list[str]]
    :param filename: Имя файла, в который будет сохранена карта.
    :type filename: str
    """
    # Открытие файла для записи
    with open(filename, 'w') as f:
        # Запись каждой строки карты в файл
        for row in game_map:
            f.write('"'+''.join(row) + '",\n')


if __name__ == "__main__":
    width = 25
    height = 25
    coin_chance = 0.1  # Вероятность появления монетки
    filename = 'map.txt'  # Имя файла для сохранения карты

    # Генерация карты и сохранение её в файл
    level = generate_map(width, height, coin_chance)
    save_map_to_file(level, filename)
