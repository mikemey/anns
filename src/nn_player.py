import neat

from auto_player import AutomaticMaster, AutoPlayer
from fitness_calc import create_fitness_calculator
from game_engine import BoxPusherEngine, Direction, MOVE_VECTOR
from training_levels import Level

first_training_level = Level(
    field_size=(5, 5),
    player=(4, 1),
    walls=[],
    boxes=[(1, 3)],
    goal=(0, 1),
    max_points=20
)


class NeuralNetMaster:
    def __init__(self, training_levels=[first_training_level]):
        assert len(training_levels) > 0, "at least one level required"
        self.levels = training_levels

    @staticmethod
    def create_game(genome, config, level):
        engine = BoxPusherEngine(level)
        game_state = GameState(engine)
        player = NeuralNetPlayer(game_state, genome, config)
        return engine, player

    def eval_genome(self, genome, config):
        fitness_sum = 0
        for level in self.levels:
            engine, player = self.create_game(genome, config, level)
            calculator = create_fitness_calculator(engine, level)
            while not engine.game_over():
                player.next_move(engine)
            fitness_sum += calculator.get_fitness()
        return fitness_sum / len(self.levels)

    def showcase_genome(self, genome, config):
        showcase_level = self.levels[0]
        showcase_level.print()
        engine, player = self.create_game(genome, config, showcase_level)
        calculator = create_fitness_calculator(engine, showcase_level, True)
        auto_master = AutomaticMaster(engine, player, True, True)
        auto_master.start()
        print('Showcase genome: {}, average fitness: {:.0f}, showcase-level fitness: {:.0f}'
              .format(genome.key, genome.fitness, calculator.get_fitness()))


class GameState:
    def __init__(self, engine: BoxPusherEngine):
        self.engine = engine
        self.norm_width = engine.field_size[0] - 1
        self.norm_height = engine.field_size[1] - 1
        self.grid_template = [0.0] * engine.field_size[0] * engine.field_size[1]

    def get_current(self):
        return self.__positional_state__()

    def __positional_state__(self):
        # allowed_moves = [
        #     self.__norm_direction__(Direction.UP),
        #     self.__norm_direction__(Direction.DOWN),
        #     self.__norm_direction__(Direction.LEFT),
        #     self.__norm_direction__(Direction.RIGHT)
        # ]
        return \
            self.__norm_position__(self.engine.player) + \
            self.__norm_position__(self.engine.goal) + \
            self.__norm_position__(self.engine.boxes[0])

    def __grid_state__(self):
        grid = self.grid_template.copy()
        grid[self.__position_ix__(self.engine.player)] = 0.25
        grid[self.__position_ix__(self.engine.goal)] = 0.5
        grid[self.__position_ix__(self.engine.boxes[0])] = 0.75
        return grid

    def __position_ix__(self, pos):
        return pos[0] * self.engine.field_size[0] + pos[1]

    def __norm_position__(self, pos):
        return [pos[0] / self.norm_width, pos[1] / self.norm_height]

    def __norm_direction__(self, direction):
        return 1.0 if self.engine.can_move_to(self.engine.player + MOVE_VECTOR[direction]) \
            else 0.0


class NeuralNetPlayer(AutoPlayer):
    def __init__(self, game_state: GameState, genome, config):
        self.net = neat.nn.FeedForwardNetwork.create(genome, config)
        self.game_state = game_state
        self.directions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]

    def next_move(self, engine):
        output = self.net.activate(self.game_state.get_current())
        direction_ix = output.index(max(output))
        engine.player_move(self.directions[direction_ix])


if __name__ == '__main__':
    test_level = first_training_level
    print('Level:', vars(test_level))
    test_level.print()
    state = GameState(BoxPusherEngine(test_level))
    raw_state = state.get_current()
    print(raw_state)
    # for ix, cell in enumerate(raw_state):
    #     if (ix % test_level.field_size[0]) == 0:
    #         print()
    #     print(' {:.2f}'.format(cell), end='')
