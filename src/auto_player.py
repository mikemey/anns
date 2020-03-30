from game_engine import BoxPusherEngine, Direction
from game_window import GameObserver, BoxPusherWindow


class AutoPlayer:
    def next_move(self, engine):
        pass


class AutomaticMaster(GameObserver):
    def __init__(self, engine: BoxPusherEngine, player: AutoPlayer,
                 close_automatically=False, disable_text=False):
        self.window = None
        self.engine = engine
        self.player = player
        self.auto_close = close_automatically
        self.disable_text = disable_text

    def start(self):
        self.window = BoxPusherWindow(self, False, self.disable_text)
        self.window.reset_game(self.engine, "AI run")
        self.window.start()

    def game_done(self):
        self.window.stop()

    def next_move(self):
        self.player.next_move(self.engine)
        if self.auto_close and self.engine.game_over():
            self.window.stop()


DEMO_LEVEL = {
    'field': (4, 4),
    'player': (1, 0),
    'walls': [],
    'boxes': [(2, 1)],
    'goal': (3, 3),
    'max_points': 20
}


class DemoPlayer(AutoPlayer):
    def __init__(self):
        self.move_ix = -1
        self.moves = [
            Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.RIGHT,
            Direction.UP, Direction.UP
        ]

    def next_move(self, engine):
        self.move_ix += 1
        engine.player_move(self.moves[self.move_ix])


if __name__ == "__main__":
    demo_engine = BoxPusherEngine(DEMO_LEVEL)
    AutomaticMaster(demo_engine, DemoPlayer()).start()
