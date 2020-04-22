import math
from functools import reduce

import numpy as np
from shapely.geometry import LineString

from .racer_engine import create_obstacles_collision_boxes
from .tracks import Level

DEG_20 = math.pi / 9
DEG_40 = math.pi / 9 * 2
DEG_65 = math.pi / 36 * 13
DEG_90 = math.pi / 2

TRACE_LINE_ANGLES = [DEG_90, DEG_65, DEG_40, DEG_20, 0, -DEG_20, -DEG_40, -DEG_65, -DEG_90]


# TODO train best players on new trace-lines:
# DEG_15 = math.pi / 12
# DEG_30 = math.pi / 6
# DEG_60 = math.pi / 3
# DEG_90 = math.pi / 2
#
# TRACE_LINE_ANGLES = [DEG_90, DEG_60, DEG_30, DEG_15, 0, -DEG_15, -DEG_30, -DEG_60, -DEG_90]


class TracerLines:
    def __init__(self, level: Level):
        self.trace_len = level.width
        obstacle_coll_boxes = create_obstacles_collision_boxes(level.obstacles)
        self.collision_boxes = [
            LineString(np.reshape(level.outer_track, (-1, 2))),
            LineString(np.reshape(level.inner_track, (-1, 2))),
            *[LineString(coll_box.exterior.coords) for coll_box in obstacle_coll_boxes]
        ]

    def get_trace_distances(self, pos, rotation_grad):
        rot = math.radians(rotation_grad)
        return [self.__closest_distance_on_line(pos, rot + angle) for angle in TRACE_LINE_ANGLES]

    def get_trace_points(self, pos, rotation_grad):
        rot = math.radians(rotation_grad)
        return [self.__closest_point_on_line(pos, rot + angle) for angle in TRACE_LINE_ANGLES]

    def __closest_distance_on_line(self, pos, rot):
        cross_pts = self.__cross_points_on_line(pos, rot)
        if len(cross_pts) == 0:
            return self.trace_len
        return min(np.sum((np.abs(np.array(cross_pts) - pos)), axis=1))

    def __closest_point_on_line(self, pos, rot):
        cross_pts = self.__cross_points_on_line(pos, rot)
        if len(cross_pts) == 0:
            return pos
        sq_distances = np.sum((np.array(cross_pts) - pos) ** 2, axis=1)
        return cross_pts[np.argmin(sq_distances)]

    def __cross_points_on_line(self, pos, rot):
        trace_target = (pos[0] + math.cos(rot) * self.trace_len, pos[1] - math.sin(rot) * self.trace_len)
        tracer = LineString([pos, trace_target])
        intersections = [box.intersection(tracer) for box in self.collision_boxes]
        candidates = reduce(lambda all_xs, curr_xs: all_xs.union(curr_xs), intersections)

        cross_pts = []
        if not candidates.is_empty:
            if hasattr(candidates, 'geoms'):
                for pts in getattr(candidates, 'geoms'):
                    cross_pts.append((pts.x, pts.y))
            else:
                cross_pts.append((candidates.x, candidates.y))

        return cross_pts
