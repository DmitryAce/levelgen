import unittest
from Plot import Plot
from Board import Board, Tile
from generator import *


class TestPlot(unittest.TestCase):
    def test_plot_init(self):
        self.assertEqual(True, False)


class TestBoard(unittest.TestCase):
    def test_map_init(self):
        self.assertEqual("   \n   \n   ", Board(3, 3).render())
        self.assertEqual("#####\n#   #\n#   #\n#   #\n#####", Board(3, 3).add_border().render())
        brd = init_map(2, "MazeGrowth")
        brd = generate_treasures(brd, Plot(2))
        print(brd[1])


if __name__ == '__main__':
    unittest.main()
