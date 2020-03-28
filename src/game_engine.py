from enum import Enum
from numpy import array


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


MOVE_VECTOR = {
    Direction.UP: array([0, 1]),
    Direction.DOWN: array([0, -1]),
    Direction.LEFT: array([-1, 0]),
    Direction.RIGHT: array([1, 0])
}


def in_positions(all_pos, pos):
    for p in all_pos:
        if (p == pos).all():
            return True
    return False


class BoxPusherEngine:
    def __init__(self, level_config):
        self.field_size = level_config['field']
        self.player = array(level_config['player'])
        self.walls = level_config['walls']
        self.boxes = [array(box_pos) for box_pos in level_config['boxes']]
        self.goal = level_config['goal']

    def player_move(self, direction):
        move = MOVE_VECTOR[direction]
        new_pos = self.player + move
        if self.__is_wall__(new_pos):
            return

        for ix, box in enumerate(self.boxes):
            if (box == new_pos).all():
                new_box_pos = box + move
                if self.__is_occupied__(new_box_pos):
                    return
                if self.__is_goal__(new_box_pos):
                    del self.boxes[ix]
                else:
                    self.boxes[ix] += move

        self.player += move

    def __is_wall__(self, position):
        return in_positions(self.walls, position)

    def __is_box__(self, position):
        return in_positions(self.boxes, position)

    def __is_occupied__(self, position):
        return self.__is_wall__(position) or self.__is_box__(position)

    def __is_goal__(self, position):
        return (self.goal == position).all()
