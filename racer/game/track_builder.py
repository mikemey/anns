import math

import numpy as np
import pyglet
from pyglet.window import key

from tracks import INNER_TRACK, OUTER_TRACK


def center_image(image):
    image.anchor_x = image.width / 2
    image.anchor_y = image.height / 2


pyglet.resource.path = ['resources']
pyglet.resource.reindex()
player_img = pyglet.resource.image("car-frame.png")
pointer_img = pyglet.resource.image("pointer.png")
center_image(player_img)
center_image(pointer_img)

TRACK_COLOR = 160, 10, 60
ACTIVE_TRACK_COLOR = 230, 50, 100
COORDS_COLOR = 100, 100, 100, 255


class TrackBuilderWindow(pyglet.window.Window):
    def __init__(self):
        super().__init__(1000, 700, caption='Track builder')
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glEnable(pyglet.gl.GL_LINE_SMOOTH)
        pyglet.gl.glClearColor(0.5, 0.8, 0.4, 1)
        self.batch = pyglet.graphics.Batch()
        self.player = pyglet.sprite.Sprite(img=player_img, batch=self.batch)
        self.player.scale = 0.5
        self.player.position = (100, 100)
        pyglet.text.Label('switch track:', x=830, y=670, batch=self.batch)
        pyglet.text.Label('\'Enter\'', x=940, y=670, batch=self.batch)
        pyglet.text.Label('switch mode:', x=830, y=650, batch=self.batch)
        pyglet.text.Label('\'a\'', x=940, y=650, batch=self.batch)
        pyglet.text.Label('print track:', x=830, y=630, batch=self.batch)
        pyglet.text.Label('\'p\'', x=940, y=630, batch=self.batch)

        self.track_point_highlighter = TrackPoint(batch=self.batch)
        pyglet.text.Label('Mouse:', x=860, y=600, multiline=True, width=50,
                          font_size=12, batch=self.batch)
        self.mouse_label = pyglet.text.Label('', x=930, y=600, multiline=True, width=50,
                                             font_name='Verdana', font_size=12,
                                             batch=self.batch, color=COORDS_COLOR)
        self.select_mode = True
        self.select_point_ix = -1
        self.closest_point = (0, 0)
        self.mouse = [0, 0]
        self.all_tracks = (OUTER_TRACK, INNER_TRACK)
        self.track_ix = 0
        self.track = self.all_tracks[self.track_ix]

    def on_draw(self):
        self.clear()
        pyglet.gl.glLineWidth(5)
        self.draw_track(0)
        self.draw_track(1)
        self.batch.draw()

    def draw_track(self, track_ix):
        pts = self.all_tracks[track_ix].copy()
        if not self.select_mode and self.track_ix == track_ix:
            pts.extend(self.mouse)
        pt_count = int(len(pts) / 2)
        color = ACTIVE_TRACK_COLOR if self.track_ix == track_ix else TRACK_COLOR
        pyglet.graphics.draw(pt_count, pyglet.gl.GL_LINE_STRIP,
                             ('v2i', pts), ('c3B', color * pt_count)
                             )

    def on_key_press(self, symbol, modifiers):
        super().on_key_press(symbol, modifiers)
        if symbol == key.A:
            self.select_mode = not self.select_mode
        elif symbol == key.P:
            print('Outer track:')
            print(self.all_tracks[0])
            print('Inner track:')
            print(self.all_tracks[1])
        elif symbol == key.ENTER:
            self.track_ix = 0 if self.track_ix == 1 else 1
            self.track = self.all_tracks[self.track_ix]

    def on_mouse_press(self, x, y, button, modifiers):
        if self.select_mode:
            self.select_point_ix = -1 if self.select_point_ix >= 0 \
                else self.get_closest_point_ix()
        else:
            self.track += [x, y]
        return True

    def on_mouse_motion(self, x, y, dx, dy):
        self.update_mouse(x, y)
        if self.select_point_ix >= 0:
            self.track[self.select_point_ix] = x
            self.track[self.select_point_ix + 1] = y

    def update_mouse(self, x, y):
        self.mouse = [x, y]
        self.mouse_label.text = coord_format(x, y)

    def update(self, dt):
        point_ix = self.get_closest_point_ix()
        px, py = self.track[point_ix], self.track[point_ix + 1]
        self.track_point_highlighter.update(px, py)

    def get_closest_point_ix(self):
        mouse = np.array(self.mouse)
        min_distance = math.inf
        closest_ix = -1
        for ix in range(0, len(self.track), 2):
            track_pt = (self.track[ix], self.track[ix + 1])
            dist = np.linalg.norm(mouse - track_pt)
            if dist < min_distance:
                min_distance = dist
                closest_ix = ix
        return closest_ix


class TrackPoint:
    def __init__(self, batch, font_size=8, offset=15):
        super().__init__()
        self.point = pyglet.sprite.Sprite(img=pointer_img, batch=batch)
        self.label = pyglet.text.Label('', font_size=font_size, batch=batch, font_name='Verdana',
                                       color=COORDS_COLOR, multiline=True, width=50)
        self.offset = offset

    def update(self, x, y):
        self.point.update(x=x, y=y)
        self.label.x = x + self.offset
        self.label.y = y + self.offset / 2
        self.label.text = coord_format(x, y)


def coord_format(x, y):
    return 'x={}\ny={}'.format(x, y)


if __name__ == '__main__':
    w = TrackBuilderWindow()
    pyglet.clock.schedule_interval(w.update, 1 / 120.0)
    pyglet.app.run()
