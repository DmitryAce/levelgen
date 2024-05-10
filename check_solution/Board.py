from enum import Enum, auto
from typing import List, Tuple


class Tile(Enum):
    NONE = auto()
    WALL = auto()
    DOOR = auto()
    COIN = auto()
    TREASURE = auto()


class Board:
    __translate = {
        " ": Tile.NONE,
        "#": Tile.WALL,
        "D": Tile.DOOR,
        "C": Tile.COIN,
        "T": Tile.TREASURE
    }

    def __init__(self, width, height):
        self.__shape: List[int] = [width, height]  # x, y
        self.__map: List[List[Tile]] = [
            [Tile.NONE for _ in range(width)]
            for _ in range(height)
        ]
        self.__init_translate__()

    def __init_translate__(self):
        for key, val in dict(self.__translate).items():
            self.__translate[val] = key

    def render(self):
        return "\n".join(["".join(map(lambda x: self.__translate[x], s)) for s in self.__map])

    def __str__(self):
        return self.render()

    @classmethod
    def from_matrix(cls, matrix: List[List[str]]):
        instance = cls(len(matrix), len(matrix[0]))
        for x, row in enumerate(matrix):
            for y, tile in enumerate(row):
                instance.set_tile(x, y, cls.__translate[tile.upper()])
        return instance

    def add_border(self):
        """
        Добавляет границу к карте
        """

        # Верхняя граница
        if not all(map(lambda t: t == Tile.WALL, self.__map[0])):
            self.__map.insert(0, [Tile.WALL] * self.__shape[0])
            self.__shape[1] += 1

        # Нижняя граница
        if not all(map(lambda t: t == Tile.WALL, self.__map[-1])):
            self.__map.append([Tile.WALL] * self.__shape[0])
            self.__shape[1] += 1

        # Левая граница
        if not all(map(lambda t: t == Tile.WALL, map(lambda c: c[0], self.__map))):
            for i in range(self.__shape[1]):
                self.__map[i].insert(0, Tile.WALL)
            self.__shape[0] += 1

        # Правая граница
        if not all(map(lambda t: t == Tile.WALL, map(lambda c: c[-1], self.__map))):
            for i in range(self.__shape[1]):
                self.__map[i].append(Tile.WALL)
            self.__shape[0] += 1

        return self

    def get_shape(self) -> List[int]:
        return self.__shape

    def get_tile(self, x: int, y: int) -> Tile:
        return self.__map[y][x]

    def set_tile(self, x: int, y: int, tile: Tile):
        self.__map[y][x] = tile
        return self

    def clear_room(self, x1, y1, x2, y2):
        for i in range(x1, x2):
            for j in range(y1, y2):
                self.__map[j][i] = Tile.NONE
        return self
