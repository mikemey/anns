import math

import matplotlib.path as mpath

from tracks import OUTER_TRACK, INNER_TRACK

CAR_BOUNDS = (-20, -11, 29, 11)
MAX_CAR_SPEED = 200
MAX_CAR_ROTATION = 100
SPEED_REDUCE = 1


class Track:
    def __init__(self):
        self.outside = mpath.Path(OUTER_TRACK)
        self.inside = mpath.Path(INNER_TRACK)
        self.inside.contains_point((200, 100))


class PlayerOperation:
    def __init__(self):
        self.accelerate = False
        self.left_turn = False
        self.right_turn = False


class Player:
    def __init__(self):
        self.position = [450, 320]
        self.rotation = 160
        self.speed = MAX_CAR_SPEED

    def update(self, dt, operations):
        if operations.accelerate:
            if operations.left_turn:
                self.rotation -= MAX_CAR_ROTATION * dt
            if operations.right_turn:
                self.rotation += MAX_CAR_ROTATION * dt
            rot = math.radians(self.rotation)
            self.position[0] += math.cos(rot) * self.speed * dt
            self.position[1] -= math.sin(rot) * self.speed * dt


class RacerEngine:
    def __init__(self):
        self.player = Player()
        self.score = 0

    def update(self, dt, operations):
        self.player.update(dt, operations)
