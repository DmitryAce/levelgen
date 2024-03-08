
class State:
    def __init__(self, x, y, collected):
        self.x = x
        self.y = y
        self.collected = collected

def is_goal_state(state, total_coins):
    return len(state.collected) == total_coins

def act(board):
    def func(state, action):
        new_x, new_y = state.x, state.y
        new_collected = state.collected.copy()
        if action == 'up':
            new_y -= 1
        elif action == 'down':
            new_y += 1
        elif action == 'left':
            new_x -= 1
        elif action == 'right':
            new_x += 1
        elif action == "take":
            if board[new_y][new_x] == '1' and ((new_x, new_y) not in state.collected):
                new_collected.append((new_x, new_y))
                new_collected = sorted(new_collected)
            else:
                return state

        if is_goal_state(State(state.x, state.y, state.collected), total_coins):
            return state

        if new_x < 0 or new_x >= len(board[0]) or new_y < 0 or new_y >= len(board):
            return state  # Выход за пределы доски

        if board[new_y][new_x] == '#':
            return state  # Столкновение со стеной


        return State(new_x, new_y, new_collected)

    return func


def make_model(board, start_state):
    graph = {}

    def rec(state):
        key = (state.x, state.y, tuple(state.collected))  # Преобразуем список в кортеж
        if key in graph:
            return
        graph[key] = []

        for action in ['up', 'down', 'left', 'right', 'take']:
            new_state = act(board)(state, action)
            new_key = (new_state.x, new_state.y, tuple(new_state.collected))
            if new_state != state:
                graph[key].append(new_key)
                rec(new_state)

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
            elif is_goal_state(State(x, y, list(collected)), total_coins):  # Преобразуем кортеж обратно в список
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
        ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#',
         '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],
        ['#', '1', ' ', ' ', '1', ' ', ' ', '1', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ',
         ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', ' ', '#', '#', '#', '#', '#', '#', '#', '1', '#', '1', '#', '#', '#', ' ', '#', ' ', '#', '1', '#', '#',
         '#', ' ', '#', ' ', '#', '#', ' ', ' ', '#', ' ', '#', ' ', '#', ' ', '#'],
        ['#', ' ', '#', ' ', ' ', ' ', '#', ' ', '1', ' ', '#', '1', '#', ' ', ' ', ' ', '#', ' ', '#', '1', '#', ' ',
         ' ', ' ', '#', ' ', '1', ' ', ' ', ' ', '#', '1', '#', ' ', '#', ' ', '#'],
        ['#', ' ', '#', ' ', '#', ' ', '#', ' ', '1', '#', '1', '#', '1', '#', ' ', '#', ' ', '#', '1', '#', ' ', '#',
         ' ', '#', ' ', '#', '#', '#', ' ', '#', '1', '#', ' ', '#', ' ', '#'],
        ['#', ' ', ' ', ' ', '#', ' ', '#', ' ', ' ', '#', ' ', '#', ' ', '#', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#',
         ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', '1', '1', '#', ' ', '#', ' ', '#'],
        ['#', ' ', '#', ' ', '#', '#', '#', ' ', '#', '#', '#', ' ', '#', ' ', '#', '#', ' ', '#', '#', '#', '#', '#',
         ' ', '#', '#', '#', '#', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', '#'],
        ['#', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#',
         ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', '#', ' ', '#'],
        ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#',
         '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],
        ['#', ' ', '1', '1', ' ', ' ', ' ', '#', ' ', ' ', '1', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', '1', '#',
         ' ', ' ', ' ', '1', '#', ' ', ' ', ' ', '#', ' ', '#', ' ', ' ', '#'],
        ['#', '1', '#', '1', '#', '#', '#', ' ', '#', '1', '#', '1', '#', '#', '#', ' ', '#', '1', '#', '1', '#', '1',
         '#', '#', '#', '#', ' ', '1', '#', '1', '#', '1', '#', '1', '#', '#'],
        ['#', ' ', ' ', ' ', '#', ' ', '#', ' ', ' ', '#', ' ', '#', '1', ' ', ' ', ' ', '#', ' ', '1', ' ', '#', ' ',
         '#', '1', ' ', ' ', ' ', ' ', '1', '1', ' ', ' ', '#', ' ', '#', '1'],
        ['#', '#', '#', '#', '#', ' ', '#', ' ', '#', '#', '#', ' ', '#', '#', '#', ' ', ' ', ' ', '#', '#', '#', '#',
         ' ', '#', ' ', '#', '#', '#', ' ', '#', '#', '#', '#', ' ', '#', '1'],
        ['#', ' ', ' ', ' ', ' ', ' ', '1', '1', ' ', '#', '1', '1', ' ', '#', ' ', ' ', ' ', '#', '1', '1', ' ', '#',
         '1', '1', ' ', '#', '1', ' ', ' ', '#', '1', '1', '#', ' ', '#', '1'],
        ['#', ' ', '#', ' ', '#', '#', '#', '#', '#', '#', '#', '#', ' ', '#', '#', '#', ' ', '#', '1', '#', '#', '#',
         ' ', '#', '1', '#', ' ', '#', '1', '#', '1', '#', ' ', '#', '1', '#'],
        ['#', ' ', '#', ' ', '1', ' ', ' ', ' ', ' ', ' ', '#', '1', ' ', ' ', ' ', ' ', ' ', '1', '#', '1', '#', ' ',
         '#', '1', '#', ' ', ' ', '#', '1', ' ', '#', '1', '#', ' ', '1', '#'],
        ['#', '1', '#', '1', '#', '1', '#', '#', '#', '#', ' ', '#', '1', '#', '#', '#', '#', '#', '1', '#', '#', '#',
         ' ', '#', '#', '#', ' ', '#', '1', '#', '#', '#', '#', ' ', '#', '#'],
        ['#', ' ', '1', '1', ' ', ' ', ' ', '#', ' ', ' ', '#', ' ', '#', ' ', ' ', ' ', ' ', ' ', '1', '#', '1', ' ',
         ' ', '#', '1', ' ', ' ', ' ', ' ', ' ', '1', '1', '#', ' ', ' ', '#'],
        ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#',
         '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#']
    ]

    START_STATE = State(5, 17, [])
    total_coins = sum(row.count('1') for row in board)
    print(total_coins)
    graph = make_model(board, START_STATE)
    make_graph(graph, tuple((START_STATE.x, START_STATE.y, ())), "graph.txt", total_coins)