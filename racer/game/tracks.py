from typing import Tuple, List

__OUTER_TRACK = [465, 305, 380, 270, 288, 210, 235, 98, 161, 36, 48, 27, 14, 109, 34, 652, 104, 693, 203, 689,
                 282, 633, 322, 543, 303, 454, 237, 403, 378, 473, 435, 576, 512, 647, 638, 671, 766, 634, 875,
                 438, 941, 179, 927, 100, 861, 37, 720, 34, 633, 103, 570, 202, 546, 267, 518, 297, 465, 305]

__INNER_TRACK = [465, 390, 362, 358, 210, 260, 145, 139, 105, 128, 124, 584, 154, 607, 193, 591, 219, 558, 214,
                 497, 154, 444, 128, 389, 151, 318, 232, 315, 359, 362, 477, 428, 516, 518, 591, 578, 696, 565,
                 769, 436, 811, 304, 847, 159, 819, 129, 753, 123, 703, 166, 660, 252, 617, 326, 550, 378, 465, 390]

__TRACK_SIZE = 1000, 700
__INIT_CAR_POSITION = [505, 344]
__INIT_CAR_ROTATION = 180
__INNER_TRACK_OFFSET = 2890
__OUTER_TRACK_OFFSET = 3521.7


class TrackPosition:
    def __init__(self, x, y, rot):
        self.x, self.y, self.rot = x, y, rot

    def __repr__(self):
        return 'TrackPosition({:.0f}, {:.0f}, {:.0f})'.format(self.x, self.y, self.rot)


class Level:
    def __init__(self, width, height,
                 outer_track, outer_track_offset,
                 inner_track, inner_track_offset,
                 single_car: TrackPosition,
                 two_cars: Tuple[TrackPosition, TrackPosition],
                 obstacles: List[TrackPosition]):
        self.width = width
        self.height = height
        self.outer_track = outer_track
        self.outer_track_offset = outer_track_offset
        self.inner_track = inner_track
        self.inner_track_offset = inner_track_offset
        self.single_car = single_car
        self.two_cars = two_cars
        self.obstacles = obstacles


default_level = Level(
    width=1000, height=700,
    outer_track=[465, 305, 380, 270, 288, 210, 235, 98, 161, 36, 48, 27, 14, 109, 34, 652, 104, 693, 203, 689,
                 282, 633, 322, 543, 303, 454, 237, 403, 378, 473, 435, 576, 512, 647, 638, 671, 766, 634, 875,
                 438, 941, 179, 927, 100, 861, 37, 720, 34, 633, 103, 570, 202, 546, 267, 518, 297, 465, 305],
    outer_track_offset=3521.7,
    inner_track=[465, 390, 362, 358, 210, 260, 145, 139, 105, 128, 124, 584, 154, 607, 193, 591, 219, 558, 214,
                 497, 154, 444, 128, 389, 151, 318, 232, 315, 359, 362, 477, 428, 516, 518, 591, 578, 696, 565,
                 769, 436, 811, 304, 847, 159, 819, 129, 753, 123, 703, 166, 660, 252, 617, 326, 550, 378, 465, 390],
    inner_track_offset=2890,
    single_car=TrackPosition(505, 344, 180),
    two_cars=(TrackPosition(507, 357, 180), TrackPosition(502, 324, 180)),
    obstacles=[TrackPosition(126, 157, 2), TrackPosition(675, 550, 7), TrackPosition(800, 145, -5), TrackPosition(59, 647, 59)]
)
