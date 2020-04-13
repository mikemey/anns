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


def get_trace_points(pos, rotation_grad):
    rot = math.radians(rotation_grad)
    return [
        closest_point_on_line(pos, rot),
        closest_point_on_line(pos, rot + DEG_20),
        closest_point_on_line(pos, rot - DEG_20),
        closest_point_on_line(pos, rot + DEG_40),
        closest_point_on_line(pos, rot - DEG_40),
        closest_point_on_line(pos, rot + DEG_65),
        closest_point_on_line(pos, rot - DEG_65),
        closest_point_on_line(pos, rot + DEG_90),
        closest_point_on_line(pos, rot - DEG_90)
    ]


def closest_point_on_line(pos, rot):
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

    np_cross_pts = np.array(cross_pts)
    if len(np_cross_pts) == 0:
        return []
    sq_distances = np.sum((np_cross_pts - pos) ** 2, axis=1)
    return cross_pts[np.argmin(sq_distances)]
