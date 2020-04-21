from typing import List

from pyglet.window import key

from game.racer_engine import RacerEngine, PlayerOperation, PlayerState
from game.racer_window import RaceController
from game.racer_window import RacerWindow


class DemoMaster:
    def __init__(self):
        self.controller = DemoController()

    def run(self):
        w = RacerWindow(self.controller, show_warmup_screen=False, show_traces=False)
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
        self.time = 0
        self.player1 = DemoPlayer(self.level)
        self.player2 = DemoPlayer(self.level, 1.5)

    def get_player_count(self):
        return 2

    def reset(self):
        super().reset()
        self.time = 0
        self.player1.reset()
        self.player2.reset()

    def on_key_press(self, symbol):
        if self.show_end_screen:
            if symbol == key.N:
                self.reset()

    def get_score_text(self):
        return '2 player demo'

    def update_player_states(self, dt):
        if not self.show_end_screen:
            self.time += dt
            self.player1.update_position(dt, self.time)
            self.player2.update_position(dt, self.time)

        if self.player1.engine.game_over and self.player2.engine.game_over:
            self.show_end_screen = True

    def get_player_states(self) -> List[PlayerState]:
        return [self.player1.get_state(), self.player2.get_state()]

    def get_end_text(self):
        return 'Game over!', '"n" New game'


class DemoPlayer:
    def __init__(self, level, time_delay=0):
        self.time_delay, self.level = time_delay, level
        self.engine = RacerEngine(self.level)
        self.next_step_ix = -1
        self.next_step = None
        self.__set_next_step__()

    def __set_next_step__(self):
        self.next_step_ix = min(self.next_step_ix + 1, len(MOVES) - 1)
        self.next_step = MOVES[self.next_step_ix]

    def reset(self):
        self.engine = RacerEngine(self.level)
        self.next_step_ix = -1
        self.next_step = None
        self.__set_next_step__()

    def update_position(self, dt, time):
        if self.engine.game_over or time < self.time_delay:
            return
        if self.next_step[0] + self.time_delay < time:
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

    def get_state(self):
        return self.engine.player_state
