from typing import Tuple

from pyglet.window import key

from game.racer_engine import RacerEngine, PlayerOperation
from game.racer_window import RaceController
from game.racer_window import RacerWindow


class ManualMaster:
    def __init__(self):
        self.controller = ManualController()

    def run(self):
        w = RacerWindow(self.controller)
        w.start()


class ManualController(RaceController):
    def __init__(self):
        super().__init__()
        self.engine = RacerEngine()
        self.player_operations = PlayerOperation()

    def on_key_press(self, symbol):
        if self.show_lost_screen:
            return
        if symbol == key.P:
            self.show_paused_screen = not self.show_paused_screen
        if symbol == key.UP:
            self.player_operations.accelerate()
        if symbol == key.DOWN:
            self.player_operations.reverse()
        if symbol == key.LEFT:
            self.player_operations.turn_left()
        if symbol == key.RIGHT:
            self.player_operations.turn_right()

    def on_key_release(self, symbol):
        if symbol in (key.UP, key.DOWN):
            self.player_operations.stop_direction()
        if symbol == key.LEFT:
            self.player_operations.stop_left()
        if symbol == key.RIGHT:
            self.player_operations.stop_right()

    def focus_lost(self):
        self.show_paused_screen = True

    def get_score(self):
        return self.engine.score

    def update_player(self, dt) -> Tuple[float, float, float]:
        if self.show_paused_screen or self.show_lost_screen:
            return
        self.engine.update(dt, self.player_operations)
        if self.engine.game_over:
            self.show_lost_screen = True
            return
        pl = self.engine.player
        return pl.position[0], pl.position[1], pl.rotation
