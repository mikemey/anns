import numpy as np
import pyglet
from pyglet.window import key

from racer_engine import RacerEngine, PlayerOperation, CAR_BOUND_POINTS
from tracks import OUTER_TRACK, INNER_TRACK, WINDOW_SIZE

TRACK_COLOR = 160, 10, 60
CAR_COLOR = tuple(np.random.randint(0, 255, size=3))
WINDOW_POS = 20, 0

pyglet.resource.path = ['resources']
pyglet.resource.reindex()
car_frame_img = pyglet.resource.image("car-frame.png")
car_frame_img.anchor_x = car_frame_img.width * 2 / 5
car_frame_img.anchor_y = car_frame_img.height / 2


def convert_data(points, color):
    pts_count = int(len(points) / 2)
    vertices = ('v2i', points)
    color_data = ('c3B', color * pts_count)
    return pts_count, vertices, color_data


def create_vertex_list(points, color):
    return pyglet.graphics.vertex_list(*convert_data(points, color))


def add_points_to(batch, points, color):
    pts_count, vertices, color_data = convert_data(points, color)
    batch.add(pts_count, pyglet.gl.GL_LINE_STRIP, None, vertices, color_data)


class RacerWindow(pyglet.window.Window):
    def __init__(self, engine: RacerEngine):
        super().__init__(*WINDOW_SIZE, caption='Racer')
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        self.set_location(*WINDOW_POS)
        pyglet.gl.glClearColor(0.5, 0.8, 0.4, 1)
        self.engine = engine
        self.batch = pyglet.graphics.Batch()
        self.score_label = pyglet.text.Label(x=self.width - 100, y=self.height - 25, batch=self.batch)
        add_points_to(self.batch, OUTER_TRACK, TRACK_COLOR)
        add_points_to(self.batch, INNER_TRACK, TRACK_COLOR)
        self.car_frame = pyglet.sprite.Sprite(img=car_frame_img, batch=self.batch)
        self.car_frame.scale = 0.5
        self.car_color = create_vertex_list(CAR_BOUND_POINTS, CAR_COLOR)
        self.pause_overlay = PauseOverlay()

        self.player_operations = PlayerOperation()
        self.game_state = GameState()

    def on_draw(self):
        self.clear()
        self.draw_car_background()
        pyglet.gl.glLineWidth(5)
        self.batch.draw()
        if self.game_state.is_paused:
            self.pause_overlay.draw()

    def draw_car_background(self):
        pyglet.gl.glPushMatrix()

        pyglet.gl.glTranslatef(self.car_frame.x, self.car_frame.y, 0)
        pyglet.gl.glRotatef(-self.car_frame.rotation, 0, 0, 1.0)
        self.car_color.draw(pyglet.gl.GL_POLYGON)
        pyglet.gl.glPopMatrix()

    def on_key_press(self, symbol, modifiers):
        super().on_key_press(symbol, modifiers)
        if symbol == key.UP:
            self.player_operations.accelerate()
        if symbol == key.DOWN:
            self.player_operations.reverse()
        if symbol == key.LEFT:
            self.player_operations.turn_left()
        if symbol == key.RIGHT:
            self.player_operations.turn_right()

    def on_key_release(self, symbol, modifiers):
        if symbol in (key.UP, key.DOWN):
            self.player_operations.stop_direction()
        if symbol == key.LEFT:
            self.player_operations.stop_left()
        if symbol == key.RIGHT:
            self.player_operations.stop_right()
        if symbol == key.P:
            self.game_state.is_paused = not self.game_state.is_paused

    def on_deactivate(self):
        self.game_state.is_paused = True

    def update(self, dt):
        if self.game_state.is_paused:
            return
        self.engine.update(dt, self.player_operations)
        pl = self.engine.player
        self.car_frame.update(x=pl.position[0], y=pl.position[1], rotation=pl.rotation)
        self.score_label.text = 'Score: {}'.format(self.engine.score)


class PauseOverlay:
    def __init__(self):
        self.overlay = pyglet.graphics.Batch()
        size = WINDOW_SIZE
        cnt, vertices, color = convert_data(
            [0, 0, size[0], 0, size[0], size[1], 0, size[1]],
            (30, 30, 30, 150))
        transparent = ('c4B', color[1])
        self.overlay.add(4, pyglet.gl.GL_POLYGON, None, vertices, transparent)

        self.pause_lbl = pyglet.text.Label('Paused',
                                           color=(255, 255, 0, 255), font_size=22, bold=True)
        self.pause_lbl.x = size[0] / 2 - self.pause_lbl.content_width / 2
        self.pause_lbl.y = size[1] / 2 - self.pause_lbl.content_height / 2
        self.continue_lbl = pyglet.text.Label('press "P" to continue...',
                                              color=(255, 255, 150, 255), font_size=16)
        self.continue_lbl.x = size[0] / 2 - self.continue_lbl.content_width / 2
        self.continue_lbl.y = size[1] / 2 - self.pause_lbl.content_height - self.continue_lbl.content_height

    def draw(self):
        self.overlay.draw()
        self.pause_lbl.draw()
        self.continue_lbl.draw()


class GameState:
    def __init__(self):
        self.is_paused = False


if __name__ == '__main__':
    w = RacerWindow(RacerEngine())
    pyglet.clock.schedule_interval(w.update, 1 / 120.0)
    pyglet.app.run()
