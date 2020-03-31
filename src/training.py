import math
import os
from datetime import datetime

import neat
from neat.reporting import BaseReporter

from nn_player import NeuralNetMaster

SHOWCASE_EVERY_GEN = 1000
SUMMARIZE_GENS = 10


class Trainer:
    def __init__(self):
        self.gen_count = 0

    def run(self, config_file):
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                             neat.DefaultSpeciesSet, neat.DefaultStagnation,
                             config_file)
        pop = neat.Population(config)
        pop.add_reporter(BPReporter())
        winner = pop.run(self.eval_genomes, 100000)
        print('\nWinner fitness:', winner.fitness)

    def eval_genomes(self, genomes, config: neat.config.Config):
        nn_master = NeuralNetMaster()

        self.gen_count += 1
        if (self.gen_count % SHOWCASE_EVERY_GEN) == 0:
            nn_master.level.print()
            eval_generation_and_showcase_winner(nn_master, genomes, config)
        else:
            eval_generation(nn_master, genomes, config)


class BPReporter(BaseReporter):
    def __init__(self):
        self.generations = 0
        self.total_fit = 0
        self.total_pop = 0

        self.batch_fit, self.batch_pop, self.batch_best, self.batch_best_size \
            = self.__reset_batch__()
        self.__report__('--- START ---')

    def start_generation(self, generation):
        self.generations += 1

    def __reset_batch__(self):
        self.batch_fit = 0
        self.batch_pop = 0
        self.batch_best = -math.inf
        self.batch_best_size = None
        return self.batch_fit, self.batch_pop, self.batch_best, self.batch_best_size

    def post_evaluate(self, config, population, species_set, best_genome):
        gen_fitness = [genome.fitness for genome in population.values()]
        self.batch_fit += sum(gen_fitness)
        self.batch_pop += len(gen_fitness)

        if self.batch_best < best_genome.fitness:
            self.batch_best = best_genome.fitness
            self.batch_best_size = best_genome.size()

        if (self.generations % SUMMARIZE_GENS) == 0:
            self.total_fit += self.batch_fit
            self.total_pop += self.batch_pop

            rolling_fit_mean = self.total_fit / self.total_pop
            batch_fit_mean = self.batch_fit / self.batch_pop
            self.__report__('{:5} gens, {:2} spc, avg r/b {:4.0f}/{:4.0f}, best: {:4.0f} {}'.format(
                self.generations, len(species_set.species),
                rolling_fit_mean, batch_fit_mean,
                self.batch_best, self.batch_best_size)
            )
            self.__reset_batch__()

    @staticmethod
    def __report__(msg):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print('[{}] {}'.format(ts, msg))


def eval_generation(nn_master, genomes, config):
    for genome_id, genome in genomes:
        nn_master.eval_genome(genome, config)


def eval_generation_and_showcase_winner(nn_master, genomes, config):
    best, best_genome = -math.inf, None
    for genome_id, genome in genomes:
        nn_master.eval_genome(genome, config)
        if genome.fitness > best:
            best = genome.fitness
            best_genome = genome
    nn_master.showcase_genome(best_genome, config)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'training.cfg')
    Trainer().run(config_path)
