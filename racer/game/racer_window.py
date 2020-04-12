from os import path
from typing import Tuple

import numpy as np
import pyglet

from .racer_engine import CAR_BOUND_POINTS
from .tracks import OUTER_TRACK, INNER_TRACK, WINDOW_SIZE

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

    def interact(self):
        pass

    def on_key_press(self, symbol):
        pass

    def on_key_release(self, symbol):
        pass

    def focus_lost(self):
        pass

    def update_player(self, dt) -> Tuple[float, float, float]:
        pass

    def get_score(self):
        pass


class RacerWindow(pyglet.window.Window):
    BG_COLOR = 0.5, 0.8, 0.4, 1
    WINDOW_POS = 20, 0
    TRACK_COLOR = 160, 10, 60
    CAR_COLOR = tuple(np.random.randint(0, 255, size=3))

    def __init__(self, controller: RaceController):
        super().__init__(*WINDOW_SIZE, caption='Racer')
        self.controller = controller
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        self.set_location(*self.WINDOW_POS)
        pyglet.gl.glClearColor(*self.BG_COLOR)
        self.batch = pyglet.graphics.Batch()
        add_points_to(self.batch, OUTER_TRACK, self.TRACK_COLOR)
        add_points_to(self.batch, INNER_TRACK, self.TRACK_COLOR)

        self.score_box = ScoreBox(self.batch)
        self.car_frame = pyglet.sprite.Sprite(img=car_frame_img, batch=self.batch)
        self.car_frame.scale = 0.5
        self.car_color = create_vertex_list(CAR_BOUND_POINTS, self.CAR_COLOR)
        self.pause_overlay = GameOverlay('Paused', '"p" to continue...')
        self.lost_overlay = GameOverlay('Lost!', '')

    def start(self):
        pyglet.clock.schedule_interval(self.update, 1 / 120.0)
        pyglet.app.run()

    def on_draw(self):
        self.clear()
        self.draw_car_background()
        pyglet.gl.glLineWidth(5)
        self.batch.draw()
        if self.controller.show_lost_screen:
            self.lost_overlay.draw()
        elif self.controller.show_paused_screen:
            self.pause_overlay.draw()

    def draw_car_background(self):
        pyglet.gl.glPushMatrix()
        pyglet.gl.glTranslatef(self.car_frame.x, self.car_frame.y, 0)
        pyglet.gl.glRotatef(-self.car_frame.rotation, 0, 0, 1.0)
        self.car_color.draw(pyglet.gl.GL_POLYGON)
        pyglet.gl.glPopMatrix()

        pyglet.gl.glLineWidth(1)
        rot = math.radians(self.car_frame.rotation)
        for pos in find_nearest_points(self.car_frame.position, rot):
            pyglet.graphics.draw(2, pyglet.gl.GL_LINE_STRIP,
                                 ('v2f', self.car_frame.position + pos),
                                 ('c3B', (100, 100, 255) * 2)
                                 )

    def on_key_press(self, symbol, modifiers):
        super().on_key_press(symbol, modifiers)
        self.controller.on_key_press(symbol)

    def on_key_release(self, symbol, modifiers):
        self.controller.on_key_release(symbol)

    def on_deactivate(self):
        self.controller.focus_lost()

    def update(self, dt):
        player_pos = self.controller.update_player(dt)
        if player_pos:
            pos_x, pos_y, rot = player_pos
            self.car_frame.update(x=pos_x, y=pos_y, rotation=rot)
            self.score_box.update_text(self.controller.get_score())


