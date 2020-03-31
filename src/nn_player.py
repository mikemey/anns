import neat

from auto_player import AutomaticMaster, AutoPlayer
from game_engine import BoxPusherEngine, Direction, MOVE_VECTOR, GameListener, positions_contains
from training_levels import Level, distance_between


class PenaltyCalculator(GameListener):
    def __init__(self, verbose=False):
        super().__init__()
        self.verbose = verbose
        self.unmoved_box_penalty = 10
        self.penalty = self.unmoved_box_penalty
        self.covered_positions = []

    def __log__(self, *data):
        if self.verbose:
            print(*data)

    def new_position(self, pos):
        self.__log__(' new pos:', pos)
        if positions_contains(self.covered_positions, pos):
            self.__log__('path pen: 1')
            self.penalty += 1
        else:
            self.covered_positions.append(pos.copy())

    def box_move(self):
        if self.unmoved_box_penalty:
            self.__log__(' BOX move')
            self.penalty -= self.unmoved_box_penalty
            self.unmoved_box_penalty = False


class NeuralNetMaster:
    def __init__(self):
        self.level = Level.generate_level()
        self.level_box_error = distance_error(self.level.goal, self.level.boxes)

    def __create_game__(self, genome, config):
        engine = BoxPusherEngine(self.level.as_game_config())
        game_state = GameState(engine)
        player = NeuralNetPlayer(game_state, genome, config)
        return engine, player

    def eval_genome(self, genome, config):
        engine, player = self.__create_game__(genome, config)
        calculator = PenaltyCalculator()
        engine.listeners.add(calculator)
        while not engine.game_over():
            player.next_move(engine)

        box_error = 10 * (distance_error(engine.goal, engine.boxes) / self.level_box_error)
        genome.fitness = engine.points - box_error - calculator.penalty

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
        engine = self.engine
        pl = self.engine.player

        allowed_moves = [
            engine.can_move_to(pl + MOVE_VECTOR[Direction.UP]),
            engine.can_move_to(pl + MOVE_VECTOR[Direction.DOWN]),
            engine.can_move_to(pl + MOVE_VECTOR[Direction.LEFT]),
            engine.can_move_to(pl + MOVE_VECTOR[Direction.RIGHT])
        ]
        return \
            allowed_moves + \
            self.__norm_pos__(pl) + \
            self.__norm_pos__(engine.goal) + \
            self.__norm_pos__(engine.boxes[0])

    def __norm_pos__(self, pos):
        return [pos[0] / self.norm_width, pos[1] / self.norm_height]


class NeuralNetPlayer(AutoPlayer):
    def __init__(self, game_state: GameState, genome, config):
        self.net = neat.nn.RecurrentNetwork.create(genome, config)
        self.game_state = game_state
        self.directions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]

    def next_move(self, engine):
        output = self.net.activate(self.game_state.get_current())
        direction_ix = output.index(max(output))
        engine.player_move(self.directions[direction_ix])


def distance_error(goal, boxes):
    err = 0
    for box in boxes:
        err += distance_between(goal, box)
    return err


if __name__ == '__main__':
    test_level = Level.generate_level()
    print('Level:', test_level.as_game_config())
    test_level.print()
