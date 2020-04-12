from typing import Tuple

from pyglet.window import key

from game.racer_engine import RacerEngine, PlayerOperation
from game.racer_window import RaceController
from game.racer_window import RacerWindow


class DemoMaster:
    def __init__(self):
        self.controller = DemoController()

    def run(self):
        w = RacerWindow(self.controller)
        w.start()


FORWARD = 0
REVERSE = 1
LEFT = 2
RIGHT = 3

MOVES = [
    (0.4, FORWARD, None),
    (0.5, FORWARD, LEFT),
    (1.2, FORWARD, None),
    (1.45, FORWARD, LEFT),
    (2.4, FORWARD, None),
    (3.2, FORWARD, RIGHT),
    (4.8, FORWARD, None),
    (5.58, FORWARD, RIGHT),
    (6.0, None, None),
    (6.55, FORWARD, RIGHT),
    (6.75, None, None),
    (7.6, None, LEFT),
    (8.2, FORWARD, LEFT),
    (9.2, FORWARD, None),
    (9.3, FORWARD, LEFT),
    (10.0, FORWARD, None),
    (10.25, FORWARD, RIGHT),
    (10.45, FORWARD, None),
    (10.8, FORWARD, RIGHT),
    (11.4, FORWARD, None),
    (11.5, FORWARD, RIGHT),
    (12.55, FORWARD, None),
    (13.3, FORWARD, RIGHT),
    (13.8, FORWARD, None),
    (13.9, FORWARD, RIGHT),
    (14.5, FORWARD, None),
    (20.0, FORWARD, LEFT)
]


class DemoController(RaceController):
    def __init__(self):
        super().__init__()
        self.engine = RacerEngine()
        self.time = 0
        self.next_step_ix = -1
        self.next_step = None
        self.__set_next_step__()

    def reset(self):
        super().reset()
        self.engine = RacerEngine()
        self.time = 0
        self.next_step_ix = -1
        self.__set_next_step__()

    def __set_next_step__(self):
        self.next_step_ix = min(self.next_step_ix + 1, len(MOVES) - 1)
        self.next_step = MOVES[self.next_step_ix]

    def on_key_press(self, symbol):
        if self.show_lost_screen:
            if symbol == key.N:
                self.reset()

    def get_score(self):
        return self.engine.score

    def update_player(self, dt) -> Tuple[float, float, float]:
        if self.show_paused_screen or self.show_lost_screen:
            return
        self.time += dt
        if self.next_step[0] < self.time:
            self.__set_next_step__()

        move, turn = self.next_step[1], self.next_step[2]
        operation = PlayerOperation()
        if move == FORWARD:
            operation.accelerate()
        elif move == REVERSE:
            operation.reverse()
        if turn == LEFT:
            operation.turn_left()
        elif turn == RIGHT:
            operation.turn_right()
        self.engine.update(dt, operation)
        if self.engine.game_over:
            self.show_lost_screen = True
            return
        pl = self.engine.player
        return pl.position[0], pl.position[1], pl.rotation
