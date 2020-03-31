from game_engine import BoxPusherEngine, GameListener, positions_contains
from training_levels import Level, distance_between


class FitnessCalculator(GameListener):
    def __init__(self, engine: BoxPusherEngine, level: Level, verbose=False):
        super().__init__()
        self.engine = engine
        self.verbose = verbose
        self.score = level.max_points
        self.covered_positions = []

        self.level_box_error = self.__current_box_error__()
        self.engine.listeners.add(self)
        self.__log__('-- start --')

    def __current_box_error__(self):
        err = 0
        for box in self.engine.boxes:
            err += distance_between(box, self.engine.goal)
        return err

    def __log__(self, *data):
        if self.verbose:
            print('score: {:4}'.format(self.score), *data)

    def new_position(self, pos):
        self.score -= 1
        self.__log__('new pos:', pos)
        if positions_contains(self.covered_positions, pos):
            self.score -= 1
            self.__log__('field covered')
        else:
            self.covered_positions.append(pos.copy())

    def box_move(self):
        self.score += 5
        self.__log__('box move')

    def box_in_goal(self):
        self.score += 10
        self.__log__('box in goal')

    def get_fitness(self):
        box_error = 20 * (self.__current_box_error__() / self.level_box_error) ** 2
        self.__log__('BOX penalty:', box_error)
        return self.score - box_error
