from enum import Enum


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class BoxPusherEngine:
    def __init__(self):
        self.field_size = (6, 6)
        self.player_pos = (2, 4)
        self.walls = [
            (0, 5), (1, 5), (2, 5), (3, 5), (4, 5), (5, 5),
            (0, 4), (3, 4), (5, 4),
            (0, 3), (5, 3),
            (0, 2), (3, 2), (5, 2),
            (0, 1), (5, 1),
            (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0)
        ]

    def player_move(self, direction):
        new_x = self.player_pos[0]
        new_y = self.player_pos[1]
        if direction == Direction.UP:
            new_y += 1
        elif direction == Direction.DOWN:
            new_y -= 1
        elif direction == Direction.LEFT:
            new_x -= 1
        elif direction == Direction.RIGHT:
            new_x += 1

        new_pos = (new_x, new_y)
        for wall in self.walls:
            if new_pos == wall:
                new_pos = self.player_pos
                break

        self.player_pos = new_pos
