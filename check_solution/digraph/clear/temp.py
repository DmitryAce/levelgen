from collections import namedtuple
import graphviz


def make_model(graph, state, is_goal, actions):
    if state in graph:
        return
    graph[state] = set()
    if is_goal(state):
        return
    for action in actions:
        new = action(state)
        if new != state:
            graph[state].add(new)
            make_model(graph, new, is_goal, actions)
    return graph

def draw_model(graph, start, is_goal):
    lines = ['digraph {', 'ranksep=0.01', 'rankdir=LR']
    states = list(graph)
    for i, state in enumerate(states):
        x, y, collected = state
        color = 'lightgreen' if is_goal(state) else 'dodgerblue' if state == start else 'white'
        lines += [f'n{i} [label="({x}, {y})\n{len(collected)}$", shape="circle", style="filled", fillcolor="{color}"]']
        for new in graph[state]:
            lines += [f'n{i} -> n{states.index(new)}']
    lines.append('}')
    source = '\n'.join(lines)
    graphviz.Source(source, format='svg').render('graph')


State = namedtuple('State', 'x y collected')

def go(board, state, x=0, y=0):
    mx = len(board[0]) - 1
    my = len(board) - 1
    x = max(min(state.x + x, mx), 0)
    y = max(min(state.y + y, my), 0)
    if board[y][x] == '#':
        return state
    return state._replace(x=x, y=y)

def collect(board, state):
    coin = (state.x, state.y)
    exists = board[state.y][state.x] == '1'
    collected = coin in state.collected
    if exists and not collected:
        money = state.collected.union({coin})
        return state._replace(collected=money)
    return state

def make_dandybot_model(board, start, is_goal):
    return make_model({}, start, is_goal, [
        lambda state: go(board, state, y=-1), # up
        lambda state: go(board, state, y=+1), # down
        lambda state: go(board, state, x=-1), # left
        lambda state: go(board, state, x=+1), # right
        lambda state: collect(board, state),  # take
    ])

if __name__ == '__main__':
    board = [
        ['#', ' ', '1'],
        ['#', ' ', '#'],
        ['1', ' ', ' '],
        ['#', ' ', '#'],
        ['#', ' ', '1']
    ]

    def is_goal(state):
        return len(state.collected) == sum(row.count('1') for row in board)

    start = State(2, 2, frozenset())
    graph = make_dandybot_model(board, start, is_goal)
    print(len(graph))
    draw_model(graph, start, is_goal)
