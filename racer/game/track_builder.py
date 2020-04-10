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

INNER_COLOR = (160, 20, 180)
OUTER_COLOR = (210, 120, 30)


class TrackBuilderWindow(pyglet.window.Window):
    def __init__(self):
        super().__init__(1000, 700, caption='Track builder')
        pyglet.gl.glClearColor(0.5, 0.8, 0.4, 1)
        self.batch = pyglet.graphics.Batch()
        self.player = pyglet.sprite.Sprite(img=player_img, batch=self.batch)
        self.player.scale = 0.5
        self.player.position = (100, 100)

        self.select_mode = True
        self.select_point_ix = -1
        self.closest_point = (0, 0)
        self.pointer = pyglet.sprite.Sprite(img=pointer_img, batch=self.batch)
        self.mouse = [0, 0]
        self.all_tracks = (OUTER_TRACK, INNER_TRACK)
        self.track_ix = 0
        self.track = self.all_tracks[self.track_ix]

    def on_draw(self):
        self.clear()
        pyglet.gl.glLineWidth(4)
        self.draw_track(0, OUTER_COLOR)
        self.draw_track(1, INNER_COLOR)
        self.batch.draw()

    def draw_track(self, track_ix, color):
        pts = self.all_tracks[track_ix].copy()
        if not self.select_mode and self.track_ix == track_ix:
            pts.extend(self.mouse)
        pt_count = int(len(pts) / 2)
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
        self.mouse = [x, y]
        if self.select_point_ix >= 0:
            self.track[self.select_point_ix] = x
            self.track[self.select_point_ix + 1] = y

    def update(self, dt):
        point_ix = self.get_closest_point_ix()
        self.pointer.position = (self.track[point_ix], self.track[point_ix + 1])

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


if __name__ == '__main__':
    w = TrackBuilderWindow()
    pyglet.clock.schedule_interval(w.update, 1 / 120.0)
    pyglet.app.run()
