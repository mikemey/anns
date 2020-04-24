from typing import List

import pyglet

from .racer_engine import PlayerState
from .racer_graphics import CarGraphics, TrackGraphics, ScoreBox, GameOverlay, \
    WarmupSequence, Indicators, RankingBox
from .tracks import Level

DEFAULT_WARMUP_SCREEN = True
DEFAULT_SHOW_TRACES = False
DEFAULT_SHOW_FPS = False
ENABLE_INDICATORS = False


class RaceController:
    def __init__(self, level: Level):
        self.level = level
        self.show_end_screen = False
        self.show_paused_screen = False
        self.__reset_hook = None

    def reset(self):
        self.show_end_screen = False
        self.show_paused_screen = False
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


class RacerWindow(pyglet.window.Window):
    BG_COLOR = 0.5, 0.8, 0.4, 1
    WINDOW_POS = 20, 0

    def __init__(self, controller: RaceController,
                 show_warmup_screen=DEFAULT_WARMUP_SCREEN,
                 show_traces=DEFAULT_SHOW_TRACES,
                 show_fps=DEFAULT_SHOW_FPS):
        super().__init__(controller.level.width, controller.level.height, caption='Racer')
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glEnable(pyglet.gl.GL_LINE_SMOOTH)
        pyglet.gl.glClearColor(*self.BG_COLOR)
        self.set_location(*self.WINDOW_POS)
        self.controller = controller

        self.show_warmup_screen = show_warmup_screen
        self.warmup = WarmupControl(controller.level, show_warmup_screen)
        self.track = TrackGraphics(controller.level)
        self.score_box = ScoreBox(controller.level)

        car_count = self.controller.get_player_count()
        self.cars = [CarGraphics(ix + 1, controller.level, show_traces=show_traces)
                     for ix in range(car_count)]
        self.pause_overlay = GameOverlay(controller.level, 'Paused', '"p" to continue...')
        self.end_overlay = None
        self.fps_display = pyglet.window.FPSDisplay(window=self) if show_fps else None
        self.indicator = Indicators() if ENABLE_INDICATORS else None
        self.ranking = RankingBox(controller.level)

        self.controller.set_reset_hook(self.on_reset)

    def on_reset(self):
        self.end_overlay = None
        self.warmup.reset()
        if self.indicator:
            self.indicator.reset()

    def start(self):
        pyglet.clock.schedule_interval(self.update, 1 / 120.0)
        self.warmup.next_screen()
        pyglet.app.run()

    def on_draw(self):
        self.clear()
        self.track.draw()
        for stopped_car in filter(lambda car: car.show_dead_x, self.cars):
            stopped_car.draw()
        for active_car in filter(lambda car: not car.show_dead_x, self.cars):
            active_car.draw()

        if self.warmup.show:
            self.warmup.screen.draw()
        elif self.controller.show_end_screen:
            if not self.end_overlay:
                self.end_overlay = GameOverlay(self.controller.level, *self.controller.get_end_text())
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
        if self.warmup.control_released:
            self.controller.update_player_states(dt)

        player_states = self.controller.get_player_states()
        for player_state, car in zip(player_states, self.cars):
            car.update(player_state)

        self.score_box.update_text(self.controller.get_score_text())
        self.ranking.update(self.controller.get_ranking())
        if self.indicator and not self.controller.show_paused_screen:
            self.indicator.update(player_states[-1])


class WarmupControl:
    def __init__(self, level, show_warmup_screen):
        self.__default_warmup = show_warmup_screen
        self.show = self.__default_warmup
        self.control_released = not self.__default_warmup
        self.screen = WarmupSequence(level)

    def reset(self):
        self.screen.reset()
        self.show = self.__default_warmup
        self.control_released = not self.__default_warmup
        self.next_screen()

    def next_screen(self, _=None):
        if self.show:
            self.show = next(self.screen, False)
            if self.show:
                self.control_released = self.screen.shows_last_screen()
                delay = self.screen.current_delay()
                pyglet.clock.schedule_once(self.next_screen, delay)
