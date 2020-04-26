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


__empty_level = Level(
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
              769, 436, 811, 304, 847, 159, 819, 129, 753, 123, 703, 166, 660, 252, 617, 326, 550, 378, 465, 390],
    'two_cars': (TrackPosition(507, 357, 180), TrackPosition(502, 324, 180))
}
__mercury_mod_1 = {
    'name': 'mercury 1', 'outer_track_offset': 3521.7, 'inner_track_offset': 2890,
    'single_car': TrackPosition(505, 344, 180),
    'obstacles': [TrackPosition(126, 158, 2), TrackPosition(675, 549, 7), TrackPosition(800, 146, -5), TrackPosition(59, 647, 59)]
}
__mercury_mod_2 = {
    'name': 'mercury 2', 'outer_track_offset': 1746, 'inner_track_offset': 1471,
    'single_car': TrackPosition(280, 380, 335),
    'obstacles': [TrackPosition(126, 158, 2), TrackPosition(675, 549, 7), TrackPosition(578, 225, -22), TrackPosition(562, 573, -40)]
}
__mercury_mod_3 = {
    'name': 'mercury 3', 'outer_track_offset': 2488, 'inner_track_offset': 2077,
    'single_car': TrackPosition(790, 500, 68),
    'obstacles': [TrackPosition(59, 647, 59), TrackPosition(35, 250, 2), TrackPosition(730, 530, 60),
                  TrackPosition(882, 348, -15), TrackPosition(100, 450, 2)]
}

__venus_track = {
    'width': 1000, 'height': 700,
    'outer': [359, 288, 554, 292, 599, 341, 614, 403, 551, 537, 481, 606, 384, 664, 287, 685, 14, 683, 20, 18,
              340, 17, 440, 28, 556, 29, 626, 15, 983, 16, 984, 366, 923, 457, 837, 609, 789, 667, 720, 684, 641,
              665, 572, 601, 565, 535, 587, 467, 640, 392, 719, 302, 719, 280, 713, 263, 657, 262, 563, 271, 370,
              267, 264, 242, 235, 265, 241, 286, 359, 288],
    'inner': [359, 410, 434, 410, 458, 424, 459, 443, 393, 503, 282, 571, 134, 568, 114, 536, 114, 136, 132, 118,
              277, 120, 416, 182, 560, 184, 703, 116, 863, 121, 876, 133, 875, 332, 801, 441, 740, 542, 718, 543,
              718, 526, 860, 332, 866, 282, 866, 190, 808, 142, 687, 134, 566, 190, 404, 188, 278, 130,
              147, 128, 121, 160, 120, 450, 158, 488, 236, 489, 305, 408, 359, 410],
    'two_cars': (TrackPosition(314, 363, 0), TrackPosition(315, 333, 0))
}
__venus_mod_1 = {
    'name': 'venus 1', 'outer_track_offset': 4618, 'inner_track_offset': 3938,
    'single_car': TrackPosition(314, 348, 0),
    'obstacles': [TrackPosition(265, 552, 89), TrackPosition(550, 574, 7), TrackPosition(694, 281, -2),
                  TrackPosition(846, 140, 89)]
}
__venus_mod_2 = {
    'name': 'venus 2', 'outer_track_offset': 4261, 'inner_track_offset': 3010,
    'single_car': TrackPosition(486, 230, 180),
    'obstacles': [TrackPosition(141, 383, -2), TrackPosition(176, 397, 0),
                  TrackPosition(265, 590, 89), TrackPosition(300, 111, -26), TrackPosition(308, 577, 32),
                  TrackPosition(695, 561, 2),
                  TrackPosition(730, 560, 2)]
}
__venus_mod_3 = {
    'name': 'venus 3', 'outer_track_offset': 1470, 'inner_track_offset': 793,
    'single_car': TrackPosition(65, 270, 90),
    'obstacles': [TrackPosition(33, 548, 0), TrackPosition(95, 328, 0), TrackPosition(219, 345, 0),
                  TrackPosition(219, 290, 0), TrackPosition(430, 64, 0), TrackPosition(430, 100, 0),
                  TrackPosition(705, 485, 56), TrackPosition(721, 98, -2), TrackPosition(730, 254, 20),
                  TrackPosition(767, 534, 60)]
}

