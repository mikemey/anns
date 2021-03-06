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
from neat.population import CompleteExtinctionException
from neat.reporting import BaseReporter

ALLOWED_LETTERS = string.ascii_lowercase + ' '
CONSIDER_CHARS = 3
NET_FILE_SUFFIX = '.net'

ANSWERS = [
    'Hallo Susanne, mein Mäuschen! Ich hab dich lieb! Bussi!\n',
    'Hallo Madelaine, mein Schätzchen! Ich hab dich soooo viel lieb! Bussi!\n',
    'Tut mir leid, das versteh\' ich nicht :(\n'
]
fixed_train_data = [
    ('susanne', (1, 0, 0, 0)), ('madelaine', (0, 1, 0, 0)),
    ('exit', (0, 0, 0, 1)), ('', (0, 0, 1, 0)), ('bla', (0, 0, 1, 0))
]


def random_string():
    return ''.join(random.choice(ALLOWED_LETTERS)
                   for _ in range(random.randrange(CONSIDER_CHARS + 1)))


def create_training_set():
    neg_cases = [(random_string(), (0, 0, 1, 0)), (random_string(), (0, 0, 1, 0))]
    return [(text_to_pins(t), r) for t, r in fixed_train_data + neg_cases] * 5


def text_to_pins(text):
    filtered = filter(lambda c: c in ALLOWED_LETTERS, text.lower()[:CONSIDER_CHARS])
    total = 0
    for char_ix, ch in enumerate(filtered):
        char_val = (char_ix * len(ALLOWED_LETTERS)) + (ALLOWED_LETTERS.index(ch) + 1)
        total += char_val
    return [1 if total & (1 << n) else 0 for n in range(8)]


def get_net_file(name):
    return name if name.endswith(NET_FILE_SUFFIX) else name + '.net'


class ChatterBox:
    SAVE_CMD = 'save '

    @staticmethod
    def from_genome(genome, config):
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        return ChatterBox(net, genome)

    @staticmethod
    def from_fs(name):
        with open(get_net_file(name), 'rb') as f:
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
        print("Wer bist du? (beenden mit 'exit')")
        wait_for_input = True
        while wait_for_input:
            in_text = input('>> ', )
            if enable_save and in_text.startswith(ChatterBox.SAVE_CMD):
                name_param = in_text[len(ChatterBox.SAVE_CMD):]
                file_name = get_net_file(name_param)
                self.save_net(file_name)
                print('net saved:', file_name)
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

    def save_net(self, name):
        with open(get_net_file(name), 'wb') as f:
            pickle.dump(self.net, f, protocol=pickle.HIGHEST_PROTOCOL)


class Trainer:
    def __init__(self):
        local_dir = os.path.dirname(__file__)
        config_file = os.path.join(local_dir, 'chatter.cfg')
        self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                  neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                  config_file)
        self.training_set = create_training_set()
        gen_config = self.config.genome_config
        self.max_fitness = gen_config.num_outputs * len(self.training_set)
        if self.max_fitness != self.config.fitness_threshold:
            shutdown(msg='Config fitness_threshold != max-fitnesse: {} != {}'.format(
                self.config.fitness_threshold, self.max_fitness
            ))

        ts_input_len = len(self.training_set[0][0])
        if ts_input_len != gen_config.num_inputs:
            shutdown(msg='Training set input length not matching input-nodes: {} != {}'.format(
                ts_input_len, gen_config.num_inputs
            ))

        print('Maximum fitness:', self.max_fitness)
        self.chat_percentiles = [0.96, 0.98, 0.99, 0.995]

    def run(self):
        pop = neat.Population(self.config)
        pop.add_reporter(Reporter())
        try:
            winner = pop.run(self.eval_genomes, 100000)
            print('\nWinner fitness:', winner.fitness)
            ChatterBox.from_genome(winner, self.config).chat()
        except CompleteExtinctionException:
            shutdown(msg='Complete extinction')

    def eval_genomes(self, genomes, config):
        self.training_set = create_training_set()
        max_fitness = config.genome_config.num_outputs * len(self.training_set)

        best_fit = -math.inf
        best_genome = None
        for genome_id, genome in genomes:
            ChatterBox.from_genome(genome, config).train(self.training_set, max_fitness)
            if genome.fitness > best_fit:
                best_fit = genome.fitness
                best_genome = genome

        if len(self.chat_percentiles):
            demo_fitness = self.chat_percentiles[0] * max_fitness
            if best_fit > demo_fitness:
                print('\nDEMO chat percent {}, fitness: {:2.2f}'.format(self.chat_percentiles[0], best_fit))
                ChatterBox.from_genome(best_genome, config).chat()
                self.chat_percentiles = self.chat_percentiles[1:]


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


def shutdown(signal_received=None, frame=None, msg='exit'):
    print('\n', msg)
    exit(0)


if __name__ == '__main__':
    signal(SIGINT, shutdown)
    if len(sys.argv) == 3 and sys.argv[1] == 'run':
        ChatterBox.from_fs(sys.argv[2]).chat(False)
    else:
        Trainer().run()
