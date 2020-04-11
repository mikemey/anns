import math

import matplotlib.path as mpath
import numpy as np

from tracks import *

CAR_BOUNDS = (-19, -11, 29, 11)
CAR_BOUND_POINTS = (CAR_BOUNDS[0], CAR_BOUNDS[1], CAR_BOUNDS[2], CAR_BOUNDS[1],
                    CAR_BOUNDS[2], CAR_BOUNDS[3], CAR_BOUNDS[0], CAR_BOUNDS[3]
                    )
CAR_COLL_BOX = np.reshape(CAR_BOUND_POINTS, (-1, 2)) * 0.9
MAX_CAR_SPEED = 300
MAX_CAR_ROTATION = 200
CAR_FRICTION = 0.98
MIN_SPEED = 10


def ignore_speed(speed):
    return abs(speed) < MIN_SPEED


class PlayerOperation:
    FWD_IX = 0
    REV_IX = 1
    LEFT_IX = 2
    RIGHT_IX = 3

    def __init__(self):
        self._data = [False] * 4

    def get_move_factor(self):
        if self._data[self.FWD_IX]:
            return 1
        if self._data[self.REV_IX]:
            return -1
        return 0

    def get_turn_factor(self):
        if self._data[self.LEFT_IX]:
            return -1
        if self._data[self.RIGHT_IX]:
            return 1
        return 0

    def accelerate(self):
        self._data[self.FWD_IX] = True
        self._data[self.REV_IX] = False

    def reverse(self):
        self._data[self.FWD_IX] = False
        self._data[self.REV_IX] = True

    def stop_direction(self):
        self._data[self.FWD_IX] = False
        self._data[self.REV_IX] = False

    def turn_left(self):
        self._data[self.LEFT_IX] = True
        self._data[self.RIGHT_IX] = False

    def turn_right(self):
        self._data[self.LEFT_IX] = False
        self._data[self.RIGHT_IX] = True

    def stop_left(self):
        self._data[self.LEFT_IX] = False

    def stop_right(self):
        self._data[self.RIGHT_IX] = False


class RacerEngine:
    def __init__(self):
        self.player = Player()
        self.track = Track()
        self.score = 0
        self.game_over = False

    def update(self, dt, operations):
        self.player.update(dt, operations)
        if not self.track.contains_points(self.player.boundaries):
            self.game_over = True
        elif not ignore_speed(self.player.speed):
            self.score += 1 if self.player.speed > 0 else -2


class Player:
    def __init__(self):
        self.position = INIT_CAR_POSITION
        self.rotation = INIT_CAR_ROTATION
        self.speed = 0
        self.boundaries = []

    def update(self, dt, operations: PlayerOperation):
        self.speed *= CAR_FRICTION
        move_fact = operations.get_move_factor()
        if move_fact:
            new_speed = self.speed + MAX_CAR_SPEED * dt * move_fact
            self.speed = min(MAX_CAR_SPEED, max(-MAX_CAR_SPEED, new_speed))
        elif ignore_speed(self.speed):
            self.speed = 0

        if not ignore_speed(self.speed):
            turn_fact = operations.get_turn_factor() * math.copysign(1, self.speed)
            allowed_rot = MAX_CAR_ROTATION * ((abs(self.speed) / MAX_CAR_SPEED) ** 0.5)
            self.rotation += allowed_rot * dt * turn_fact

        rot = math.radians(self.rotation)
        self.position[0] += math.cos(rot) * self.speed * dt
        self.position[1] -= math.sin(rot) * self.speed * dt
        self.boundaries = self.__update_boundaries__(rot)

    def __update_boundaries__(self, radians):
        c, s = np.cos(radians), np.sin(radians)
        j = np.array([[c, s], [-s, c]])

        def move_rotate_pt(pt):
            m = np.dot(j, pt)
            return np.array(self.position) + m.T

        return [move_rotate_pt(pt) for pt in CAR_COLL_BOX]


class Track:
    def __init__(self):
        self.outside = mpath.Path(np.reshape(OUTER_TRACK, (-1, 2)))
        self.inside = mpath.Path(np.reshape(INNER_TRACK, (-1, 2)))

    def contains_points(self, points):
        return all(self.outside.contains_points(points)) and \
               not any(self.inside.contains_points(points))
