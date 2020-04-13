import random

import numpy as np

from game_engine import Level


def generate_level():
    try:
        occupied = []
        field_size = (5, 5)
        # walls = [find_available_pos(occupied, 0, 5) for _ in range(random.randrange(0, 4))]
        walls = []
        player = find_available_pos(occupied, 0, 5)
        goal = find_available_pos(occupied, 0, 5, (2, 2), 1)
        box = find_available_pos(occupied, 1, 4, goal, 3, True)
        return Level(field_size, player, walls, [box], goal, max_points=20)
    except RecursionError:
        return generate_level()


def find_available_pos(occupied, start, exclusive_end, avoid_pos=None, min_dist=0, avoid_same_line=False):
    new_pos = (random.randrange(start, exclusive_end, 1), random.randrange(start, exclusive_end, 1))
    if new_pos in occupied:
        return find_available_pos(occupied, start, exclusive_end, avoid_pos, min_dist, avoid_same_line)
    elif avoid_pos is not None and distance_between(new_pos, avoid_pos) < min_dist:
        return find_available_pos(occupied, start, exclusive_end, avoid_pos, min_dist, avoid_same_line)
    elif avoid_same_line and (new_pos[0] == avoid_pos[0] or new_pos[1] == avoid_pos[1]):
        return find_available_pos(occupied, start, exclusive_end, avoid_pos, min_dist, avoid_same_line)
    else:
        occupied.append(new_pos)
        return new_pos


def distance_between(pos_a, pos_b):
    return sum(np.absolute(np.array(pos_a) - np.array(pos_b)))


def distance_sum_between(positions, pos):
    total_distance = 0
    for p in positions:
        total_distance += distance_between(p, pos)
    return total_distance
