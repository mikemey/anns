from enum import Enum


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class BoxPusherEngine:
    def __init__(self):
        self.field_size = (8, 6)
        self.player_pos = [0, 4]

    def player_move(self, direction):
        if direction == Direction.UP:
            self.player_pos[1] += 1
        elif direction == Direction.DOWN:
            self.player_pos[1] -= 1
        elif direction == Direction.LEFT:
            self.player_pos[0] -= 1
        elif direction == Direction.RIGHT:
            self.player_pos[0] += 1
