from typing import List

import pyglet

from .racer_engine import PlayerState
from .racer_graphics import CarGraphics, TrackGraphics, ScoreBox, GameOverlay, \
    WarmupSequence, Indicators, RankingBox
from .tracks import TRACK_SIZE

ENABLE_INDICATORS = False
SHOW_FPS = False


class RaceController:
    def __init__(self, show_warmup_screen=True):
        self.show_end_screen = False
        self.show_paused_screen = False
        self.__warmup_controller = WarmupController(show_warmup_screen)
        self.__reset_hook = None

    @property
    def warmup_controller(self):
        return self.__warmup_controller

    def reset(self):
        self.show_end_screen = False
        self.show_paused_screen = False
        self.__warmup_controller.reset()
        if self.__reset_hook:
            self.__reset_hook()

    def get_player_count(self):
        raise NotImplementedError()

    def on_key_press(self, symbol):
        pass

    def on_key_release(self, symbol):
        pass

    def focus_lost(self):
        pass

    def update_player_states(self, dt):
        raise NotImplementedError()

    def get_player_states(self) -> List[PlayerState]:
        raise NotImplementedError()

    def get_score_text(self):
        raise NotImplementedError()

    def get_ranking(self):
        pass

    def get_end_text(self):
        raise NotImplementedError()

    def set_reset_hook(self, reset_hook):
        self.__reset_hook = reset_hook


class WarmupController:
    RESET_DELAY = 0.5

    def __init__(self, show_warmup_screen):
        self.__default_warmup = show_warmup_screen
        self.show_warmup_screen = self.__default_warmup
        self.control_released = not self.__default_warmup
        self.warmup_screen = WarmupSequence()

    def reset(self):
        self.warmup_screen.reset()
        self.show_warmup_screen = self.__default_warmup
        self.control_released = not self.__default_warmup
        self.next_screen()

    def next_screen(self, _=None):
        if self.show_warmup_screen:
            self.show_warmup_screen = next(self.warmup_screen, False)
            if self.show_warmup_screen:
                self.control_released = self.warmup_screen.shows_last_screen()
                delay = self.warmup_screen.current_delay()
                pyglet.clock.schedule_once(self.next_screen, delay)


class RacerWindow(pyglet.window.Window):
    BG_COLOR = 0.5, 0.8, 0.4, 1
    WINDOW_POS = 20, 0

    def __init__(self, controller: RaceController, show_traces=True, show_fps=SHOW_FPS):
        super().__init__(*TRACK_SIZE, caption='Racer')
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glEnable(pyglet.gl.GL_LINE_SMOOTH)
        pyglet.gl.glClearColor(*self.BG_COLOR)
        self.set_location(*self.WINDOW_POS)
        self.controller = controller
        self.controller.set_reset_hook(self.on_reset)
        self.warmup_controller = controller.warmup_controller
        self.warmup_screen = self.warmup_controller.warmup_screen

        self.track = TrackGraphics()
        self.score_box = ScoreBox()

        car_count = self.controller.get_player_count()
        self.cars = [CarGraphics(car_count - ix, show_traces) for ix in range(car_count)]
        self.pause_overlay = GameOverlay('Paused', '"p" to continue...')
        self.end_overlay = None
        self.fps_display = pyglet.window.FPSDisplay(window=self) if show_fps else None
        self.indicator = Indicators() if ENABLE_INDICATORS else None
        self.ranking = RankingBox()

    def on_reset(self):
        self.end_overlay = None

    def start(self):
        pyglet.clock.schedule_interval(self.update, 1 / 120.0)
        self.warmup_controller.next_screen()
        pyglet.app.run()

    def on_draw(self):
        self.clear()
        self.track.draw()
        for stopped_car in filter(lambda car: car.show_dead_x, self.cars):
            stopped_car.draw()
        for active_car in filter(lambda car: not car.show_dead_x, self.cars):
            active_car.draw()

        if self.warmup_controller.show_warmup_screen:
            self.warmup_screen.draw()
        elif self.controller.show_end_screen:
            if not self.end_overlay:
                self.end_overlay = GameOverlay(*self.controller.get_end_text())
            self.end_overlay.draw()
        elif self.controller.show_paused_screen:
            self.pause_overlay.draw()

        self.score_box.draw()
        self.ranking.draw()
        if self.fps_display:
            self.fps_display.draw()
        if self.indicator:
            self.indicator.draw()

    def on_key_press(self, symbol, modifiers):
        super().on_key_press(symbol, modifiers)
        self.controller.on_key_press(symbol)

    def on_key_release(self, symbol, modifiers):
        self.controller.on_key_release(symbol)

    def on_deactivate(self):
        self.controller.focus_lost()

    def on_mouse_motion(self, x, y, dx, dy):
        if self.indicator:
            self.indicator.update_mouse(x, y)

    def update(self, dt):
        if self.warmup_controller.control_released:
            self.controller.update_player_states(dt)

        player_states = self.controller.get_player_states()
        for player_state, car in zip(player_states, self.cars):
            car.update(player_state)

        self.score_box.update_text(self.controller.get_score_text())
        self.ranking.update(self.controller.get_ranking())
        if self.indicator:
            self.indicator.update(player_states[-1])
