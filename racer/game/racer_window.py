import numpy as np
import pyglet
from pyglet.window import key

from racer_engine import RacerEngine, PlayerOperation, CAR_BOUNDS
from tracks import OUTER_TRACK, INNER_TRACK

TRACK_COLOR = (160, 10, 60)
CAR_COLOR = tuple(np.random.randint(0, 255, size=3))
CAR_BOUND_POINTS = (CAR_BOUNDS[0], CAR_BOUNDS[1], CAR_BOUNDS[2], CAR_BOUNDS[1],
                    CAR_BOUNDS[2], CAR_BOUNDS[3], CAR_BOUNDS[0], CAR_BOUNDS[3]
                    )

pyglet.resource.path = ['resources']
pyglet.resource.reindex()
car_frame_img = pyglet.resource.image("car-frame.png")
car_frame_img.anchor_x = car_frame_img.width * 2 / 5
car_frame_img.anchor_y = car_frame_img.height / 2


def create_line_graphics(points, color=TRACK_COLOR):
    pts_count = int(len(points) / 2)
    vertices = ('v2i', points)
    color_data = ('c3B', color * pts_count)
    return pyglet.graphics.vertex_list(pts_count, vertices, color_data)


class RacerWindow(pyglet.window.Window):
    def __init__(self, engine: RacerEngine):
        super().__init__(1000, 700, caption='Racer')
        pyglet.gl.glClearColor(0.5, 0.8, 0.4, 1)
        self.engine = engine
        self.batch = pyglet.graphics.Batch()
        self.score_label = pyglet.text.Label(x=10, y=self.height - 25, batch=self.batch)
        self.track_lines = [create_line_graphics(t) for t in (OUTER_TRACK, INNER_TRACK)]

        self.car_frame = pyglet.sprite.Sprite(img=car_frame_img, batch=self.batch)
        self.car_frame.scale = 0.5
        self.car_color = create_line_graphics(CAR_BOUND_POINTS, CAR_COLOR)
        self.player_operations = PlayerOperation()

    def on_draw(self):
        self.clear()
        pyglet.gl.glLineWidth(5)
        for track_line in self.track_lines:
            track_line.draw(pyglet.gl.GL_LINE_STRIP)

        self.draw_car_background()
        self.batch.draw()

    def draw_car_background(self):
        pyglet.gl.glLineWidth(1)
        pyglet.gl.glPushMatrix()

        pyglet.gl.glTranslatef(self.car_frame.x, self.car_frame.y, 0)
        pyglet.gl.glRotatef(-self.car_frame.rotation, 0, 0, 1.0)
        self.car_color.draw(pyglet.gl.GL_POLYGON)
        pyglet.gl.glPopMatrix()

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
        self.car_frame.update(x=pl.position[0], y=pl.position[1], rotation=pl.rotation)
        self.score_label.text = 'Score: {}'.format(self.engine.score)


if __name__ == '__main__':
    w = RacerWindow(RacerEngine())
    pyglet.clock.schedule_interval(w.update, 1 / 120.0)
    pyglet.app.run()