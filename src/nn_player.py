import neat

from auto_player import AutomaticMaster, AutoPlayer
from game_engine import BoxPusherEngine, Direction, MOVE_VECTOR, GameListener, positions_contains
from training_levels import Level, distance_between


class NeuralNetMaster:
    def __init__(self):
        self.level = Level.generate_level()

    def __create_game__(self, genome, config):
        engine = BoxPusherEngine(self.level)
        game_state = GameState(engine)
        player = NeuralNetPlayer(game_state, genome, config)
        return engine, player

    def eval_genome(self, genome, config):
        engine, player = self.__create_game__(genome, config)
        calculator = FitnessCalculator(engine, self.level)
        while not engine.game_over():
            player.next_move(engine)
        genome.fitness = calculator.get_fitness()

    def showcase_genome(self, genome, config):
        print('Showcase genome: {}, fitness: {}'.format(genome.key, genome.fitness))
        engine, player = self.__create_game__(genome, config)
        auto_master = AutomaticMaster(engine, player, True, True)
        auto_master.start()


class GameState:
    def __init__(self, engine: BoxPusherEngine):
        self.engine = engine
        self.norm_width = self.engine.field_size[0] - 1
        self.norm_height = self.engine.field_size[1] - 1

    def get_current(self):
        allowed_moves = [
            self.__norm_direction__(Direction.UP),
            self.__norm_direction__(Direction.DOWN),
            self.__norm_direction__(Direction.LEFT),
            self.__norm_direction__(Direction.RIGHT)
        ]
        return \
            allowed_moves + \
            self.__norm_position__(self.engine.player) + \
            self.__norm_position__(self.engine.goal) + \
            self.__norm_position__(self.engine.boxes[0])

    def __norm_position__(self, pos):
        return [pos[0] / self.norm_width, pos[1] / self.norm_height]

    def __norm_direction__(self, direction):
        return 1.0 if self.engine.can_move_to(self.engine.player + MOVE_VECTOR[direction]) \
            else 0.0


class NeuralNetPlayer(AutoPlayer):
    def __init__(self, game_state: GameState, genome, config):
        self.net = neat.nn.RecurrentNetwork.create(genome, config)
        self.game_state = game_state
        self.directions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]

    def next_move(self, engine):
        output = self.net.activate(self.game_state.get_current())
        direction_ix = output.index(max(output))
        engine.player_move(self.directions[direction_ix])


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


if __name__ == '__main__':
    test_level = Level.generate_level()
    print('Level:', test_level)
    test_level.print()
    print(GameState(BoxPusherEngine(test_level)).get_current())
