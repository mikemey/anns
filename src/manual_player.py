from fitness_calc import FitnessCalculator
from game_engine import BoxPusherEngine
from game_window import GameWindowObserver, BoxPusherWindow
from manual_levels import LEVELS


class GameMaster(GameWindowObserver):
    def __init__(self):
        self.current_level_ix = 0
        self.window = BoxPusherWindow(self)
        self.calculator = None

    def start(self):
        self.create_game()
        self.window.start()

    def game_done(self, quit_game):
        if quit_game:
            self.window.stop()
            return

        print('Player fitness:', self.calculator.get_fitness())
        if self.window.engine.game_won:
            self.current_level_ix = (self.current_level_ix + 1) % len(LEVELS)
        self.create_game()

    def create_game(self):
        level = LEVELS[self.current_level_ix]
        engine = BoxPusherEngine(level)
        self.calculator = FitnessCalculator(engine, level, True)
        self.window.reset_game(engine, "Level {}".format(self.current_level_ix + 1))


if __name__ == "__main__":
    GameMaster().start()
