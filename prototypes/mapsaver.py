def save_map(game_map, filename):
    with open(filename, 'w') as f:
        for row in game_map:
            f.write('"' + ''.join(row) + '",\n')