import math

import matplotlib.path as mpath

from tracks import OUTER_TRACK, INNER_TRACK

CAR_BOUNDS = (-20, -11, 29, 11)
CAR_SPEED = 250
CAR_ROTATION = 200
CAR_FRICTION = 0.98
MIN_SPEED = 10


def ignore_speed(speed):
    return abs(speed) < MIN_SPEED


class Track:
    def __init__(self):
        self.outside = mpath.Path(OUTER_TRACK)
        self.inside = mpath.Path(INNER_TRACK)
        self.inside.contains_point((200, 100))


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


class Player:
    def __init__(self):
        self.position = [450, 320]
        self.rotation = 170
        self.speed = 0

    def update(self, dt, operations: PlayerOperation):
        self.speed *= CAR_FRICTION
        move_fact = operations.get_move_factor()
        if move_fact:
            new_speed = self.speed + CAR_SPEED * dt * move_fact
            self.speed = min(CAR_SPEED, max(-CAR_SPEED, new_speed))
        elif ignore_speed(self.speed):
            self.speed = 0

        if not ignore_speed(self.speed):
            turn_fact = operations.get_turn_factor()
            allowed_rot = CAR_ROTATION * ((abs(self.speed) / CAR_SPEED) ** 0.5)
            self.rotation += allowed_rot * dt * turn_fact

        rot = math.radians(self.rotation)
        self.position[0] += math.cos(rot) * self.speed * dt
        self.position[1] -= math.sin(rot) * self.speed * dt


class RacerEngine:
    def __init__(self):
        self.player = Player()
        self.score = 0

    def update(self, dt, operations):
        self.player.update(dt, operations)
