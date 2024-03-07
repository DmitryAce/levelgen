import json
from pathlib import Path
import graphviz, math


collectables_dict = {
        "1": "coin",
        "k": "key",
        "t": "treasure",
        "l": "lever",
        "E": "escaped",
        "X": "escaped",
        "d": "opened",
        (1, 0): "right",
        (0, 1): "down",
        (-1, 0): "left",
        (0, -1): "up",
    }

def is_subset(sub_dict, main_dict):
    for key, value in sub_dict.items():
        if key not in main_dict or main_dict[key] != value:
            return False
    return True

def find_coordinates(matrix, target):
    for y, row in enumerate(matrix):
        for x, value in enumerate(row):
            if value == target:
                return x, y
    return None

def find_all_coordinates(matrix, element):
    e_coordinates = []
    for y, row in enumerate(matrix):
        for x, value in enumerate(row):
            if isinstance(value, str) and value.lower() == element:
                e_coordinates.append((x, y))
    return e_coordinates

def euclidean_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def draw_graph(states, connections):
    dot = graphviz.Digraph()
    for state in states:
        title = "X:"+str(state['x'])+"Y:"+str(state['y'])
        dot.node(str(state['state']), label=title, style='filled', fillcolor=color_dict.get(state['action']), shape='circle')
    for k,v in connections.items():
        action = [state["action"] for state in states if state["state"] == k][0]
        dot.edge(str(k), str(v), label=action)

    dot.render('game_graph', format='png', view=True)

