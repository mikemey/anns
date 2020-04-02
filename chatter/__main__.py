import os
import random
import string
from datetime import datetime
from signal import signal, SIGINT

import neat
from neat.reporting import BaseReporter

ALLOWED_LETTERS = string.ascii_lowercase + ' '
CONSIDER_CHARS = 5
PINS_TEMPLATE = [0.0]

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
    neg_cases = [(random_string(), (0, 0, 1, 0)) for _ in range(CONSIDER_CHARS)]
    return [(text_to_pins(t), r) for t, r in fixed_train_data + neg_cases]


def text_to_pins(text):
    pins = PINS_TEMPLATE.copy()
    filtered = filter(lambda c: c in ALLOWED_LETTERS, text[:CONSIDER_CHARS])
    for ix, ch in enumerate(filtered):
        pins[ix] = (ALLOWED_LETTERS.index(ch) + 1) / len(ALLOWED_LETTERS)
    return pins


default_train_set = []
for _ in range(25):
    default_train_set += create_training_set()


class ChatterBox:
    def __init__(self, genome, config):
        self.net = neat.nn.FeedForwardNetwork.create(genome, config)
        self.genome = genome

    def train(self, training_set):
        self.genome.fitness = len(PINS_TEMPLATE) * len(training_set)
        for pins_in, expected_out in training_set:
            actual_output = self.net.activate(pins_in)
            for actual_pin, expected_pin in zip(actual_output, expected_out):
                self.genome.fitness -= (actual_pin - expected_pin) ** 2

    def chat(self):
        print("Wie ist dein Name? (beenden mit 'exit')")
        wait_for_questions = True
        while wait_for_questions:
            in_text = input('>> ', )
            output = self.net.activate(text_to_pins(in_text.lower()))
            answer_ix = output.index(max(output))
            if answer_ix < 3:
                print(ANSWERS[answer_ix])
            else:
                shutdown(None, None)


def run(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    pop = neat.Population(config)
    pop.add_reporter(Reporter())
    winner = pop.run(eval_genomes, 100000)

    print('\nWinner fitness:', winner.fitness)
    config.save('winner.genome')
    ChatterBox(winner, config).chat()


def eval_genomes(genomes, config):
    # training_set = create_training_set()
    for genome_id, genome in genomes:
        ChatterBox(genome, config).train(default_train_set)


class Reporter(BaseReporter):
    def __init__(self):
        self.generations, self.total_fit, self.total_pop = 0, 0, 0
        self.__report__('--- START ---')

    def start_generation(self, generation):
        self.generations += 1

    def post_evaluate(self, config, population, species_set, best_genome):
        gen_fitness = [genome.fitness for genome in population.values()]
        gen_sum = sum(gen_fitness)
        gen_count = len(gen_fitness)
        self.total_fit += gen_sum
        self.total_pop += gen_count
        rolling_fit_mean = self.total_fit / self.total_pop
        self.__report__('{:5} gens, {:2} spc, avg tot/gen {:1.2f} / {:1.2f}, best: {:1.2f} {}'.format(
            self.generations, len(species_set.species),
            rolling_fit_mean, gen_sum / gen_count,
            best_genome.fitness, best_genome.size())
        )

    @staticmethod
    def __report__(msg):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print('[{}] {}'.format(ts, msg))


def shutdown(signal_received, frame):
    print('\nBussi! Baba!')
    exit(0)


if __name__ == '__main__':
    signal(SIGINT, shutdown)
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'chatter.cfg')
    run(config_path)
    # for tr in create_training_set():
    #     print(tr)
    while True:
        in_text = input('text: ', )
        print(text_to_pins(in_text))
