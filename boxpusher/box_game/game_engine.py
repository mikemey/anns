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


class Level:
    def __init__(self, field_size, player, walls, boxes, goal, max_points):
        self.field_size = field_size
        self.player = player
        self.walls = walls
        self.boxes = boxes
        self.goal = goal
        self.max_points = max_points

    def print(self):
        intend = '>>'
        separator = intend + '─' * (2 * self.field_size[0] + 2)
        field = [['░░'] * self.field_size[0] for _ in range(self.field_size[1])]

        field[self.player[1]][self.player[0]] = '├┘'
        field[self.goal[1]][self.goal[0]] = '╰╯'
        for box in self.boxes:
            field[box[1]][box[0]] = '[]'
        for wall in self.walls:
            field[wall[1]][wall[0]] = '▐▍'

        print(separator)
        for line in reversed(field):
            print(intend, ''.join(line))
        print(separator)


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

    def invalid_move(self):
        for listener in self.listener:
            listener.invalid_move()


class BoxPusherEngine:
    def __init__(self, level: Level):
        self.field_size = level.field_size
        self.player = array(level.player)
        self.walls = level.walls
        self.boxes = [array(box_pos) for box_pos in level.boxes]
        self.goal = level.goal
        for box in self.boxes:
            assert not (box == self.goal).all(), "box cannot have same position as goal: {}".format(box)

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
            self.listeners.invalid_move()
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
                    self.listeners.invalid_move()
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
        return not self.positions_contains(self.walls, position) \
               and 0 <= position[0] < self.field_size[0] \
               and 0 <= position[1] < self.field_size[1]

    def __is_occupied__(self, position):
        return not self.can_move_to(position) or self.positions_contains(self.boxes, position)

    def __is_goal__(self, position):
        return (self.goal == position).all()

    @staticmethod
    def positions_contains(all_pos, pos):
        for p in all_pos:
            if (p == pos).all():
                return True
        return False
