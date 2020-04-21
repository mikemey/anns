import math

import numpy as np
import pyglet
from pyglet.window import key

from .racer_graphics import pointer_img, box_img
from .tracks import Level, TrackPosition

TRACK_COLOR = 160, 10, 60
ACTIVE_TRACK_COLOR = 230, 50, 100
COORDS_COLOR = 100, 100, 100, 255


def coord_format(x, y):
    return 'x={:.0f}\ny={:.0f}'.format(x, y)


class EditState:
    def __init__(self, level: Level):
        self.all_tracks = (level.outer_track, level.inner_track)
        self.track_ix = 0
        self.track = self.all_tracks[self.track_ix]
        self.mouse = [0, 0]
        self.obstacles = level.obstacles

    def coords(self, ix):
        return self.track[ix], self.track[ix + 1]


class EditMode:
    def __init__(self, state: EditState):
        self.state = state

    def name(self):
        raise NotImplementedError()

    def set_visible(self, visible):
        pass

    def switch_track(self):
        self.state.track_ix = 0 if self.state.track_ix == 1 else 1
        self.state.track = self.state.all_tracks[self.state.track_ix]

    def on_key_press(self, symbol):
        pass

    def on_key_release(self, symbol):
        pass

    def on_mouse_motion(self, x, y):
        self.state.mouse = [x, y]

    def on_mouse_press(self, x, y):
        pass

    def draw(self):
        self.__draw_track(0)
        self.__draw_track(1)

    def __draw_track(self, track_ix):
        pts = self.get_track_points(track_ix)
        pt_count = int(len(pts) / 2)
        color = ACTIVE_TRACK_COLOR if self.state.track_ix == track_ix else TRACK_COLOR
        line_width = 5 if self.state.track_ix == track_ix else 3
        pyglet.gl.glLineWidth(line_width)
        pyglet.graphics.draw(pt_count, pyglet.gl.GL_LINE_STRIP,
                             ('v2i', pts), ('c3B', color * pt_count)
                             )

    def get_track_points(self, track_ix):
        return self.state.all_tracks[track_ix]

    def closest_track_point_ix_to_mouse(self):
        mouse = np.array(self.state.mouse)
        min_distance = math.inf
        closest_ix = -1
        for ix in range(0, len(self.state.track), 2):
            track_pt = (self.state.track[ix], self.state.track[ix + 1])
            dist = np.linalg.norm(mouse - track_pt)
            if dist < min_distance:
                min_distance = dist
                closest_ix = ix
        return closest_ix

    def update(self):
        pass


class AddPointMode(EditMode):
    def __init__(self, state):
        super().__init__(state)

    def name(self):
        return 'ADD pt'

    def on_mouse_press(self, x, y):
        self.state.track += [x, y]

    def get_track_points(self, track_ix):
        pts = self.state.all_tracks[track_ix].copy()
        if self.state.track_ix == track_ix:
            pts.extend(self.state.mouse)
        return pts


class EditPointsMode(EditMode):
    def __init__(self, state, batch):
        super().__init__(state)
        self.track_point = TrackPoint(batch=batch)
        self.set_visible(False)
        self.select_point_ix = -1

    def name(self):
        return 'EDIT pt'

    def set_visible(self, visible):
        self.track_point.set_visible(visible)

    def on_mouse_press(self, x, y):
        self.select_point_ix = -1 if self.select_point_ix >= 0 \
            else self.closest_track_point_ix_to_mouse()

    def on_mouse_motion(self, x, y):
        super().on_mouse_motion(x, y)
        if self.select_point_ix >= 0:
            self.state.track[self.select_point_ix] = x
            self.state.track[self.select_point_ix + 1] = y

    def update(self):
        px, py = self.state.coords(self.closest_track_point_ix_to_mouse())
        self.track_point.update(px, py)


class InsertPointMode(EditMode):
    def __init__(self, state, batch):
        super().__init__(state)
        self.track_points = [TrackPoint(batch=batch, show_xy=False), TrackPoint(batch=batch, show_xy=False)]
        self.set_visible(False)
        self.insert_ix = -1

    def name(self):
        return 'INSERT pt'

    def set_visible(self, visible):
        for pt in self.track_points:
            pt.set_visible(visible)

    def on_mouse_press(self, x, y):
        self.insert_ix = -1 if self.insert_ix >= 0 \
            else self.closest_track_point_ix_to_mouse() + 2

        if self.insert_ix >= 0:
            self.state.track.insert(self.insert_ix, self.state.mouse[1])
            self.state.track.insert(self.insert_ix, self.state.mouse[0])

    def on_mouse_motion(self, x, y):
        super().on_mouse_motion(x, y)
        if self.insert_ix >= 0:
            self.state.track[self.insert_ix] = x
            self.state.track[self.insert_ix + 1] = y

    def update(self):
        if self.insert_ix < 0:
            ix = self.closest_track_point_ix_to_mouse()
            self.track_points[0].update(*self.state.coords(ix))

            second_ix = ix + 2
            if second_ix >= len(self.state.track):
                second_ix = ix - 2
            self.track_points[1].update(*self.state.coords(second_ix))


class AddObstaclesMode(EditMode):
    def __init__(self, state, batch):
        super().__init__(state)
        self.batch = batch
        self.sprites = []
        self.mouse_sprite = pyglet.sprite.Sprite(img=box_img, batch=self.batch)
        self.mouse_sprite.update(scale=0.4)
        self.box_rotation = 0
        for obstacle in state.obstacles:
            self.__add_box_sprite(obstacle.x, obstacle.y, obstacle.rot, False)
        self.set_visible(False)

    def name(self):
        return 'ADD box'

    def set_visible(self, visible):
        self.mouse_sprite.visible = visible
        self.mouse_sprite.update(x=self.state.mouse[0], y=self.state.mouse[1])

    def __add_box_sprite(self, x, y, rot, add_to_obstacles=True):
        box = pyglet.sprite.Sprite(img=box_img, batch=self.batch)
        box.update(x=x, y=y, rotation=rot, scale=0.4)
        self.sprites.append(box)
        if add_to_obstacles:
            self.state.obstacles.append(TrackPosition(x, y, rot))

    def on_mouse_motion(self, x, y):
        self.mouse_sprite.update(x=x, y=y)

    def on_mouse_press(self, x, y):
        self.__add_box_sprite(x, y, self.mouse_sprite.rotation)

    def on_key_press(self, symbol):
        if symbol == key.C:
            self.box_rotation = -0.5
        if symbol == key.V:
            self.box_rotation = 0.5

    def on_key_release(self, symbol):
        if symbol == key.C or symbol == key.V:
            self.box_rotation = 0

    def update(self):
        if self.box_rotation:
            self.mouse_sprite.rotation += self.box_rotation


class TrackPoint:
    def __init__(self, batch, font_size=8, offset=15, show_xy=True):
        super().__init__()
        self.point = pyglet.sprite.Sprite(img=pointer_img, batch=batch)
        self.label = pyglet.text.Label('', font_size=font_size, batch=batch, font_name='Verdana',
                                       color=COORDS_COLOR, multiline=True, width=50) \
            if show_xy else None
        self.offset = offset

    def set_visible(self, visible):
        self.point.visible = visible
        if self.label:
            self.label.text = ''

    def update(self, x, y):
        self.point.update(x=x, y=y)
        if self.label:
            self.label.x = x + self.offset
            self.label.y = y + self.offset / 2
            self.label.text = coord_format(x, y)
