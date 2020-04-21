import math

import numpy as np
from shapely.geometry import Polygon, LinearRing, Point

from .tracks import Level

CAR_BOUNDS = (-15, -11, 33, 11)
CAR_BOUND_POINTS = (CAR_BOUNDS[0], CAR_BOUNDS[1], CAR_BOUNDS[2], CAR_BOUNDS[1],
                    CAR_BOUNDS[2], CAR_BOUNDS[3], CAR_BOUNDS[0], CAR_BOUNDS[3]
                    )
CAR_COLL_BOX = np.reshape(CAR_BOUND_POINTS, (-1, 2)) * 0.95
MAX_CAR_SPEED = 300
MAX_CAR_ROTATION = 200
CAR_FRICTION = 0.98
MIN_SPEED = 10

BOX_COLL_BOX = np.array([[-18, -18], [18, -18], [18, 18], [-18, 18]])


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

    def stop_all(self):
        self._data[self.FWD_IX] = False
        self._data[self.REV_IX] = False
        self._data[self.LEFT_IX] = False
        self._data[self.RIGHT_IX] = False


class RacerEngine:
    def __init__(self, level):
        self.player_state = PlayerState(level)
        self.track = Track(level)
        self.__game_over = False

    @property
    def game_over(self):
        return self.__game_over

    @game_over.setter
    def game_over(self, game_over):
        self.player_state.is_alive = not game_over
        self.__game_over = game_over

    def update(self, dt, operations):
        self.player_state.update(dt, operations)
        if not self.track.contains(self.player_state.boundaries):
            self.game_over = True


class PlayerState:
    EMPTY_DELTAS = ((0, (-100, -100)),) * 2

    def __init__(self, level: Level):
        self.x, self.y, self.rotation = level.single_car.x, level.single_car.y, level.single_car.rot
        self.speed = 0
        self.boundaries = Polygon(np.reshape(CAR_BOUND_POINTS, (-1, 2)))
        self.is_alive = True
        self.distance = 0
        self.last_deltas = self.EMPTY_DELTAS
        self.__distance_tracker = DistanceTracker(level)

    @property
    def relevant_speed(self):
        if self.__ignore_speed():
            return 0
        return self.speed

    def __ignore_speed(self):
        return abs(self.speed) < MIN_SPEED

    def update(self, dt, operations: PlayerOperation):
        self.speed *= CAR_FRICTION
        move_fact = operations.get_move_factor()
        if move_fact:
            new_speed = self.speed + MAX_CAR_SPEED * dt * move_fact
            self.speed = min(MAX_CAR_SPEED, max(-MAX_CAR_SPEED, new_speed))
        elif self.__ignore_speed():
            self.speed = 0

        if not self.__ignore_speed():
            turn_fact = operations.get_turn_factor() * math.copysign(1, self.speed)
            allowed_rot = MAX_CAR_ROTATION * ((abs(self.speed) / MAX_CAR_SPEED) ** 0.5)
            self.rotation += allowed_rot * dt * turn_fact

        rot = math.radians(self.rotation)
        cosine, sine = math.cos(rot), math.sin(rot)
        self.x += cosine * self.speed * dt
        self.y -= sine * self.speed * dt
        self.boundaries = create_collision_box(CAR_COLL_BOX, self.x, self.y, cosine, sine)
        self.__update_distance__()

    def __update_distance__(self):
        deltas = self.__distance_tracker.get_deltas(self.x, self.y)
        self.distance += deltas[0][0] + deltas[1][0]
        self.last_deltas = deltas

    def flattened_boundaries(self):
        return np.array(self.boundaries.exterior.coords[:-1]).flatten()


class Track:
    def __init__(self, level: Level):
        self.__outside = Polygon(np.reshape(level.outer_track, (-1, 2)))
        self.__inside = Polygon(np.reshape(level.inner_track, (-1, 2)))
        self.__obstacles = []
        for pt in level.obstacles:
            rot = math.radians(pt.rot)
            cosine, sine = math.cos(rot), math.sin(rot)
            self.__obstacles.append(create_collision_box(BOX_COLL_BOX, pt.x, pt.y, cosine, sine))

    def contains(self, geometry):
        return self.__outside.contains(geometry) and \
               not self.__inside.intersects(geometry) and \
               not any([obs.intersects(geometry) for obs in self.__obstacles])


class DistanceTracker:
    def __init__(self, level: Level):
        self.__outside_tracker = LineDistanceTracker(level.outer_track, level.outer_track_offset)
        self.__inside_tracker = LineDistanceTracker(level.inner_track, level.inner_track_offset)

    def get_deltas(self, x, y):
        point = Point(x, y)
        return self.__outside_tracker.get_delta(point), self.__inside_tracker.get_delta(point)


class LineDistanceTracker:
    def __init__(self, track, offset):
        self.__line = LinearRing(np.reshape(track, (-1, 2)))
        self.__prev_d = offset
        self.__line_length = np.round(self.__line.length)
        self.__delta_limit = self.__line_length - 100

    def get_delta(self, point):
        dist = np.round(self.__line.project(point))
        return self.__get_delta_score(dist), self.__get_line_point(dist)

    def __get_delta_score(self, dist):
        delta_score = dist - self.__prev_d
        if delta_score < -self.__delta_limit:
            delta_score = self.__line_length - self.__prev_d + dist
        elif delta_score > self.__delta_limit:
            delta_score = -(self.__prev_d + self.__line_length - dist)
        self.__prev_d = dist
        return delta_score

    def __get_line_point(self, dist):
        pts = self.__line.interpolate(dist)
        return list(pts.coords)[0]


def create_collision_box(box, x, y, cosine, sine):
    j = np.array([[cosine, sine], [-sine, cosine]])
    new_boundaries = []
    for ix in range(len(box)):
        m = np.dot(j, box[ix])
        moved = np.array((x, y)) + m.T
        new_boundaries.append(moved)
    return Polygon(new_boundaries)
