import math

import numpy as np
import shapely
from shapely.geometry import LineString

OUTER_TRACK = [465, 305, 380, 270, 288, 210, 235, 98, 161, 36, 48, 27, 14, 109, 34, 652, 104, 693, 203, 689,
               282, 633, 322, 543, 303, 454, 237, 403, 378, 473, 435, 576, 512, 647, 638, 671, 766, 634, 875,
               438, 941, 179, 927, 100, 861, 37, 720, 34, 633, 103, 570, 202, 546, 267, 518, 297, 465, 305]

INNER_TRACK = [465, 390, 362, 358, 210, 260, 145, 139, 105, 128, 124, 584, 154, 607, 193, 591, 219, 558, 214,
               497, 154, 444, 128, 389, 151, 318, 232, 315, 359, 362, 477, 428, 516, 518, 591, 578, 696, 565,
               769, 436, 811, 304, 847, 159, 819, 129, 753, 123, 703, 166, 660, 252, 617, 326, 550, 378, 465, 390]

TRACK_SIZE = 1000, 700
INIT_CAR_POSITION = [505, 345]
INIT_CAR_ROTATION = 180

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
