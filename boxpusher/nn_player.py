import neat
import numpy as np

from auto_player import AutomaticMaster, AutoPlayer
from fitness_calc import create_fitness_calculator
from box_game.game_engine import BoxPusherEngine, Level, Direction, MOVE_VECTOR
from box_game.training_levels import generate_level
from training_reporter import FITNESS_FORMAT

SHOWCASE_TEMPLATE = 'Showcase genome: {{}}, average fitness: {0}, showcase-level fitness: {0}'.format(FITNESS_FORMAT)
first_training_level = Level(
    field_size=(5, 5),
    player=(4, 1),
    walls=[],
    boxes=[(1, 3)],
    goal=(0, 1),
    max_points=20
)


def generate_training_levels():
    return [generate_level() for _ in range(30)]


class NeuralNetMaster:
    def __init__(self):
        self.levels = generate_training_levels()

    @staticmethod
    def create_game(genome, config, level):
        engine = BoxPusherEngine(level)
        game_state = GameState(engine)
        player = NeuralNetPlayer(game_state, genome, config)
        return engine, player

    def eval_genome(self, genome, config):
        fitness_sum, box_moves, goals, wins, lost = 0, 0, 0, 0, 0
        for level in self.levels:
            engine, calculator = self.__play_game__(genome, config, level)
            fitness_sum += calculator.get_fitness()
            box_moves += calculator.box_moves
            goals += calculator.box_in_goals
            if engine.game_won:
                wins += 1
            if engine.game_lost:
                lost += 1
        return fitness_sum / len(self.levels), box_moves, goals, wins, lost

    def __play_game__(self, genome, config, level):
        engine, player = self.create_game(genome, config, level)
        calculator = create_fitness_calculator(engine, level)
        while not engine.game_over():
            player.next_move(engine)
        return engine, calculator

    def showcase_genome(self, genome, config):
        showcase_level = self.levels[0]
        _, calculator = self.__play_game__(genome, config, showcase_level)
        print(SHOWCASE_TEMPLATE.format(genome.key, genome.fitness, calculator.get_fitness()))

        engine, player = self.create_game(genome, config, showcase_level)
        # create_fitness_calculator(engine, showcase_level, False)  # print fitness calculation details
        auto_master = AutomaticMaster(engine, player, True, True)
        auto_master.start()


class GameState:
    def __init__(self, engine: BoxPusherEngine):
        self.engine = engine
        self.norm_width = engine.field_size[0] - 1
        self.norm_height = engine.field_size[1] - 1
        self.grid_template = [0.0]  # * engine.field_size[0] * engine.field_size[1]

    def get_current(self):
        return self.__all_relative_state__()

    def __player_relative_state__(self):
        return np.concatenate((
            self.__norm_distance__(self.engine.player, self.engine.goal),
            self.__norm_distance__(self.engine.player, self.engine.boxes[0])
        ))

    def __all_relative_state__(self):
        return np.concatenate((
            self.__norm_distance__(self.engine.player, self.engine.boxes[0]),
            self.__norm_distance__(self.engine.boxes[0], self.engine.goal)
        ))

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
        grid[self.__position_ix__(self.engine.boxes[0])] = 0.5
        grid[self.__position_ix__(self.engine.goal)] += 0.75
        return grid

    def __position_ix__(self, pos):
        return pos[0] * self.engine.field_size[0] + pos[1]

    def __norm_position__(self, pos):
        return [pos[0] / self.norm_width, pos[1] / self.norm_height]

    def __norm_direction__(self, direction):
        return 1.0 if self.engine.can_move_to(self.engine.player + MOVE_VECTOR[direction]) \
            else 0.0

    def __norm_distance__(self, pos_a, pos_b):
        diff = pos_b - pos_a
        return diff[0] / self.norm_width, diff[1] / self.norm_height


class NeuralNetPlayer(AutoPlayer):
    def __init__(self, game_state: GameState, genome, config):
        self.net = neat.nn.RecurrentNetwork.create(genome, config)
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