def bfs(states, collectables, win_req, EXITTYPE, spawnpoint):
    queue, reached, connections = [states[0]], [], {}

    STATECNT = 1
    while queue:
        current = queue.pop(0)
        print(current["state"], "CORDS: ", current["x"], current["y"])
        x = current['x']
        y = current['y']
        board = current['board']
        coins = current['coins']
        keys = current['keys']
        lever = current['lever']
        treasures = current['treasures']
        escaped = current['escaped']

        # КОНЕЦ
        if board[y][x] == "E" and is_subset(win_req, current):
            coords = find_all_coordinates(board, "E")
            distances = [euclidean_distance((spawnpoint[0], spawnpoint[1]), point) for point in coords]
            farthest_exit = coords[distances.index(max(distances))]

            if farthest_exit == (x, y):
                STATECNT += 1
                cur_state = {
                    'state': STATECNT,
                    'parent': current['state'],
                    'action': "fake",
                    'x': x,
                    'y': y,
                    'board': board,
                    'coins': coins,
                    'keys': keys,
                    'treasures': treasures,
                    'lever': lever,
                    'escaped': True,
                }
                states.append(cur_state)
                reached.append(cur_state)
                connections[current['state']] = STATECNT
                continue
            else:
                STATECNT += 1
                board[y][x] = " "
                cur_state = {
                    'state': STATECNT,
                    'parent': current['state'],
                    'action': collectables_dict.get("E"),
                    'x': x,
                    'y': y,
                    'board': board,
                    'coins': coins,
                    'keys': keys,
                    'treasures': treasures,
                    'lever': lever,
                    'escaped': escaped,
                }
                states.append(cur_state)
                queue.append(cur_state)
                connections[current['state']] = STATECNT
                continue

        if board[y][x] == "X" and is_subset(win_req, current):
            STATECNT += 1
            cur_state = {
                'state': STATECNT,
                'parent': current['state'],
                'action': collectables_dict.get("X"),
                'x': x,
                'y': y,
                'board': board,
                'coins': coins,
                'keys': keys,
                'treasures': treasures,
                'lever': lever,
                'escaped': True,
            }
            states.append(cur_state)
            reached.append(cur_state)
            connections[current['state']] = STATECNT
            continue

        if is_subset(win_req, current) and EXITTYPE == 0:
            STATECNT += 1
            cur_state = {
                'state': STATECNT,
                'parent': current['state'],
                'action': 'escaped',
                'x': x,
                'y': y,
                'board': board,
                'coins': coins,
                'keys': keys,
                'treasures': treasures,
                'lever': lever,
                'escaped': True,
            }
            states.append(cur_state)
            reached.append(cur_state)
            connections[current['state']] = STATECNT
            continue

        # Если в состоянии есть что подобрать
        if board[y][x] in collectables:
            STATECNT += 1
            loot = board[y][x]

            if board[y][x] == "1":
                board[y][x] = " "
                cur_state = {
                    'state': STATECNT,
                    'parent': current['state'],
                    'action': collectables_dict.get(loot),
                    'x': x,
                    'y': y,
                    'board': board,
                    'coins': coins+1,
                    'keys': keys,
                    'treasures': treasures,
                    'lever': lever,
                    'escaped': escaped,
                }
            elif board[y][x] == "k":
                board[y][x] = " "
                cur_state = {
                    'state': STATECNT,
                    'parent': current['state'],
                    'action': collectables_dict.get(loot),
                    'x': x,
                    'y': y,
                    'board': board,
                    'coins': coins,
                    'keys': keys+1,
                    'treasures': treasures,
                    'lever': lever,
                    'escaped': escaped,
                }
            elif board[y][x] == "t":
                board[y][x] = " "
                cur_state = {
                    'state': STATECNT,
                    'parent': current['state'],
                    'action': collectables_dict.get(loot),
                    'x': x,
                    'y': y,
                    'board': board,
                    'coins': coins,
                    'keys': keys,
                    'treasures': treasures+1,
                    'lever': lever,
                    'escaped': escaped,
                }
            elif board[y][x] == "d":
                board[y][x] = " "
                cur_state = {
                    'state': STATECNT,
                    'parent': current['state'],
                    'action': collectables_dict.get(loot),
                    'x': x,
                    'y': y,
                    'board': board,
                    'coins': coins,
                    'keys': keys-1,
                    'treasures': treasures,
                    'lever': lever,
                    'escaped': escaped,
                }
            elif board[y][x] == "l":
                board[y][x] = "L"

                x1, y1 = find_coordinates(board, "x")
                board[y1][x1] = "X"

                cur_state = {
                    'state': STATECNT,
                    'parent': current['state'],
                    'action': collectables_dict.get(loot),
                    'x': x,
                    'y': y,
                    'board': board,
                    'keys': keys,
                    'treasures': treasures,
                    'lever': True,
                    'escaped': escaped,
                }

            states.append(cur_state)
            queue.append(cur_state)
            reached.append(current)
            connections[current['state']] = STATECNT
            continue


        # Окрестность фон Неймана
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            new_state = {
                'x': x+dx,
                'y': y+dy,
                'board': board,
                'coins': coins,
                'keys': keys,
                'treasures': treasures,
                'lever': lever,
                'escaped': escaped,
            }
            p = board[new_state['y']][new_state['x']]
            if p == "#" or (p == "d" and (not new_state['keys'])):
                continue

            exist = False

            for r in reached:
                if is_subset(new_state, r):
                    exist = True
                    break

            if exist:
                continue

            if 0 <= new_state['y'] < len(board) and 0 <= new_state['x'] < len(board[0]):
                STATECNT += 1
                cur_state = {
                    'state': STATECNT,
                    'parent': current['state'],
                    'action': collectables_dict.get((dx, dy)),
                    'x': x+dx,
                    'y': y+dy,
                    'board': board,
                    'coins': coins,
                    'keys': keys,
                    'treasures': treasures,
                    'lever': lever,
                    'escaped': escaped,
                }
                states.append(cur_state)
                queue.append(cur_state)
                connections[current['state']] = STATECNT
    return states, connections


def mk_graph(filename, cnt):
    game = json.loads(Path(filename).read_text())

    # Данные зависящие от игры
    collectables = ["1","k","t","l","d"]
    actions = ["take", "up", "down", "left", "right"]
    win_req = game["win_req"][cnt]
    EXITTYPE = game["exit_type"][cnt]
    spawnpoint = game["levels"][cnt]["start"]

    # Создаем граф
    dot = graphviz.Digraph()

    states = [ ]

    # Подгружаем метаданные
    spawn = (game["levels"][cnt]["start"][0], game["levels"][cnt]["start"][1])
    board = [list(i) for i in game["maps"][cnt]]  # Board
    plot = game["plot"][cnt]

    states.append({
        'state': 0,
        'parent': 0,
        'action': "init",
        'x': spawn[0],
        'y': spawn[1],
        'board': board,
        'coins': 0,
        'keys': 0,
        'treasures': 0,
        'lever': False,
        'escaped': 0,
    })

    #dot.node('n0', label='start', style='filled', fillcolor='darkorchid4', shape='circle')

    states, connections = bfs(states, collectables, win_req, EXITTYPE, spawnpoint)
    print("hello")

if __name__ == '__main__':
    for i in range(1):
        print(f"Уровень {i+1} :", mk_graph("game.json", i))