__earth_track = {
    'width': 1080, 'height': 800,
    'outer': [500, 229, 474, 226, 450, 216, 429, 200, 413, 179, 403, 155, 383, 107, 351, 66, 310, 34, 262, 14, 210,
              7, 158, 14, 110, 34, 69, 66, 37, 107, 17, 155, 10, 207, 17, 259, 37, 307, 69, 348, 110, 380, 158, 400,
              110, 420, 69, 452, 37, 493, 17, 541, 10, 593, 17, 645, 37, 693, 69, 734, 110, 766, 158, 786, 210, 793,
              262, 786, 310, 766, 351, 734, 383, 693, 403, 645, 413, 621, 429, 600, 450, 584, 474, 574, 500, 571, 526,
              574, 550, 584, 571, 600, 587, 621, 597, 645, 617, 693, 649, 734, 690, 766, 738, 786, 790, 793, 842, 786,
              890, 766, 931, 734, 963, 693, 983, 645, 990, 593, 983, 541, 963, 493, 931, 452, 890, 420, 842, 400, 890,
              380, 931, 348, 963, 307, 983, 259, 990, 207, 983, 155, 963, 107, 931, 66, 890, 34, 842, 14, 790, 7, 738,
              14, 690, 34, 649, 66, 617, 107, 597, 155, 587, 179, 571, 200, 550, 216, 526, 226, 500, 229],
    'inner': [500, 329, 448, 322, 400, 302, 359, 270, 327, 229, 307, 181, 297, 157, 281, 136, 260, 120, 236, 110, 210,
              107, 184, 110, 160, 120, 139, 136, 123, 157, 113, 181, 110, 207, 113, 233, 123, 257, 139, 278, 160, 294,
              184, 304, 205, 307, 228, 317, 248, 332, 263, 352, 273, 375, 276, 400, 276, 400, 273, 425, 263, 448, 248,
              468, 228, 483, 205, 493, 184, 496, 160, 506, 139, 522, 123, 543, 113, 567, 110, 593, 113, 619, 123, 643,
              139, 664, 160, 680, 184, 690, 210, 693, 236, 690, 260, 680, 281, 664, 297, 643, 307, 619, 327, 571, 359,
              530, 400, 498, 448, 478, 500, 471, 500, 471, 552, 478, 600, 498, 641, 530, 673,
              571, 693, 619, 703, 643, 719, 664, 740, 680, 764, 690, 790, 693, 816, 690, 840, 680, 861, 664, 877, 643,
              887, 619, 890, 593, 887, 567, 877, 543, 861, 522, 840, 506, 816, 496, 795, 493, 772, 483, 752, 468, 737,
              448, 727, 425, 724, 400, 724, 400, 727, 375, 737, 352, 752, 332, 772, 317, 795, 307, 816, 304, 840, 294,
              861, 278, 877, 257, 887, 233, 890, 207, 887, 181, 877, 157, 861, 136, 840, 120, 816, 110, 790, 107, 764,
              110, 740, 120, 719, 136, 703, 157, 693, 181, 673, 229, 641, 270, 600, 302, 552, 322, 500, 329],
    'two_cars': (TrackPosition(545, 291, 177), TrackPosition(540, 258, 178))
}
__earth_mod_1 = {
    'name': 'earth 1', 'outer_track_offset': 3833, 'inner_track_offset': 3245,
    'single_car': TrackPosition(540, 275, 180),
    'obstacles': [TrackPosition(76, 763, 53), TrackPosition(197, 129, 8), TrackPosition(264, 148, -43),
                  TrackPosition(538, 457, 82), TrackPosition(574, 467, 66)]
}
__earth_mod_2 = {
    'name': 'earth 2', 'outer_track_offset': 989, 'inner_track_offset': 984,
    'single_car': TrackPosition(155, 455, 210),
    'obstacles': [TrackPosition(76, 763, 53), TrackPosition(300, 138, -46),
                  TrackPosition(530, 560, -12), TrackPosition(825, 665, 27)]
}
__earth_mod_3 = {
    'name': 'earth 3', 'outer_track_offset': 2815, 'inner_track_offset': 2291,
    'single_car': TrackPosition(875, 485, 145),
    'obstacles': [TrackPosition(145, 683, -36), TrackPosition(272, 114, -32), TrackPosition(300, 138, -46),
                  TrackPosition(489, 557, 5), TrackPosition(530, 560, -12), TrackPosition(735, 127, 53),
                  TrackPosition(775, 112, -37), TrackPosition(868, 372, 22), TrackPosition(896, 356, 35)]
}


def __track_with(track, mod):
    return Level(
        name=mod['name'], width=track['width'], height=track['height'],
        inner_track=track['inner'],
        outer_track=track['outer'],
        outer_track_offset=mod['outer_track_offset'], inner_track_offset=mod['inner_track_offset'],
        single_car=mod['single_car'],
        two_cars=track['two_cars'],
        obstacles=mod['obstacles']
    )


Mercury_1 = __track_with(__mercury_track, __mercury_mod_1)
Mercury_2 = __track_with(__mercury_track, __mercury_mod_2)
Mercury_3 = __track_with(__mercury_track, __mercury_mod_3)

Venus_1 = __track_with(__venus_track, __venus_mod_1)
Venus_2 = __track_with(__venus_track, __venus_mod_2)
Venus_3 = __track_with(__venus_track, __venus_mod_3)

Earth_1 = __track_with(__earth_track, __earth_mod_1)
Earth_2 = __track_with(__earth_track, __earth_mod_2)
Earth_3 = __track_with(__earth_track, __earth_mod_3)

MANUAL_LEVELS = [Mercury_1, Venus_1, Earth_1, Mercury_2, Venus_2, Earth_2, Mercury_3, Venus_3, Earth_3]
EDIT_LEVEL = MANUAL_LEVELS[0]
DEMO_LEVEL = Mercury_1
SHOWCASE_FROM_FILE_LEVEL = Mercury_1


class Trainings:
    def __init__(self):
        self.__entries = [
            (Earth_1, 1500), (Mercury_1, 1500), (Venus_1, 1500),
            (Earth_2, 1500), (Mercury_2, 1500), (Venus_2, 1500),
            (Earth_3, 1500), (Mercury_3, 1500), (Venus_3, 1500)
        ]
        self.__ix = -1

    def has_next(self):
        return self.__ix < len(self.__entries)

    def reset(self):
        self.__ix = -1

    def next(self):
        self.__ix += 1
        return self.__entries[self.__ix]
