import json
from pathlib import Path


def bfs(board, source_point, point_type, restritions):
    queue, reached, parents = [source_point], {source_point}, {}
    while queue:
        current = queue.pop(0)
        if board[current[1]][current[0]] == point_type:
            return current
        # Окрестность фон Неймана
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            p = (current[0] + dx, current[1] + dy)
            if 0 <= p[1] < len(board) and 0 <= p[0] < len(board[0]) and not board[p[1]][p[0]] in restritions and p not in reached:
                queue.append(p)
                reached.add(p)
                parents[p] = current
    return []


def check_level(filename, cnt):
    game = json.loads(Path(filename).read_text())

    # Подгружаем метаданные
    spawn = (game["levels"][cnt]["start"][0], game["levels"][cnt]["start"][1])
    board = [list(i) for i in game["maps"][cnt]]  # Board
    plot = game["plot"][cnt]

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


if __name__ == '__main__':
    TESTS = [{"ИКБО-03-22": [list(range(40)), list(range(40))]}]
    GROUPS, TASKS = ["ИКБО-03-22"], [0, 1]


    def check_solution(group, task, variant, difficulty, code):
        if "42" in code:
            return True, ""
        return False, "An error has occured."