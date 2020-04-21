import math

import numpy as np
import shapely
from shapely.geometry import LineString

from .tracks import OUTER_TRACK, INNER_TRACK, TRACK_SIZE

OUTER_LINE = LineString(np.reshape(OUTER_TRACK, (-1, 2)))
INNER_LINE = LineString(np.reshape(INNER_TRACK, (-1, 2)))

TRACE_LEN = TRACK_SIZE[0]
DEG_15 = math.pi / 12
DEG_30 = math.pi / 6
DEG_45 = math.pi / 4
DEG_90 = math.pi / 2

TRACE_LINE_ANGLES = [DEG_90, DEG_45, DEG_30, DEG_15, 0, -DEG_15, -DEG_30, -DEG_45, -DEG_90]


def get_trace_distances(pos, rotation_grad):
    rot = math.radians(rotation_grad)
    return [closest_distance_on_line(pos, rot + angle) for angle in TRACE_LINE_ANGLES]


def get_trace_points(pos, rotation_grad):
    rot = math.radians(rotation_grad)
    return [closest_point_on_line(pos, rot + angle) for angle in TRACE_LINE_ANGLES]


def closest_distance_on_line(pos, rot):
    cross_pts = cross_points_on_line(pos, rot)
    if len(cross_pts) == 0:
        return TRACE_LEN
    return min(np.sum((np.abs(np.array(cross_pts) - pos)), axis=1))


def closest_point_on_line(pos, rot):
    cross_pts = cross_points_on_line(pos, rot)
    if len(cross_pts) == 0:
        return pos
    sq_distances = np.sum((np.array(cross_pts) - pos) ** 2, axis=1)
    return cross_pts[np.argmin(sq_distances)]


def cross_points_on_line(pos, rot):
    trace_target = (pos[0] + math.cos(rot) * TRACE_LEN, pos[1] - math.sin(rot) * TRACE_LEN)
    tracer = LineString([pos, trace_target])
    candidates = OUTER_LINE.intersection(tracer).union(INNER_LINE.intersection(tracer))
    cross_pts = []
    if not candidates.is_empty:
        if isinstance(candidates, shapely.geometry.MultiPoint):
            for pts in candidates.geoms:
                cross_pts.append((pts.x, pts.y))
        else:
            cross_pts.append((candidates.x, candidates.y))

    return cross_pts
