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
    goal = find_available_pos(occupied, 0, 5, (2, 2), 1)
    box = find_available_pos(occupied, 1, 4, goal, 3)
    return {
        'field': (5, 5),
        'player': player,
        'walls': [],
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
        if self.print_state:
            self.print_state = False
            print_game(self.__get_game_state__(engine), self.field_size[0])

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
        err += distance_between(goal, box)
    return err


def distance_between(pos_a, pos_b):
    return sum(np.absolute(np.array(pos_a) - np.array(pos_b)))


def enable_pin(pins, width, field_pos, pin_offset):
    pix = FIELD_PINS_LEN * field_pos[0] + FIELD_PINS_LEN * width * field_pos[1] + pin_offset
    pins[pix] = 1


def print_game(pins, field_width):
    line = '=============='
    for i in range(len(pins)):
        if (i % (FIELD_PINS_LEN * field_width)) == 0:
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


if __name__ == '__main__':
    master = NeuralNetMaster()
    print('Level:', master.level)
    state = master.__get_game_state__(BoxPusherEngine(master.level))
    print_game(state, master.field_size[0])
