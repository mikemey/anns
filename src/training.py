import math
import os

import neat

from nn_player import NeuralNetMaster

SHOWCASE_EVERY_GEN = 1000


class Trainer:
    def __init__(self):
        self.gen_count = 0

    def run(self, config_file):
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                             neat.DefaultSpeciesSet, neat.DefaultStagnation,
                             config_file)
        pop = neat.Population(config)
        pop.add_reporter(neat.StdOutReporter(False))
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
