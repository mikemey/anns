from typing import List

from pyglet.window import key

from game.racer_engine import RacerEngine, PlayerOperation
from game.racer_window import RaceController, PlayerState
from game.racer_window import RacerWindow


class ManualMaster:
    def __init__(self, two_players=False):
        self.controller = ManualController(two_players)

    def run(self):
        w = RacerWindow(self.controller, show_traces=not self.controller.two_players)
        w.start()


PLAYER1_KEYS = key.UP, key.DOWN, key.LEFT, key.RIGHT
PLAYER2_KEYS = key.W, key.S, key.A, key.D


class ManualController(RaceController):
    def __init__(self, two_players: bool):
        super().__init__()
        self.two_players = two_players
        self.players = self.__setup_players()

    def reset(self):
        super().reset()
        self.players = self.__setup_players()

    def __setup_players(self):
        if self.two_players:
            player1 = ManualPlayer(*PLAYER1_KEYS)
            player1.state.y += 10
            player2 = ManualPlayer(*PLAYER2_KEYS)
            player2.state.y -= 20
            return [player2, player1]
        return [ManualPlayer(*PLAYER1_KEYS)]

    def get_player_count(self):
        return len(self.players)

    def on_key_press(self, symbol):
        if self.show_end_screen:
            if symbol == key.N:
                self.reset()
            return
        if symbol == key.P:
            self.show_paused_screen = not self.show_paused_screen
        for player in self.players:
            player.on_key_press(symbol)

    def on_key_release(self, symbol):
        for player in self.players:
            player.on_key_release(symbol)

    def focus_lost(self):
        self.show_paused_screen = True

    def get_score_text(self):
        if self.two_players:
            diff = self.players[1].score - self.players[0].score
            if diff == 0:
                return '=='
            return 'Player 1' if diff > 0 else 'Player 2'
        return 'Score: {:.0f}'.format(self.players[0].score)

    def update_player_states(self, dt):
        if not (self.show_paused_screen or self.show_end_screen):
            for player in self.players:
                player.update(dt)

            if all([player.engine.game_over for player in self.players]):
                self.show_end_screen = True

    def get_player_states(self) -> List[PlayerState]:
        return [player.state for player in self.players]

    def get_end_text(self):
        if self.two_players:
            return 'Winner:  {}'.format(self.get_score_text()), '"n" New game'
        return 'Lost!', '"n" New game'


class ManualPlayer:
    def __init__(self, up, down, left, right):
        self.score = 0
        self.engine = RacerEngine()
        self.operation = PlayerOperation()
        self.up, self.down, self.left, self.right = up, down, left, right

    @property
    def state(self):
        return self.engine.player_state

    def on_key_press(self, symbol):
        if symbol == self.up:
            self.operation.accelerate()
        if symbol == self.down:
            self.operation.reverse()
        if symbol == self.left:
            self.operation.turn_left()
        if symbol == self.right:
            self.operation.turn_right()

    def on_key_release(self, symbol):
        if symbol in (self.up, self.down):
            self.operation.stop_direction()
        if symbol == self.left:
            self.operation.stop_left()
        if symbol == self.right:
            self.operation.stop_right()

    def update(self, dt):
        if not self.engine.game_over:
            self.engine.update(dt, self.operation)
            relevant_speed = self.engine.player_state.relevant_speed
            amp = 0.002 if relevant_speed < 0 else 0.001
            self.score += relevant_speed * amp
