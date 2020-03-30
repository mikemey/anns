import random

import neat
import numpy as np

from auto_player import AutomaticMaster, AutoPlayer
from game_engine import BoxPusherEngine, Direction, GameListener, positions_contains

# field-pins: [Wall, Player, Goal, Box]
FIELD_PINS_LEN = 4
WALL_PIN_OFFSET = 0
PLAYER_PIN_OFFSET = 1
GOAL_PIN_OFFSET = 2
BOX_PIN_OFFSET = 3


def generate_level():
    try:
        occupied = []
        walls = []
        # walls = [find_available_pos(occupied, 0, 5) for _ in range(random.randrange(0, 4))]
        player = find_available_pos(occupied, 0, 5)
        goal = find_available_pos(occupied, 0, 5, (2, 2), 1)
        box = find_available_pos(occupied, 1, 4, goal, 3, True)
        return {
            'field': (5, 5),
            'player': player,
            'walls': walls,
            'boxes': [box],
            'goal': goal,
            'max_points': 20
        }
    except RecursionError:
        return generate_level()


def find_available_pos(occupied, start, exclusive_end, avoid_pos=None, min_dist=0, avoid_same_line=False):
    new_pos = (random.randrange(start, exclusive_end, 1), random.randrange(start, exclusive_end, 1))
    if new_pos in occupied:
        return find_available_pos(occupied, start, exclusive_end, avoid_pos, min_dist, avoid_same_line)
    elif avoid_pos is not None and distance_between(new_pos, avoid_pos) < min_dist:
        return find_available_pos(occupied, start, exclusive_end, avoid_pos, min_dist, avoid_same_line)
    elif avoid_same_line and (new_pos[0] == avoid_pos[0] or new_pos[1] == avoid_pos[1]):
        return find_available_pos(occupied, start, exclusive_end, avoid_pos, min_dist, avoid_same_line)
    else:
        occupied.append(new_pos)
        return new_pos


class PenaltyCalculator(GameListener):
    def __init__(self, verbose=False):
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
        self.level = generate_level()
        self.level_box_error = distance_error(self.level['goal'], self.level['boxes'])
        self.field_size = self.level['field']
        self.pins_template = [0] * FIELD_PINS_LEN * self.field_size[0] * self.field_size[1]

    def __create_game__(self, genome, config):
        engine = BoxPusherEngine(self.level)
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

    def print_level(self):
        GameState(BoxPusherEngine(self.level)).print()

    def showcase_genome(self, genome, config):
        print('Showcase genome: {}, fitness: {}'.format(genome.key, genome.fitness))
        engine, player = self.__create_game__(genome, config)
        auto_master = AutomaticMaster(engine, player, True, True)
        auto_master.start()


class GameState:
    def __init__(self, engine):
        self.engine = engine
        self.field_width = self.engine.field_size[0]
        field_height = self.engine.field_size[1]
        self.pins_template = [0] * FIELD_PINS_LEN * self.field_width * field_height

    def get_current(self):
        pins = self.pins_template.copy()

        enable_pin(pins, self.field_width, self.engine.player, PLAYER_PIN_OFFSET)
        enable_pin(pins, self.field_width, self.engine.goal, GOAL_PIN_OFFSET)
        for box in self.engine.boxes:
            enable_pin(pins, self.field_width, box, BOX_PIN_OFFSET)
        for wall in self.engine.walls:
            enable_pin(pins, self.field_width, wall, WALL_PIN_OFFSET)

        return pins

    def print(self):
        field = list()
        pins = self.get_current()
        line = '=============='
        for i in range(len(pins)):
            if (i % (FIELD_PINS_LEN * self.field_width)) == 0:
                field.append(line)
                line = ''
            if (i % FIELD_PINS_LEN) == 0:
                next_field = pins[i:i + FIELD_PINS_LEN]
                if next_field[PLAYER_PIN_OFFSET]:
                    line += ' ¥'
                elif next_field[GOAL_PIN_OFFSET]:
                    line += ' @'
                elif next_field[BOX_PIN_OFFSET]:
                    line += ' ▭'
                elif next_field[WALL_PIN_OFFSET]:
                    line += ' █'
                else:
                    line += ' ░'
        field.append(line)
        field.append('==============')
        for line in reversed(field):
            print(line)


class NeuralNetPlayer(AutoPlayer):
    def __init__(self, game_state: GameState, genome, config):
        self.net = neat.nn.FeedForwardNetwork.create(genome, config)
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


def distance_between(pos_a, pos_b):
    return sum(np.absolute(np.array(pos_a) - np.array(pos_b)))


def enable_pin(pins, width, field_pos, pin_offset):
    pix = FIELD_PINS_LEN * field_pos[0] + FIELD_PINS_LEN * width * field_pos[1] + pin_offset
    pins[pix] = 1


if __name__ == '__main__':
    master = NeuralNetMaster()
    print('Level:', master.level)
    GameState(BoxPusherEngine(master.level)).print()
