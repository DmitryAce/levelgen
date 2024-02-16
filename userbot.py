def get_directions(path_points):
    """
    Функция получения направления путем преобразования разниц
    между координатами.

    :param path_points: Список точек пути.
    :type path_points: list[tuple[int, int]]
    :return: Список направлений.
    :rtype: list[str]
    """
    directions = {
        (1, 0): "right",
        (-1, 0): "left",
        (0, 1): "down",
        (0, -1): "up"
    }
    # Генерация списка направлений на основе точек пути
    return [directions[(p[0] - path_points[i][0], p[1] - path_points[i][1])]
            for i, p in enumerate(path_points[1:])]


def bfs(source_point, check):
    """
    Функция реализующая поиск в ширину.

    :param source_point: Начальная точка поиска.
    :type source_point: tuple[int, int]
    :param check: Функция проверки наличия препятствия в заданной точке.
    :type check: function
    :return: Список направлений для достижения цели.
    :rtype: list[str]
    """
    # Инициализация очереди для обхода в ширину
    queue, reached, parents = [source_point], {source_point}, {}
    while queue:
        current = queue.pop(0)
        if check("gold", current[0], current[1]):
            path_points = [current]
            # Восстановление пути до начальной точки по словарю родителей
            while path_points[-1] in parents:
                path_points.append(parents[path_points[-1]])
            return get_directions(path_points[::-1])
        # Здесь перебираем соседние точки
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            p = (current[0] + dx, current[1] + dy)
            if not check("wall", p[0], p[1]) and p not in reached:
                queue.append(p)
                reached.add(p)
                # Запись текущей точки как родителя соседней точки
                parents[p] = current
    return []


def script(check, x, y):
    """
    Определяет действие для игрока в зависимости от его
    текущего положения и окружающей обстановки.

    :param check: Функция проверки наличия объектов в заданной точке.
    :type check: function
    :param x: Координата X текущего положения игрока.
    :type x: int# Если игрок не находится на точке, то он должен пропустить ход
    :param y: Координата Y текущего положения игрока.
    :type y: int
    :return: Действие для игрока.
    :rtype: str
    """
    # Проверка, нужно ли взять золото, если игрок находится на точке с золотом
    if check("gold", x, y) and check("player", x, y):
        return "take"
    # Если игрок находится на точке без золота, вызывается поиск пути к золоту
    elif check("player", x, y):
        # Возвращается первое направление в пути
        return bfs((x, y), check)[0]
    else:
        # Если игрок не находится на точке, то он должен пропустить ход
        return "pass"
