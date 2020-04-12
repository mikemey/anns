from os import path
from typing import Tuple, List

import numpy as np
import pyglet

from .racer_engine import CAR_BOUND_POINTS
from .tracks import OUTER_TRACK, INNER_TRACK, TRACK_SIZE, get_trace_points

resource_dir = path.join(path.abspath(path.dirname(__file__)), 'resources')
pyglet.resource.path = [resource_dir]
pyglet.resource.reindex()
car_frame_img = pyglet.resource.image('car-frame.png')
car_frame_img.anchor_x = car_frame_img.width / 3
car_frame_img.anchor_y = car_frame_img.height / 2


class RaceController:
    def __init__(self):
        self.show_lost_screen = False
        self.show_paused_screen = False

    def reset(self):
        self.show_lost_screen = False
        self.show_paused_screen = False

    def get_player_count(self):
        pass

    def on_key_press(self, symbol):
        pass

    def on_key_release(self, symbol):
        pass

    def focus_lost(self):
        pass

    def update_players(self, dt) -> List[Tuple[float, float, float]]:
        pass

    def get_score(self):
        pass


class RacerWindow(pyglet.window.Window):
    BG_COLOR = 0.5, 0.8, 0.4, 1
    WINDOW_POS = 20, 0

    def __init__(self, controller: RaceController):
        super().__init__(*TRACK_SIZE, caption='Racer')
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glClearColor(*self.BG_COLOR)
        self.set_location(*self.WINDOW_POS)
        self.controller = controller

        self.track = TrackGraphics()
        self.score_box = ScoreBox()
        self.cars = [CarGraphics() for _ in range(self.controller.get_player_count())]
        self.pause_overlay = GameOverlay('Paused', '"p" to continue...')
        self.lost_overlay = GameOverlay('Lost!', '"n" New game')

    def start(self):
        pyglet.clock.schedule_interval(self.update, 1 / 120.0)
        pyglet.app.run()

    def on_draw(self):
        self.clear()
        self.track.draw()
        for car in self.cars:
            car.draw()
        if self.controller.show_lost_screen:
            self.lost_overlay.draw()
        elif self.controller.show_paused_screen:
            self.pause_overlay.draw()
        self.score_box.draw()

    def on_key_press(self, symbol, modifiers):
        super().on_key_press(symbol, modifiers)
        self.controller.on_key_press(symbol)

    def on_key_release(self, symbol, modifiers):
        self.controller.on_key_release(symbol)

    def on_deactivate(self):
        self.controller.focus_lost()

    def update(self, dt):
        player_positions = self.controller.update_players(dt)
        for player_pos, car in zip(player_positions, self.cars):
            car.update(*player_pos)
        self.score_box.update_text(self.controller.get_score())


class GraphicsElement:
    def __init__(self):
        self.batch = pyglet.graphics.Batch()

    def draw(self):
        self.batch.draw()


def random_color():
    return tuple(np.random.randint(0, 255, size=3))


class CarGraphics(GraphicsElement):
    TRACE_COLOR = 100, 100, 255

    def __init__(self, show_traces=True):
        super().__init__()
        self.show_traces = show_traces
        self.car_frame = pyglet.sprite.Sprite(img=car_frame_img, batch=self.batch)
        self.car_frame.scale = 0.5
        pts, vertices, _ = convert_data(CAR_BOUND_POINTS)
        color_data = 'c3B', random_color() + random_color() + random_color() + random_color()
        self.car_color = pyglet.graphics.vertex_list(pts, vertices, vertices, color_data)

    def draw(self):
        if self.show_traces:
            self.draw_traces()
        pyglet.gl.glPushMatrix()
        pyglet.gl.glTranslatef(self.car_frame.x, self.car_frame.y, 0)
        pyglet.gl.glRotatef(-self.car_frame.rotation, 0, 0, 1.0)
        self.car_color.draw(pyglet.gl.GL_POLYGON)
        pyglet.gl.glPopMatrix()
        self.batch.draw()

    def draw_traces(self):
        pyglet.gl.glLineWidth(1)
        for pos in get_trace_points(self.car_frame.position, self.car_frame.rotation):
            pyglet.graphics.draw(2, pyglet.gl.GL_LINE_STRIP,
                                 ('v2f', self.car_frame.position + pos),
                                 ('c3B', self.TRACE_COLOR * 2)
                                 )

    def update(self, pos_x, pos_y, rot):
        self.car_frame.update(x=pos_x, y=pos_y, rotation=rot)


