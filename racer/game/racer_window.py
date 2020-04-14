from os import path
from typing import List

import numpy as np
import pyglet

from .racer_engine import PlayerState, CAR_BOUND_POINTS
from .tracers import get_trace_points
from .tracks import OUTER_TRACK, INNER_TRACK, TRACK_SIZE

resource_dir = path.join(path.abspath(path.dirname(__file__)), 'resources')
pyglet.resource.path = [resource_dir]
pyglet.resource.reindex()
car_frame_img = pyglet.resource.image('car-frame.png')
car_frame_img.anchor_x = car_frame_img.width / 3
car_frame_img.anchor_y = car_frame_img.height / 2


class RaceController:
    def __init__(self, show_warmup_screen=True):
        self.show_lost_screen = False
        self.show_paused_screen = False
        self.__warmup_controller = WarmupController(show_warmup_screen)

    @property
    def warmup_controller(self):
        return self.__warmup_controller

    def reset(self):
        self.show_lost_screen = False
        self.show_paused_screen = False
        self.__warmup_controller.reset()

    def get_player_count(self):
        pass

    def on_key_press(self, symbol):
        pass

    def on_key_release(self, symbol):
        pass

    def focus_lost(self):
        pass

    def update_player_states(self, dt):
        pass

    def get_player_states(self) -> List[PlayerState]:
        pass

    def get_score_text(self):
        pass


class WarmupController:
    RESET_DELAY = 0.5

    def __init__(self, show_warmup_screen):
        self.__default_warmup = show_warmup_screen
        self.show_warmup_screen = show_warmup_screen
        self.control_released = False
        self.warmup_screen = WarmupSequence()

    def reset(self):
        self.warmup_screen.reset()
        self.show_warmup_screen = self.__default_warmup
        self.control_released = False
        self.next_screen()

    def next_screen(self, _=None):
        if self.show_warmup_screen:
            self.show_warmup_screen = next(self.warmup_screen, False)
            if self.show_warmup_screen:
                self.control_released = self.warmup_screen.shows_last_screen()
                delay = self.warmup_screen.current_delay()
                pyglet.clock.schedule_once(self.next_screen, delay)


class WarmupSequence:
    def __init__(self):
        self.__overlays = [(GameOverlay('3', ''), 1.0), (GameOverlay('2', ''), 1.0),
                           (GameOverlay('1', ''), 1.0), (GameOverlay('GO !!!', '', '', text_only=True), 0.7)]
        self.__current_ix = -1

    def reset(self):
        self.__current_ix = -1

    def __next__(self):
        self.__current_ix += 1
        return self.__is_current_ix_valid()

    def current_delay(self):
        return self.__overlays[self.__current_ix][1]

    def draw(self):
        if self.__is_current_ix_valid():
            self.__overlays[self.__current_ix][0].draw()

    def shows_last_screen(self):
        return self.__current_ix == len(self.__overlays) - 1

    def __is_current_ix_valid(self):
        return 0 <= self.__current_ix < len(self.__overlays)


class RacerWindow(pyglet.window.Window):
    BG_COLOR = 0.5, 0.8, 0.4, 1
    WINDOW_POS = 20, 0

    def __init__(self, controller: RaceController, show_traces=True):
        super().__init__(*TRACK_SIZE, caption='Racer')
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glClearColor(*self.BG_COLOR)
        self.set_location(*self.WINDOW_POS)
        self.controller = controller
        self.warmup_controller = controller.warmup_controller
        self.warmup_screen = self.warmup_controller.warmup_screen

        self.track = TrackGraphics()
        self.score_box = ScoreBox()
        self.cars = [CarGraphics(show_traces) for _ in range(self.controller.get_player_count())]
        self.pause_overlay = GameOverlay('Paused', '"p" to continue...')
        self.lost_overlay = GameOverlay('Lost!', '"n" New game')

    def start(self):
        pyglet.clock.schedule_interval(self.update, 1 / 120.0)
        self.warmup_controller.next_screen()
        pyglet.app.run()

    def on_draw(self):
        self.clear()
        self.track.draw()
        for car in self.cars:
            car.draw()
        if self.warmup_controller.show_warmup_screen:
            self.warmup_screen.draw()
        elif self.controller.show_lost_screen:
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
        if self.warmup_controller.control_released:
            self.controller.update_player_states(dt)
        player_states = self.controller.get_player_states()
        for player_state, car in zip(player_states, self.cars):
            car.update(player_state)
        self.score_box.update_text(self.controller.get_score_text())


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

    def update(self, player: PlayerState):
        self.car_frame.update(x=player.position[0], y=player.position[1], rotation=player.rotation)


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

    def __init__(self, main_txt, support_txt, exit_txt='"Esc" to quit', text_only=False):
        super().__init__()
        if not text_only:
            background = pyglet.graphics.OrderedGroup(0)
            cnt, vertices, transparent = convert_data(
                [0, 0, TRACK_SIZE[0], 0, TRACK_SIZE[0], TRACK_SIZE[1], 0, TRACK_SIZE[1]],
                self.BG_COLOR, color_mode='c4B')
            self.batch.add(4, pyglet.gl.GL_POLYGON, background, vertices, transparent)

        foreground = pyglet.graphics.OrderedGroup(1)
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

    def update_text(self, score_text):
        self.label.text = score_text
        self.label.x = self.center_x - self.label.content_width / 2


def convert_data(points, color=None, color_mode='c3B'):
    pts_count = int(len(points) / 2)
    vertices = ('v2i', points)
    color_data = (color_mode, color * pts_count) if color else None
    return pts_count, vertices, color_data


def add_points_to(batch, points, color, mode=pyglet.gl.GL_LINE_STRIP, group=None):
    pts_count, vertices, color_data = convert_data(points, color)
    batch.add(pts_count, mode, group, vertices, color_data)
