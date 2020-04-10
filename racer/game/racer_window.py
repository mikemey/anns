import math

import matplotlib.path as mpath
import numpy as np
import pyglet
from pyglet.window import key

from tracks import OUTER_TRACK, INNER_TRACK


def center_image(image):
    image.anchor_x = image.width / 2
    image.anchor_y = image.height / 2


pyglet.resource.path = ['resources']
pyglet.resource.reindex()
player_img = pyglet.resource.image("car-frame.png")
player_img.anchor_x = player_img.width * 2 / 5
player_img.anchor_y = player_img.height / 2
# center_image(player_img)

car_size = (48, 48)

TRACK_COLOR = (160, 10, 60)


class Track:
    def __init__(self):
        self.inside = mpath.Path(np.array([50, 50, ]))
        self.outside = mpath.Path(np.array([50, 50, ]))
        self.inside.contains_point((200, 100))


MAX_CAR_SPEED = 100
MAX_CAR_ROTATION = 100
SPEED_REDUCE = 1


class PlayerOperation:
    def __init__(self):
        self.accelerate = False
        self.left_turn = False
        self.right_turn = False


class Player:
    def __init__(self):
        self.position = [450, 320]
        self.rotation = 160
        self.speed = MAX_CAR_SPEED

    def update(self, dt, operations):
        if operations.accelerate:
            if operations.left_turn:
                self.rotation -= MAX_CAR_ROTATION * dt
            if operations.right_turn:
                self.rotation += MAX_CAR_ROTATION * dt
            rot = math.radians(self.rotation)
            self.position[0] += math.cos(rot) * self.speed * dt
            self.position[1] -= math.sin(rot) * self.speed * dt


class RacerEngine:
    def __init__(self):
        self.player = Player()
        self.score = 0

    def update(self, dt, operations):
        self.player.update(dt, operations)
        # self.player.rotation -= dt * 20


def create_track_line_graphics(track_line):
    pts_count = int(len(track_line) / 2)
    vertices = ('v2i', track_line)
    colors = ('c3B', TRACK_COLOR * pts_count)
    return pyglet.graphics.vertex_list(pts_count, colors, vertices)


class RacerWindow(pyglet.window.Window):
    def __init__(self, engine: RacerEngine):
        super().__init__(1000, 700, caption='Racer')
        pyglet.gl.glClearColor(0.5, 0.8, 0.4, 1)
        self.engine = engine
        self.batch = pyglet.graphics.Batch()
        self.score_label = pyglet.text.Label(x=10, y=self.height - 25, batch=self.batch)
        self.player = pyglet.sprite.Sprite(img=player_img, batch=self.batch)
        self.player.scale = 0.5
        self.player_operations = PlayerOperation()

        self.track_lines = [
            create_track_line_graphics(OUTER_TRACK),
            create_track_line_graphics(INNER_TRACK)
        ]

    def on_draw(self):
        self.clear()
        pyglet.gl.glLineWidth(5)
        for track_line in self.track_lines:
            track_line.draw(pyglet.gl.GL_LINE_STRIP)

        pyglet.gl.glLineWidth(1)
        pyglet.graphics.draw(3, pyglet.gl.GL_LINE_STRIP,
                             ('v2f', [0, 0] + self.engine.player.position + [20, 0])
                             )
        self.batch.draw()

    def on_key_press(self, symbol, modifiers):
        super().on_key_press(symbol, modifiers)
        if symbol == key.UP:
            self.player_operations.accelerate = True
        if symbol == key.LEFT:
            self.player_operations.left_turn = True
        if symbol == key.RIGHT:
            self.player_operations.right_turn = True

    def on_key_release(self, symbol, modifiers):
        if symbol == key.UP:
            self.player_operations.accelerate = False
        if symbol == key.LEFT:
            self.player_operations.left_turn = False
        if symbol == key.RIGHT:
            self.player_operations.right_turn = False

    def update(self, dt):
        self.engine.update(dt, self.player_operations)
        pl = self.engine.player
        self.player.update(x=pl.position[0], y=pl.position[1], rotation=pl.rotation)
        self.score_label.text = 'Score: {}'.format(self.engine.score)


if __name__ == '__main__':
    w = RacerWindow(RacerEngine())
    pyglet.clock.schedule_interval(w.update, 1 / 120.0)
    pyglet.app.run()
