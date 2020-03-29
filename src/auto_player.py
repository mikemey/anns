import arcade

from game_engine import BoxPusherEngine, Direction
from game_window import GameObserver, BoxPusherWindow

SOLVE_MOVES = [
    Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.RIGHT,
    Direction.UP, Direction.UP
]


def generate_level():
    return {
        'field': (4, 4),
        'player': (1, 0),
        'walls': [],
        'boxes': [(2, 1)],
        'goal': (3, 3),
        'max_points': 20
    }


class AutomaticMaster(GameObserver):
    def __init__(self):
        self.engine = BoxPusherEngine(generate_level())
        self.move_ix = 0

    def start(self):
        window = BoxPusherWindow(self, interactive=False)
        window.reset_game(self.engine, "AI run")
        arcade.run()

    def game_done(self):
        arcade.close_window()

    def next_move(self):
        self.engine.player_move(SOLVE_MOVES[self.move_ix])
        self.move_ix += 1


if __name__ == "__main__":
    AutomaticMaster().start()
