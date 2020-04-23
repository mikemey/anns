from typing import Tuple, List


class TrackPosition:
    def __init__(self, x, y, rot):
        self.x, self.y, self.rot = x, y, rot

    def __repr__(self):
        return 'TrackPosition({:.0f}, {:.0f}, {:.0f})'.format(self.x, self.y, self.rot)


class Level:
    def __init__(self, name, width, height,
                 outer_track, outer_track_offset,
                 inner_track, inner_track_offset,
                 single_car: TrackPosition,
                 two_cars: Tuple[TrackPosition, TrackPosition],
                 obstacles: List[TrackPosition]):
        self.name = name
        self.width = width
        self.height = height
        self.outer_track = outer_track
        self.outer_track_offset = outer_track_offset
        self.inner_track = inner_track
        self.inner_track_offset = inner_track_offset
        self.single_car = single_car
        self.two_cars = two_cars
        self.obstacles = obstacles


EMPTY_LEVEL = Level(
    name='unnamed 0', width=1000, height=700,
    outer_track=[80, 70, 200, 70, 180, 50], outer_track_offset=0,
    inner_track=[80, 130, 200, 130, 180, 150], inner_track_offset=0,
    single_car=TrackPosition(100, 100, 0), two_cars=(),
    obstacles=[]
)

__mercury_track = {
    'width': 1000, 'height': 700,
    'outer': [465, 305, 380, 270, 288, 210, 235, 98, 161, 36, 48, 27, 14, 109, 34, 652, 104, 693, 203, 689,
              282, 633, 322, 543, 303, 454, 237, 403, 378, 473, 435, 576, 512, 647, 638, 671, 766, 634, 875,
              438, 941, 179, 927, 100, 861, 37, 720, 34, 633, 103, 570, 202, 546, 267, 518, 297, 465, 305],
    'inner': [465, 390, 362, 358, 210, 260, 145, 139, 105, 128, 124, 584, 154, 607, 193, 591, 219, 558, 214,
              497, 154, 444, 128, 389, 151, 318, 232, 315, 359, 362, 477, 428, 516, 518, 591, 578, 696, 565,
              769, 436, 811, 304, 847, 159, 819, 129, 753, 123, 703, 166, 660, 252, 617, 326, 550, 378, 465, 390]
}

Mercury_1 = Level(
    name='mercury 1', width=__mercury_track['width'], height=__mercury_track['height'],
    inner_track=__mercury_track['inner'],
    outer_track=__mercury_track['outer'],
    outer_track_offset=3521.7, inner_track_offset=2890,
    single_car=TrackPosition(505, 344, 180),
    two_cars=(TrackPosition(507, 357, 180), TrackPosition(502, 324, 180)),
    obstacles=[TrackPosition(126, 157, 2), TrackPosition(675, 550, 7), TrackPosition(800, 145, -5), TrackPosition(59, 647, 59)]
)

Venus = Level(
    name='venus 1', width=1000, height=700,
    outer_track=[359, 288, 554, 292, 599, 341, 614, 403, 551, 537, 481, 606, 384, 664, 287, 685, 14, 683, 20, 18,
                 340, 17, 440, 28, 556, 29, 626, 15, 983, 16, 984, 366, 923, 457, 837, 609, 789, 667, 720, 684, 641,
                 665, 572, 601, 565, 535, 587, 467, 640, 392, 719, 302, 719, 280, 713, 263, 657, 262, 563, 271, 370,
                 267, 264, 242, 235, 265, 241, 286, 359, 288],
    outer_track_offset=4618,
    inner_track=[359, 410, 434, 410, 458, 424, 459, 443, 393, 503, 282, 571, 134, 568, 114, 536, 114, 136, 132, 118,
                 277, 120, 416, 182, 560, 184, 703, 116, 863, 121, 876, 133, 875, 332, 801, 441, 740, 542, 718, 543,
                 718, 526, 860, 332, 866, 282, 866, 190, 843, 152, 808, 142, 687, 134, 566, 190, 404, 188, 278, 130,
                 147, 128, 121, 160, 120, 450, 158, 488, 236, 489, 305, 408, 359, 410],
    inner_track_offset=3944,
    single_car=TrackPosition(314, 348, 0), two_cars=(TrackPosition(314, 363, 0), TrackPosition(315, 333, 0)),
    obstacles=[TrackPosition(141, 433, -2), TrackPosition(687, 281, -2), TrackPosition(33, 666, -2),
               TrackPosition(552, 575, 98), TrackPosition(847, 139, 89), TrackPosition(265, 552, 89),
               # TrackPosition(497, 90, 43)
               ]
)

MANUAL_LEVEL = Mercury_1

DEMO_LEVEL = Mercury_1
SHOWCASE_FROM_FILE_LEVEL = Mercury_1

TRAINING_LEVELS = [
    (Mercury_1, 2000),
    (Venus, 2000)
]
