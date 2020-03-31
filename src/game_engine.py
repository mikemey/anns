from enum import Enum, auto

from numpy import array

from training_levels import Level


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

    def box_in_goal(self):
        for listener in self.listener:
            listener.box_in_goal()


class BoxPusherEngine:
    def __init__(self, level: Level):
        self.field_size = level.field_size
        self.player = array(level.player)
        self.walls = level.walls
        self.boxes = [array(box_pos) for box_pos in level.boxes]
        self.goal = level.goal
        self.points = level.max_points
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
        if not self.can_move_to(new_pos):
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
                    self.listeners.box_in_goal()
                    del self.boxes[ix]
                else:
                    self.boxes[ix] += move
        return move

    def can_move_to(self, position):
        return not positions_contains(self.walls, position) \
               and 0 <= position[0] < self.field_size[0] \
               and 0 <= position[1] < self.field_size[1]

    def __is_occupied__(self, position):
        return not self.can_move_to(position) or positions_contains(self.boxes, position)

    def __is_goal__(self, position):
        return (self.goal == position).all()
