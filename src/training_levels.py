import random

import numpy as np


class Level:
    def __init__(self, field_size, player, walls, boxes, goal, max_points):
        self.field_size = field_size
        self.player = player
        self.walls = walls
        self.boxes = boxes
        self.goal = goal
        self.max_points = max_points

    @staticmethod
    def generate_level():
        try:
            occupied = []
            field_size = (5, 5)
            # walls = [find_available_pos(occupied, 0, 5) for _ in range(random.randrange(0, 4))]
            walls = []
            player = Level.find_available_pos(occupied, 0, 5)
            goal = Level.find_available_pos(occupied, 0, 5, (2, 2), 1)
            box = Level.find_available_pos(occupied, 1, 4, goal, 3, True)
            return Level(field_size, player, walls, [box], goal, max_points=20)
        except RecursionError:
            return Level.generate_level()

    @staticmethod
    def find_available_pos(occupied, start, exclusive_end, avoid_pos=None, min_dist=0, avoid_same_line=False):
        new_pos = (random.randrange(start, exclusive_end, 1), random.randrange(start, exclusive_end, 1))
        if new_pos in occupied:
            return Level.find_available_pos(occupied, start, exclusive_end, avoid_pos, min_dist, avoid_same_line)
        elif avoid_pos is not None and distance_between(new_pos, avoid_pos) < min_dist:
            return Level.find_available_pos(occupied, start, exclusive_end, avoid_pos, min_dist, avoid_same_line)
        elif avoid_same_line and (new_pos[0] == avoid_pos[0] or new_pos[1] == avoid_pos[1]):
            return Level.find_available_pos(occupied, start, exclusive_end, avoid_pos, min_dist, avoid_same_line)
        else:
            occupied.append(new_pos)
            return new_pos

    def as_game_config(self):
        return {
            'field': self.field_size, 'player': self.player, 'walls': self.walls,
            'boxes': self.boxes, 'goal': self.goal, 'max_points': self.max_points
        }

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


def distance_between(pos_a, pos_b):
    return sum(np.absolute(np.array(pos_a) - np.array(pos_b)))


if __name__ == '__main__':
    pass
