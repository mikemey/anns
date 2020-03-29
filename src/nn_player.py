import random

import neat
import numpy as np

from game_engine import BoxPusherEngine, Direction

OUTPUT_DIRECTIONS = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]

# field-pins: [Wall, Player, Goal, Box]
FIELD_PINS_LEN = 4
WALL_PIN_OFFSET = 0
PLAYER_PIN_OFFSET = 1
GOAL_PIN_OFFSET = 2
BOX_PIN_OFFSET = 3


def generate_level():
    occupied = []
    player = find_available_pos(occupied, 0, 5)
    goal = find_available_pos(occupied, 0, 5)
    box = find_available_pos(occupied, 1, 4)
    return {
        'field': (5, 5),
        'player': player,
        'walls': [],
        'boxes': [box],
        'goal': goal,
        'max_points': 50
    }


def find_available_pos(occupied, start, exclusive_end):
    new_pos = (random.randrange(start, exclusive_end, 1), random.randrange(start, exclusive_end, 1))
    if new_pos in occupied:
        return find_available_pos(occupied, start, exclusive_end)
    else:
        occupied.append(new_pos)
        return new_pos


class NeuralNetMaster:
    def __init__(self):
        self.level = generate_level()
        self.level_box_error = distance_error(self.level['goal'], self.level['boxes'])
        field = self.level['field']
        self.pins_template = [0] * FIELD_PINS_LEN * field[0] * field[1]

    def eval_genome(self, genome, config):
        engine = BoxPusherEngine(self.level)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        while not engine.game_over():
            game_state = self.__get_game_state__(engine)
            output = net.activate(game_state)
            direction_ix = output.index(max(output))
            engine.player_move(OUTPUT_DIRECTIONS[direction_ix])

        box_error = 10 * (distance_error(engine.goal, engine.boxes) / self.level_box_error)
        genome.fitness = engine.points - box_error

    def __get_game_state__(self, engine):
        pins = self.pins_template.copy()

        field_width = engine.field_size[0]
        enable_pin(pins, field_width, engine.player, PLAYER_PIN_OFFSET)
        enable_pin(pins, field_width, engine.goal, GOAL_PIN_OFFSET)
        for box in engine.boxes:
            enable_pin(pins, field_width, box, BOX_PIN_OFFSET)
        for wall in engine.walls:
            enable_pin(pins, field_width, wall, WALL_PIN_OFFSET)

        return pins


def distance_error(goal, boxes):
    err = 0
    for box in boxes:
        err += sum(np.absolute(np.array(box) - np.array(goal)))
    return err


def enable_pin(pins, width, field_pos, pin_offset):
    pix = FIELD_PINS_LEN * field_pos[0] + FIELD_PINS_LEN * width * field_pos[1] + pin_offset
    pins[pix] = 1

# line = '=============='
# for i in range(len(pins)):
#     if (i % (3 * engine.field_size[0])) == 0:
#         print(line)
#         line = ''
#     if (i % 3) == 0:
#         next_field = pins[i:i + 3]
#         if next_field[0]:
#             line += ' P'
#         elif next_field[1]:
#             line += ' G'
#         elif next_field[2]:
#             line += ' B'
#         else:
#             line += ' ░'
# print(line)
# print('==============')
