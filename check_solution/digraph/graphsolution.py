import graphviz


def go(room, key):
    def func(state):
        player = state['player']
        if state[key] != player:
            return state
        if player == 'alice' and state['alice_room'] == 'red':
            return state
        if player == 'bob' and state['bob_room'] == 'blue':
            return state
        new_state = dict(state)
        new_state[f"{player}_room"] = room
        return new_state

    return func


def switch_player(state):
    if state['player'] == 'alice':
        return dict(state, player='bob')
    return dict(state, player='alice')


def take(key):
    def func(state):
        if state['player'] == 'alice' and state[key] != state['alice_room']:
            return state
        if state['player'] == 'bob' and state[key] != state['bob_room']:
            return state
        new_state = dict(state)
        new_state[key] = state['player']
        return new_state

    return func


def give(key):
    def func(state):
        if state['alice_room'] != state['bob_room']:
            return state
        if state['player'] == 'alice' and state[key] != 'alice':
            return state
        if state['player'] == 'bob' and state[key] != 'bob':
            return state
        new_state = dict(state)
        new_state[key] = 'alice' if state['player'] == 'bob' else 'bob'
        return new_state

    return func


game = {
    'red': dict(
        down=go('west', 'red_key'),
        give_red=give('red_key'),
        give_blue=give('blue_key'),
        give_green=give('green_key'),
        switch=switch_player
    ),
    'blue': dict(
        down=go('east', 'blue_key'),
        give_red=give('red_key'),
        give_blue=give('blue_key'),
        give_green=give('green_key'),
        switch=switch_player
    ),
    'west': dict(
        up=go('red', 'red_key'),
        right=go('east', 'green_key'),
        take_red=take('red_key'),
        take_blue=take('blue_key'),
        take_green=take('green_key'),
        give_red=give('red_key'),
        give_blue=give('blue_key'),
        give_green=give('green_key'),
        switch=switch_player
    ),
    'east': dict(
        up=go('blue', 'blue_key'),
        left=go('west', 'green_key'),
        take_red=take('red_key'),
        take_blue=take('blue_key'),
        take_green=take('green_key'),
        give_red=give('red_key'),
        give_blue=give('blue_key'),
        give_green=give('green_key'),
        switch=switch_player
    )
}


def is_goal_state(s):
    return ('alice_room', 'red') in s and ('bob_room', 'blue') in s


def get_current_room(state):
    if state['player'] == 'alice':
        return state['alice_room']
    return state['bob_room']


def make_model(game, state):
    graph = {}
    print(frozenset(state.items()))
    def rec(state):
        key = frozenset(state.items())
        graph[key] = []
        for func in game[get_current_room(state)].values():
            new_state = func(state)
            if new_state != state:
                new_key = frozenset(new_state.items())
                if new_key not in graph[key]:
                    graph[key].append(new_key)
                if new_key not in graph:
                    rec(new_state)

    rec(state)
    return graph


def make_graph(graph, start_key, output_file):
    dead_ends = []  # find_dead_ends(graph) TODO
    with open(output_file, 'w') as f:
        f.write('digraph {\n')
        graph_keys = list(graph.keys())
        for x in graph:
            n = graph_keys.index(x)
            if x == start_key:
                f.write(f'n{n} [style="filled",fillcolor="dodgerblue",shape="circle"]\n')
            elif is_goal_state(x):
                f.write(f'n{n} [style="filled",fillcolor="green",shape="circle"]\n')
            elif x in dead_ends:
                f.write(f'n{n} [style="filled",fillcolor="red",shape="circle"]\n')
            else:
                f.write(f'n{n} [shape="circle"]\n')
        for x in graph:
            n1 = graph_keys.index(x)
            for y in graph[x]:
                n2 = graph_keys.index(y)
                f.write(f'n{n1} -> n{n2}\n')
        f.write('}')


if __name__ == "__main__":
    START_STATE = dict(
        player='alice',
        alice_room='west',
        bob_room='east',
        red_key='east',
        blue_key='west',
        green_key='east'
    )

    make_graph(make_model(game, START_STATE), START_STATE, "graph.txt")
