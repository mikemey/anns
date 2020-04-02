import math
import os
import pickle
import random
import string
import sys
from datetime import datetime
from signal import signal, SIGINT

import neat
import numpy as np
from neat.reporting import BaseReporter

ALLOWED_LETTERS = string.ascii_lowercase + ' '
CONSIDER_CHARS = 4
PINS_TEMPLATE = [0.0] * CONSIDER_CHARS

ANSWERS = [
    'Hallo Susanne, mein Mäuschen! Ich hab dich lieb! Bussi!',
    'Hallo Madelaine, mein Schätzchen! Ich hab dich soooo viel lieb! Bussi!',
    'Tut mir leid, das versteh\' ich nicht :('
]
fixed_train_data = [
    ('susanne', (1, 0, 0, 0)), ('madelaine', (0, 1, 0, 0)),
    ('exit', (0, 0, 0, 1)), ('', (0, 0, 1, 0))
]


def random_string():
    return ''.join(random.choice(ALLOWED_LETTERS)
                   for _ in range(random.randrange(CONSIDER_CHARS + 1)))


def create_training_set():
    neg_cases = [(random_string(), (0, 0, 1, 0)), (random_string(), (0, 0, 1, 0))]
    # neg_cases = [(random_string(), (0, 0, 1, 0)) for _ in range(10)]
    return [(text_to_pins(t), r) for t, r in fixed_train_data + neg_cases]


MAX_CHAR_VAL = 270


def text_to_pins(text):
    filtered = filter(lambda c: c in ALLOWED_LETTERS, text[:CONSIDER_CHARS])
    # total = 0
    # for char_ix, ch in enumerate(filtered):
    #     char_val = (char_ix * len(ALLOWED_LETTERS)) + (ALLOWED_LETTERS.index(ch) + 1)
    #     total += char_val
    # return [total / MAX_CHAR_VAL]
    pins = PINS_TEMPLATE.copy()
    for ix, ch in enumerate(filtered):
        pins[ix] = (ALLOWED_LETTERS.index(ch) + 1) / len(ALLOWED_LETTERS)
    return pins


default_train_set = create_training_set()


class ChatterBox:
    NET_FILE = 'brain.net'

    @staticmethod
    def from_genome(genome, config):
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        return ChatterBox(net, genome)

    @staticmethod
    def from_fs():
        with open(ChatterBox.NET_FILE, 'rb') as f:
            return ChatterBox(pickle.load(f))

    def __init__(self, net, genome=None):
        self.net = net
        self.genome = genome

    def train(self, training_set, max_fitness):
        self.genome.fitness = max_fitness
        for pins_in, expected_out in training_set:
            actual_output = self.net.activate(pins_in)
            self.genome.fitness -= sum(np.abs(np.array(actual_output) - expected_out)) ** 2

    def chat(self, enable_save=True):
        print("Wie ist dein Name? (beenden mit 'exit')")
        wait_for_input = True
        while wait_for_input:
            in_text = input('>> ', )
            if enable_save and in_text == 'save':
                self.save_net()
                print('net saved.')
                continue
            output = self.net.activate(text_to_pins(in_text.lower()))
            answer_ix = output.index(max(output))
            if answer_ix < 3:
                print(ANSWERS[answer_ix])
            else:
                wait_for_input = False
            if wait_for_input and in_text == 'exit':
                print('SAVE GUARD EXIT')
                wait_for_input = False
        print('\nBussi! Baba!')
        return False

    def save_net(self):
        with open(ChatterBox.NET_FILE, 'wb') as f:
            pickle.dump(self.net, f, protocol=pickle.HIGHEST_PROTOCOL)


class Trainer:
    def __init__(self):
        local_dir = os.path.dirname(__file__)
        config_file = os.path.join(local_dir, 'chatter.cfg')
        self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                  neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                  config_file)
        self.chat_with_fit = [22, 22.5, 23, 23.3]

    def run(self):
        pop = neat.Population(self.config)
        pop.add_reporter(Reporter())
        winner = pop.run(self.eval_genomes, 100000)

        print('\nWinner fitness:', winner.fitness)
        ChatterBox.from_genome(winner, self.config).chat()

    def eval_genomes(self, genomes, config):
        training_set = default_train_set
        max_fitness = config.genome_config.num_outputs * len(training_set)

        best_fit = -math.inf
        best_genome = None
        for genome_id, genome in genomes:
            ChatterBox.from_genome(genome, config).train(training_set, max_fitness)
            if genome.fitness > best_fit:
                best_fit = genome.fitness
                best_genome = genome

        if len(self.chat_with_fit) and best_fit > self.chat_with_fit[0]:
            ChatterBox.from_genome(best_genome, config).chat()
            self.chat_with_fit = self.chat_with_fit[1:]


def keep_max_gen(current_max, new_val, gen):
    if new_val > current_max[0]:
        current_max[0] = new_val
        current_max[1] = gen


class Reporter(BaseReporter):
    def __init__(self):
        self.generations, self.total_fit, self.total_pop = 0, 0, 0
        self.__report__('--- START ---')
        self.max_avg = [-math.inf, 0]
        self.max_fit = [-math.inf, 0]

    def start_generation(self, generation):
        self.generations += 1

    def post_evaluate(self, config, population, species_set, best_genome):
        gen_fitness = [genome.fitness for genome in population.values()]
        gen_fit_sum = sum(gen_fitness)
        gen_count = len(gen_fitness)
        self.total_fit += gen_fit_sum
        self.total_pop += gen_count
        rolling_fit_mean = self.total_fit / self.total_pop

        keep_max_gen(self.max_avg, rolling_fit_mean, self.generations)
        keep_max_gen(self.max_fit, best_genome.fitness, self.generations)
        self.__report__(
            '{:5}:{:2}, avg: {:2.2f} max a/f {:2.2f}[{:4}] / {:2.2f}[{:4}], gen a/b: {:2.2f} ({:2.2f} {:2}-{:2})'.format(
                self.generations, len(species_set.species), rolling_fit_mean,
                self.max_avg[0], self.max_avg[1],
                self.max_fit[0], self.max_fit[1],
                gen_fit_sum / gen_count,
                best_genome.fitness, best_genome.size()[0], best_genome.size()[1]
            ))

    @staticmethod
    def __report__(msg):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print('[{}] {}'.format(ts, msg))


def shutdown(signal_received, frame):
    print('\nexit')
    exit(0)


if __name__ == '__main__':
    signal(SIGINT, shutdown)
    if len(sys.argv) > 1 and sys.argv[1] == 'run':
        ChatterBox.from_fs().chat(False)
    else:
        Trainer().run()

    # for v in create_training_set():
    #     print(v)
    # print('"{}"\t{}'.format(v, text_to_pins(v)))
    # while True:
    #     in_text = input('text: ', )
    #     print(text_to_pins(in_text))
