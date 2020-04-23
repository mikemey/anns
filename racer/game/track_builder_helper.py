import math
import numpy as np

x_offset = 180
y_offset = 400
# radius = 200
# radius = 100
radius = 96

QU_TOP_RIGHT = 0
QU_TOP_LEFT = 1
QU_BOTTOM_LEFT = 2
QU_BOTTOM_RIGHT = 3

# circle generation
quadrants = [[], [], [], []]
for i in range(0, 91, 15):
    rad = math.radians(i)
    x, y = round(math.cos(rad) * radius), round(math.sin(rad) * radius)

    quadrants[QU_TOP_RIGHT].append([x + x_offset, y + y_offset])
    quadrants[QU_TOP_LEFT].append([-x + x_offset, y + y_offset])
    quadrants[QU_BOTTOM_LEFT].append([-x + x_offset, -y + y_offset])
    quadrants[QU_BOTTOM_RIGHT].append([x + x_offset, -y + y_offset])
    # quadrants[QU_TOP_RIGHT].extend([x, y])
    # quadrants[QU_TOP_LEFT].extend([-x, y])
    # quadrants[QU_BOTTOM_LEFT].extend([-x, -y])
    # quadrants[QU_BOTTOM_RIGHT].extend([x, -y])

# coll = [*quadrants[QU_TOP_RIGHT], *reversed(quadrants[QU_TOP_LEFT])]
# coll = [*quadrants[QU_BOTTOM_RIGHT], *reversed(quadrants[QU_BOTTOM_LEFT]), *quadrants[QU_TOP_LEFT]]
# coll = [*reversed(quadrants[QU_BOTTOM_LEFT]), *quadrants[QU_TOP_LEFT], *reversed(quadrants[QU_TOP_RIGHT])]
# coll = [*quadrants[QU_BOTTOM_LEFT], *reversed(quadrants[QU_BOTTOM_RIGHT])]
coll = [*reversed(quadrants[QU_BOTTOM_RIGHT]), *quadrants[QU_TOP_RIGHT]]
# print([el for pt in coll for el in pt])


# move points
move_line = [700, 125, 693, 177, 673, 225, 641, 266, 600, 298, 552, 318, 500, 325, 500, 325, 448, 318, 400, 298,
             359, 266, 327, 225, 307, 177, 297, 153, 281, 132, 260, 116, 236, 106, 210, 103, 210, 103, 184, 106,
             160, 116, 139, 132, 123, 153, 113, 177, 110, 203, 110, 203, 113, 229, 123, 253, 139, 274, 160, 290,
             184, 300, 210, 303]
# print([c if (ix % 2) == 0 else c + 4 for ix, c in enumerate(move_line)])


# mirror points
outline = [500, 329, 448, 322, 400, 302, 359, 270, 327, 229, 307, 181, 297, 157, 281, 136, 260, 120, 236, 110, 210,
           107, 184, 110, 160, 120, 139, 136, 123, 157, 113, 181, 110, 207, 113, 233, 123, 257, 139, 278, 160, 294,
           184, 304,
           205, 307, 228, 317, 248, 332, 263, 352, 273, 375, 276, 400, 276, 400, 273, 425, 263, 448, 248, 468, 228, 483, 205, 493,
           184, 496, 160, 506, 139, 522, 123, 543, 113, 567,
           110, 593, 113, 619, 123, 643, 139, 664, 160, 680, 184, 690, 210, 693, 236, 690, 260, 680, 281, 664, 297,
           643, 307, 619, 327, 571, 359, 530, 400, 498, 448, 478, 500, 471, 9999, 9999]
for pt in reversed(np.reshape(outline, (-1, 2))):
    x, y = pt
    mx = (500 - x) + 500
    # my = (400 - y) + 400
    outline.append(mx)
    outline.append(y)
print(outline)
