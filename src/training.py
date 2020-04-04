import math
import os
from signal import signal, SIGINT

import neat
from neat.population import CompleteExtinctionException

from nn_player import NeuralNetMaster
from training_levels import Level
from training_reporter import TrainingReporter

SHOWCASE_EVERY_GEN = 100


def generate_training_levels():
    return [Level.generate_level() for _ in range(10)]


class Trainer:
    def __init__(self):
        self.gen_count = 0

    def run(self, config_file):
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                             neat.DefaultSpeciesSet, neat.DefaultStagnation,
                             config_file)
        pop = neat.Population(config)
        pop.add_reporter(TrainingReporter())
        try:
            winner = pop.run(self.eval_genomes, 100000)
            print('\nWinner fitness:', winner.fitness)
        except CompleteExtinctionException:
            shutdown(msg='Complete extinction')

    def eval_genomes(self, genomes, config: neat.config.Config):
        nn_master = NeuralNetMaster(generate_training_levels())
        batch_best, batch_best_genome = -math.inf, None
        for _, genome in genomes:
            nn_master.eval_genome(genome, config)
            if genome.fitness > batch_best:
                batch_best = genome.fitness
                batch_best_genome = genome

        self.gen_count += 1
        if (self.gen_count % SHOWCASE_EVERY_GEN) == 0:
            print('Showcase generation:', self.gen_count)
            nn_master.showcase_genome(batch_best_genome, config)


def shutdown(signal_received=None, frame=None, msg='exit'):
    print('\n{}'.format(msg))
    exit(0)


if __name__ == '__main__':
    signal(SIGINT, shutdown)
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'training.cfg')
    Trainer().run(config_path)
