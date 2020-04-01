from game_engine import BoxPusherEngine, GameListener
from training_levels import Level, distance_between


class FitnessCalculator(GameListener):
    def __init__(self, engine: BoxPusherEngine, level: Level, verbose=False):
        super().__init__()
        self.engine = engine
        self.verbose = verbose
        self.score = level.max_points
        self.covered_positions = []

        self.level_box_error = self.__current_box_error_to__(self.engine.goal)
        self.engine.listeners.add(self)
        self.__log__('-- start --')

    def __current_box_error_to__(self, pos):
        err = 0
        for box in self.engine.boxes:
            err += distance_between(box, pos)
        return err

    def __log__(self, *data):
        if self.verbose:
            print('score: {:4}'.format(self.score), *data)

    def new_position(self, pos):
        self.score -= 1
        self.__log__('new pos:', pos)
        for p in self.covered_positions:
            if (p == pos).all():
                self.score -= 2
                self.__log__('field covered')
        self.covered_positions.append(pos.copy())

    def box_move(self):
        self.score += 10
        self.__log__('box move')

    def box_in_goal(self):
        self.score += 30
        self.__log__('box in goal')

    def invalid_move(self):
        self.score -= 10
        self.__log__('invalid move')

    def get_fitness(self):
        box_error = 50 * (self.__current_box_error_to__(self.engine.goal) / self.level_box_error) ** 2
        player_error = 50 * (self.__current_box_error_to__(self.engine.player) - len(self.engine.boxes)) ** 2
        self.__log__('box    error:', box_error)
        self.__log__('player error:', player_error)
        return self.score - box_error - player_error
