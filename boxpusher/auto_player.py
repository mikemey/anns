from box_game.game_engine import BoxPusherEngine, Level, Direction
from box_game.game_window import GameWindowObserver, BoxPusherWindow


class AutoPlayer:
    def next_move(self, engine):
        pass


class AutomaticMaster(GameWindowObserver):
    def __init__(self, engine: BoxPusherEngine, player: AutoPlayer,
                 close_automatically=False, disable_text=False):
        self.engine = engine
        self.player = player
        self.auto_close = close_automatically
        self.window = BoxPusherWindow(self, False, disable_text)

    def start(self):
        self.window.reset_game(self.engine, "AI run")
        self.window.start()

    def game_done(self, quit_game):
        self.window.stop()

    def next_move(self):
        self.player.next_move(self.engine)
        if self.auto_close and self.engine.game_over():
            self.window.stop()


DEMO_LEVEL = Level(
    field_size=(4, 4),
    player=(1, 0),
    walls=[],
    boxes=[(2, 1)],
    goal=(3, 3),
    max_points=20
)


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
