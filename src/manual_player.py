from game_engine import BoxPusherEngine
from game_window import GameObserver, BoxPusherWindow
from manual_levels import LEVELS


class GameMaster(GameObserver):
    def __init__(self):
        self.current_level_ix = 0
        self.window = BoxPusherWindow(self)

    def start(self):
        self.create_game()
        self.window.start()

    def game_done(self, quit_game):
        if quit_game:
            self.window.stop()
            return
        if self.window.engine.game_won:
            self.current_level_ix = (self.current_level_ix + 1) % len(LEVELS)
        self.create_game()

    def create_game(self):
        engine = BoxPusherEngine(LEVELS[self.current_level_ix])
        self.window.reset_game(engine, "Level {}".format(self.current_level_ix + 1))


if __name__ == "__main__":
    GameMaster().start()
