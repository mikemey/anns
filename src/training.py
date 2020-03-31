import math
import os
from statistics import mean

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
        self.gens_collected = 0
        self.batch_fitness = []
        self.batch_best = -math.inf
        self.batch_best_size = None

    def start_generation(self, generation):
        self.gens_collected += 1

    def post_evaluate(self, config, population, species_set, best_genome):
        gen_fitness = [genome.fitness for genome in population.values()]
        self.batch_fitness.extend(gen_fitness)

        if self.batch_best < best_genome.fitness:
            self.batch_best = best_genome.fitness
            self.batch_best_size = best_genome.size()

        if (self.gens_collected % SUMMARIZE_GENS) == 0:
            fit_mean = mean(self.batch_fitness)
            print('[{:5}] {:4} / {:2}  --  avg/best  {:4.0f} / {:4.0f}  {}'.format(
                self.gens_collected, len(population), len(species_set.species),
                fit_mean, self.batch_best, self.batch_best_size)
            )

            self.batch_fitness = []
            self.batch_best = -math.inf


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
