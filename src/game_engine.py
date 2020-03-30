from enum import Enum, auto

from numpy import array


class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    HALT = auto()


MOVE_VECTOR = {
    Direction.UP: array([0, 1]),
    Direction.DOWN: array([0, -1]),
    Direction.LEFT: array([-1, 0]),
    Direction.RIGHT: array([1, 0]),
    Direction.HALT: array([0, 0])
}
BOX_REWARD = 10


def positions_contains(all_pos, pos):
    for p in all_pos:
        if (p == pos).all():
            return True
    return False


class GameListener:
    def __init__(self):
        self.listener = []

    def add(self, listener):
        self.listener.append(listener)

    def new_position(self, pos):
        for listener in self.listener:
            listener.new_position(pos)

    def box_move(self):
        for listener in self.listener:
            listener.box_move()


class BoxPusherEngine:
    def __init__(self, level_config):
        self.field_size = level_config['field']
        self.player = array(level_config['player'])
        self.walls = level_config['walls']
        self.boxes = [array(box_pos) for box_pos in level_config['boxes']]
        self.goal = level_config['goal']
        self.points = level_config['max_points']
        self.game_won = False
        self.game_lost = False
        self.listeners = GameListener()

    def game_over(self):
        return self.game_won or self.game_lost

    def player_move(self, direction):
        if self.game_over():
            return

        self.points -= 1

        move = MOVE_VECTOR[direction]
        new_pos = self.player + move
        if not self.__can_move_to__(new_pos):
            move = MOVE_VECTOR[Direction.HALT]
        else:
            move = self.__check_boxes__(new_pos, move)

        if len(self.boxes) <= 0:
            self.game_won = True
        if self.points <= 0:
            self.game_lost = True

        self.player += move
        self.listeners.new_position(self.player)

    def __check_boxes__(self, player_pos, move):
        for ix, box in enumerate(self.boxes):
            if (box == player_pos).all():
                new_box_pos = box + move
                if self.__is_occupied__(new_box_pos):
                    move = MOVE_VECTOR[Direction.HALT]
                else:
                    self.listeners.box_move()
                if self.__is_goal__(new_box_pos):
                    self.points += BOX_REWARD
                    del self.boxes[ix]
                else:
                    self.boxes[ix] += move
        return move

    def __can_move_to__(self, position):
        return not positions_contains(self.walls, position) \
               and 0 <= position[0] < self.field_size[0] \
               and 0 <= position[1] < self.field_size[1]

    def __is_occupied__(self, position):
        return not self.__can_move_to__(position) or positions_contains(self.boxes, position)

    def __is_goal__(self, position):
        return (self.goal == position).all()
