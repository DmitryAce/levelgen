import graphviz


if __name__ == "__main__":

    # Создаем граф
    dot = graphviz.Digraph()

    # Добавляем узлы с подписями
    dot.node('n0', label='room1', style='filled', fillcolor='dodgerblue', shape='circle')
    dot.node('n1', label='room1', shape='circle')
    dot.node('n2', label='room2', style='filled', fillcolor='green', shape='circle')
    dot.node('n3', label='room3', shape='circle')
    dot.node('n4', label='room4', shape='circle')
    dot.node('n5', label='room5', shape='circle')

    # Добавляем ребра с подписями
    dot.edge('n0', 'n1', label='left')
    dot.edge('n0', 'n2', label='up')
    dot.edge('n0', 'n3', label='right')
    dot.edge('n1', 'n2', label='up')
    dot.edge('n1', 'n0', label='right')
    dot.edge('n3', 'n4', label='up')
    dot.edge('n3', 'n5', label='right')
    dot.edge('n4', 'n3', label='down')
    dot.edge('n4', 'n5', label='right')
    dot.edge('n5', 'n4', label='up')
    dot.edge('n5', 'n3', label='left')

    # Отображаем граф
    dot.render('game_graph', format='png', view=True)
