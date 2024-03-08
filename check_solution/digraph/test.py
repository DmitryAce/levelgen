
def is_goal_state(state, total_coins):
    return len(state['collected']) == total_coins

def go(board):
    def func(state, direction):
        new_x, new_y = state['x'], state['y']
        if direction == 'up':
            new_y -= 1
        elif direction == 'down':
            new_y += 1
        elif direction == 'left':
            new_x -= 1
        elif direction == 'right':
            new_x += 1

        if is_goal_state({'collected': state['collected']}, total_coins):
            return state

        if new_x < 0 or new_x >= len(board[0]) or new_y < 0 or new_y >= len(board):
            return state  # Выход за пределы доски

        if board[new_y][new_x] == '#':
            return state  # Столкновение со стеной

        new_state = dict(state)  # Копируем state
        new_state['x'], new_state['y'] = new_x, new_y
        if board[new_y][new_x] == '1' and ( not ( (new_x, new_y) in state['collected'] ) ):
            new_state['collected'].append((new_x, new_y))
        return new_state

    return func

def make_model(board, start_state):
    graph = {}

    def rec(state):
        key = (state['x'], state['y'], tuple(state['collected']))  # Преобразуем список в кортеж
        if key in graph:
            return
        graph[key] = []
        for direction in ['up', 'down', 'left', 'right']:
            new_state = go(board)(dict(state), direction)
            new_key = (new_state['x'], new_state['y'], tuple(new_state['collected']))
            if new_state != state:
                graph[key].append(new_key)
                rec(dict(new_state))

    rec(start_state)
    return graph
def make_graph(graph, start_key, output_file, total_coins):
    with open(output_file, 'w') as f:
        f.write('digraph {\n')
        graph_keys = list(graph.keys())
        for idx, key in enumerate(graph_keys):
            x, y, collected = key
            if key == start_key:
                f.write(f'n{idx} [label="X:{x} Y:{y} C:{collected}", style="filled",fillcolor="dodgerblue",shape="circle"]\n')
            elif is_goal_state({'collected': list(collected)}, total_coins):  # Преобразуем кортеж обратно в список
                f.write(f'n{idx} [label="X:{x} Y:{y} C:{collected}", style="filled",fillcolor="green",shape="circle"]\n')
            else:
                f.write(f'n{idx} [label="X:{x} Y:{y} C:{collected}", shape="circle"]\n')

        for idx, key in enumerate(graph_keys):
            for new_key in graph[key]:
                new_idx = graph_keys.index(new_key)
                f.write(f'n{idx} -> n{new_idx}\n')
        f.write('}')

if __name__ == "__main__":
    board = [
        ['#', ' ', '1', ' ', '#'],
        ['#', ' ', '#', ' ', '#'],
        ['1', ' ', ' ', ' ', '1'],
        ['#', ' ', '#', ' ', '#'],
        ['#', ' ', '1', ' ', '#']
    ]

    START_STATE = {'x': 1, 'y': 0, 'collected': []}
    total_coins = sum(row.count('1') for row in board)

    graph = make_model(board, START_STATE)
    make_graph(graph, tuple((START_STATE['x'], START_STATE['y'], ())), "graph.txt", total_coins)
