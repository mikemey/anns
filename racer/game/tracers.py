import math

import numpy as np
import shapely
from shapely.geometry import LineString

from .tracks import OUTER_TRACK, INNER_TRACK, TRACK_SIZE

OUTER_LINE = LineString(np.reshape(OUTER_TRACK, (-1, 2)))
INNER_LINE = LineString(np.reshape(INNER_TRACK, (-1, 2)))

TRACE_LEN = TRACK_SIZE[0]
DEG_20 = math.pi / 9
DEG_40 = math.pi / 9 * 2
DEG_65 = math.pi / 36 * 13
DEG_90 = math.pi / 2

TRACE_LINE_ANGLES = [DEG_90, DEG_65, DEG_40, DEG_20, 0, -DEG_20, -DEG_40, -DEG_65, -DEG_90]


def get_trace_distances(pos, rotation_grad):
    rot = math.radians(rotation_grad)
    return [closest_distance_on_line(pos, rot + angle) for angle in TRACE_LINE_ANGLES]


def get_trace_points(pos, rotation_grad):
    rot = math.radians(rotation_grad)
    return [closest_point_on_line(pos, rot + angle) for angle in TRACE_LINE_ANGLES]


def closest_distance_on_line(pos, rot):
    cross_pts = cross_points_on_line(pos, rot)
    return min(np.sum((np.abs(np.array(cross_pts) - pos)), axis=1))


def closest_point_on_line(pos, rot):
    cross_pts = cross_points_on_line(pos, rot)
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
