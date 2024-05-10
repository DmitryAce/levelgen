import random


class Plot:
    events = ["coins", "exit", "treasure"]
    gen_methods = ["MazeBacktracker", "MazeGrowth", "NoDeadEnds"]

    def __init__(self, difficulty: int):
        self.plot = []

        self.gen_method = random.choice(self.gen_methods)

        match difficulty:
            case 1:
                self.coin_chance = 0.5
            case 2:
                self.coin_chance = 0.35
            case 3:
                self.coin_chance = 0

        self.player_set = random.randint(1, 3)
        self.rooms = difficulty

        for i in range(0, difficulty):
            self.plot.append(filter(lambda x: x not in self.plot, self.events))
