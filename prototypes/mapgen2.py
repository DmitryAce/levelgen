import random


def generate_map2(width, height, wall_chance, coin_chance):
    """
    Генерирует карту игрового уровня.

    :param width: Ширина карты.
    :type width: int
    :param height: Высота карты.
    :type height: int
    :param wall_chance: Вероятность появления стены на карте
    (в диапазоне от 0 до 1).
    :type wall_chance: float
    :param coin_chance: Вероятность появления монеты на карте
    (в диапазоне от 0 до 1).
    :type coin_chance: float
    :return: Сгенерированная карта в виде двумерного массива.
    :rtype: list[str]
    """
    gm_map = []
    for i in range(height):
        row = []
        for j in range(width):
            rand = random.random()
            if rand < wall_chance:
                row.append('#')
            elif rand < coin_chance + wall_chance:
                row.append('1')
            else:
                row.append(' ')
        gm_map.append(''.join(row))
    return gm_map


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
            f.write('"' + ''.join(row) + '",\n')


if __name__ == "__main__":
    # Пример использования:
    width = 10
    height = 10
    wall_chance = 0.3  # Вероятность появления стены
    coin_chance = 0.1  # Вероятность появления монетки
    filename = 'map2.txt'  # Имя файла для сохранения карты

    level = generate_map2(width, height, wall_chance, coin_chance)
    save_map_to_file(level, filename)