class TrackGraphics(GraphicsElement):
    TRACK_COLOR = 160, 10, 60

    def __init__(self):
        super().__init__()
        add_points_to(self.batch, OUTER_TRACK, self.TRACK_COLOR)
        add_points_to(self.batch, INNER_TRACK, self.TRACK_COLOR)

    def draw(self):
        pyglet.gl.glLineWidth(5)
        self.batch.draw()


class GameOverlay(GraphicsElement):
    BG_COLOR = 30, 30, 30, 150
    MAIN_COLOR = 255, 255, 0, 255
    SECOND_COLOR = 255, 255, 150, 255

    def __init__(self, main_txt, support_txt, exit_txt='"Esc" to quit'):
        super().__init__()
        background = pyglet.graphics.OrderedGroup(0)
        foreground = pyglet.graphics.OrderedGroup(1)

        cnt, vertices, transparent = convert_data(
            [0, 0, TRACK_SIZE[0], 0, TRACK_SIZE[0], TRACK_SIZE[1], 0, TRACK_SIZE[1]],
            self.BG_COLOR, color_mode='c4B')
        self.batch.add(4, pyglet.gl.GL_POLYGON, background, vertices, transparent)

        main_lbl = pyglet.text.Label(main_txt, batch=self.batch, group=foreground,
                                     color=self.MAIN_COLOR, font_size=22, bold=True)
        main_lbl.x = TRACK_SIZE[0] / 2 - main_lbl.content_width / 2
        main_lbl.y = TRACK_SIZE[1] / 2 - main_lbl.content_height / 2
        support_lbl = pyglet.text.Label(support_txt, batch=self.batch, group=foreground,
                                        color=self.SECOND_COLOR, font_size=16)
        support_lbl.x = TRACK_SIZE[0] / 2 - support_lbl.content_width / 2
        support_lbl.y = TRACK_SIZE[1] / 2 - main_lbl.content_height - support_lbl.content_height
        exit_lbl = pyglet.text.Label(exit_txt, batch=self.batch, group=foreground,
                                     color=self.SECOND_COLOR, font_size=16)
        exit_lbl.x = TRACK_SIZE[0] / 2 - exit_lbl.content_width / 2
        exit_lbl.y = TRACK_SIZE[1] / 2 - main_lbl.content_height - exit_lbl.content_height * 2.3


class ScoreBox(GraphicsElement):
    BG_COLOR = 50, 50, 200
    SCORE_BOX = 125, 40

    def __init__(self):
        super().__init__()
        offset = np.array(TRACK_SIZE) - self.SCORE_BOX
        box = np.append(offset, offset + self.SCORE_BOX)
        self.center_x = offset[0] + self.SCORE_BOX[0] / 2

        background = pyglet.graphics.OrderedGroup(0)
        foreground = pyglet.graphics.OrderedGroup(1)
        add_points_to(self.batch, [
            box[0], box[1], box[2], box[1], box[2], box[3], box[0], box[3], box[0], box[1]
        ], self.BG_COLOR, pyglet.gl.GL_POLYGON, background)
        self.label = pyglet.text.Label(x=TRACK_SIZE[0] - 100, y=TRACK_SIZE[1] - 25,
                                       batch=self.batch, group=foreground)

    def update_text(self, score):
        self.label.text = 'Score: {}'.format(score)
        self.label.x = self.center_x - self.label.content_width / 2


def convert_data(points, color=None, color_mode='c3B'):
    pts_count = int(len(points) / 2)
    vertices = ('v2i', points)
    color_data = (color_mode, color * pts_count) if color else None
    return pts_count, vertices, color_data


def add_points_to(batch, points, color, mode=pyglet.gl.GL_LINE_STRIP, group=None):
    pts_count, vertices, color_data = convert_data(points, color)
    batch.add(pts_count, mode, group, vertices, color_data)
