import arcade

from game_engine import BoxPusherEngine
from game_window import GameObserver, BoxPusherWindow
from levels import LEVELS


class GameMaster(GameObserver):
    def __init__(self):
        self.current_level_ix = 0
        self.window = None

    def start(self):
        self.window = BoxPusherWindow(self)
        self.window.set_location(0, 0)
        self.window.reset_game(self.new_game_engine())
        arcade.run()

    def game_done(self):
        self.window.reset_game(self.new_game_engine())

    def new_game_engine(self):
        return BoxPusherEngine(LEVELS[self.current_level_ix])


if __name__ == "__main__":
    GameMaster().start()
