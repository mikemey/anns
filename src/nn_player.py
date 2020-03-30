import random

import neat
import numpy as np

from auto_player import AutoPlayer
from game_engine import BoxPusherEngine, Direction

# field-pins: [Wall, Player, Goal, Box]
FIELD_PINS_LEN = 4
WALL_PIN_OFFSET = 0
PLAYER_PIN_OFFSET = 1
GOAL_PIN_OFFSET = 2
BOX_PIN_OFFSET = 3


def generate_level():
    occupied = []
    walls = [find_available_pos(occupied, 0, 5) for _ in range(random.randrange(0, 4))]
    player = find_available_pos(occupied, 0, 5)
    goal = find_available_pos(occupied, 0, 5, (2, 2), 1)
    box = find_available_pos(occupied, 1, 4, goal, 3)
    return {
        'field': (5, 5),
        'player': player,
        'walls': walls,
        'boxes': [box],
        'goal': goal,
        'max_points': 50
    }


def find_available_pos(occupied, start, exclusive_end, avoid_pos=None, min_dist=0):
    new_pos = (random.randrange(start, exclusive_end, 1), random.randrange(start, exclusive_end, 1))
    if new_pos in occupied:
        return find_available_pos(occupied, start, exclusive_end, avoid_pos, min_dist)
    elif avoid_pos is not None and distance_between(new_pos, avoid_pos) < min_dist:
        return find_available_pos(occupied, start, exclusive_end, avoid_pos, min_dist)
    else:
        occupied.append(new_pos)
        return new_pos


class NeuralNetMaster:
    def __init__(self):
        self.level = generate_level()
        self.level_box_error = distance_error(self.level['goal'], self.level['boxes'])
        self.field_size = self.level['field']
        self.pins_template = [0] * FIELD_PINS_LEN * self.field_size[0] * self.field_size[1]
        self.print_state = True

    def eval_genome(self, genome, config):
        engine = BoxPusherEngine(self.level)

        game_state = GameState(engine)
        player = NeuralNetPlayer(game_state, genome, config)
        if self.print_state:
            self.print_state = False
            game_state.print()

        while not engine.game_over():
            player.next_move(engine)

        box_error = 10 * (distance_error(engine.goal, engine.boxes) / self.level_box_error)
        genome.fitness = engine.points - box_error

    # def showcase_genome(self, genome, config):
    #     print('Showcase fitness:', genome.fitness)
    #     auto_master = AutomaticMaster(self.level, NeuralNetPlayer(genome, config))
    #     auto_master.start()


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
        pins = self.get_current()
        line = '=============='
        for i in range(len(pins)):
            if (i % (FIELD_PINS_LEN * self.field_width)) == 0:
                print(line)
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
        print(line)
        print('==============')


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