class GameOverlay:
    BG_COLOR = 30, 30, 30, 150
    MAIN_COLOR = 255, 255, 0, 255
    SECOND_COLOR = 255, 255, 150, 255

    def __init__(self, main_txt, support_txt, exit_txt='"Esc" to quit'):
        self.overlay = pyglet.graphics.Batch()
        background = pyglet.graphics.OrderedGroup(0)
        foreground = pyglet.graphics.OrderedGroup(1)

        size = WINDOW_SIZE
        cnt, vertices, transparent = convert_data(
            [0, 0, size[0], 0, size[0], size[1], 0, size[1]],
            self.BG_COLOR, color_mode='c4B')
        self.overlay.add(4, pyglet.gl.GL_POLYGON, background, vertices, transparent)

        main_lbl = pyglet.text.Label(main_txt, batch=self.overlay, group=foreground,
                                     color=self.MAIN_COLOR, font_size=22, bold=True)
        main_lbl.x = size[0] / 2 - main_lbl.content_width / 2
        main_lbl.y = size[1] / 2 - main_lbl.content_height / 2
        support_lbl = pyglet.text.Label(support_txt, batch=self.overlay, group=foreground,
                                        color=self.SECOND_COLOR, font_size=16)
        support_lbl.x = size[0] / 2 - support_lbl.content_width / 2
        support_lbl.y = size[1] / 2 - main_lbl.content_height - support_lbl.content_height
        exit_lbl = pyglet.text.Label(exit_txt, batch=self.overlay, group=foreground,
                                     color=self.SECOND_COLOR, font_size=16)
        exit_lbl.x = size[0] / 2 - exit_lbl.content_width / 2
        exit_lbl.y = size[1] / 2 - main_lbl.content_height - exit_lbl.content_height * 2.3

    def draw(self):
        self.overlay.draw()


class ScoreBox:
    BG_COLOR = 50, 50, 200
    SCORE_BOX = 125, 40

    def __init__(self, batch):
        offset = np.array(WINDOW_SIZE) - self.SCORE_BOX
        box = np.append(offset, offset + self.SCORE_BOX)
        self.center_x = offset[0] + self.SCORE_BOX[0] / 2

        background = pyglet.graphics.OrderedGroup(0)
        foreground = pyglet.graphics.OrderedGroup(1)
        add_points_to(batch, [
            box[0], box[1], box[2], box[1], box[2], box[3], box[0], box[3], box[0], box[1]
        ], self.BG_COLOR, pyglet.gl.GL_POLYGON, background)
        self.label = pyglet.text.Label(x=WINDOW_SIZE[0] - 100, y=WINDOW_SIZE[1] - 25, batch=batch, group=foreground)

    def update_text(self, score):
        self.label.text = 'Score: {}'.format(score)
        self.label.x = self.center_x - self.label.content_width / 2


def convert_data(points, color, color_mode='c3B'):
    pts_count = int(len(points) / 2)
    vertices = ('v2i', points)
    color_data = (color_mode, color * pts_count)
    return pts_count, vertices, color_data


def create_vertex_list(points, color):
    return pyglet.graphics.vertex_list(*convert_data(points, color))


def add_points_to(batch, points, color, mode=pyglet.gl.GL_LINE_STRIP, group=None):
    pts_count, vertices, color_data = convert_data(points, color)
    batch.add(pts_count, mode, group, vertices, color_data)


import math
import shapely
from shapely.geometry import LineString

INNER_LINE = LineString(np.reshape(INNER_TRACK, (-1, 2)))
OUTER_LINE = LineString(np.reshape(OUTER_TRACK, (-1, 2)))

TRACE_LEN = WINDOW_SIZE[0]
DEG_20 = math.pi / 9
DEG_40 = math.pi / 9 * 2
DEG_65 = math.pi / 36 * 13
DEG_90 = math.pi / 2


def find_nearest_points(pos, rot):
    return [
        closest_on_line(pos, rot),
        closest_on_line(pos, rot + DEG_20),
        closest_on_line(pos, rot - DEG_20),
        closest_on_line(pos, rot + DEG_40),
        closest_on_line(pos, rot - DEG_40),
        closest_on_line(pos, rot + DEG_65),
        closest_on_line(pos, rot - DEG_65),
        closest_on_line(pos, rot + DEG_90),
        closest_on_line(pos, rot - DEG_90)
    ]


def closest_on_line(pos, rot):
    trace_target = (pos[0] + math.cos(rot) * TRACE_LEN, pos[1] - math.sin(rot) * TRACE_LEN)
    tracer = LineString([pos, trace_target])
    candidates = INNER_LINE.intersection(tracer).union(OUTER_LINE.intersection(tracer))
    cross_pts = []
    if not candidates.is_empty:
        if isinstance(candidates, shapely.geometry.MultiPoint):
            for pts in candidates.geoms:
                cross_pts.append((pts.x, pts.y))
        else:
            cross_pts.append((candidates.x, candidates.y))

    np_cross_pts = np.array(cross_pts)
    if len(np_cross_pts) == 0:
        return []
    sq_distances = np.sum((np_cross_pts - pos) ** 2, axis=1)
    return cross_pts[np.argmin(sq_distances)]
