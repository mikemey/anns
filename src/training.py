import math
import os
from multiprocessing import Pool
from signal import signal, SIGINT

import neat
from neat.population import CompleteExtinctionException

from nn_player import NeuralNetMaster
from training_levels import Level
from training_reporter import TrainingReporter

SHOWCASE_EVERY_GEN = 20
EVAL_PROCESSES = 4


def generate_training_levels():
    return [Level.generate_level() for _ in range(100)]


class Trainer:
    def __init__(self):
        self.reporter = TrainingReporter(SHOWCASE_EVERY_GEN)
        self.pool = None
        signal(SIGINT, self.stop)

    def run(self, config_file):
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                             neat.DefaultSpeciesSet, neat.DefaultStagnation,
                             config_file)
        pop = neat.Population(config)
        pop.add_reporter(self.reporter)
        self.pool = Pool(processes=EVAL_PROCESSES)
        try:
            winner = pop.run(self.eval_population, 100000)
            print('\nWinner fitness:', winner.fitness)
        except ValueError:
            shutdown()
        except CompleteExtinctionException:
            shutdown(msg='Complete extinction')

    def stop(self, signal_received=None, frame=None):
        if self.pool:
            self.pool.close()
            self.pool.join()
            print('process pool closed.')

    def eval_population(self, population_genomes, config: neat.config.Config):
        train_levels = generate_training_levels()
        genome_configs = [(genome, config) for _, genome in population_genomes]
        nn_master = NeuralNetMaster(train_levels)

        pop_fitness = self.pool.starmap(nn_master.eval_genome, genome_configs)
        for (fitness, *pop_stats), (genome, _) in zip(pop_fitness, genome_configs):
            genome.fitness = fitness
            self.reporter.add_pop_game_stats(*pop_stats)

        pop_best, pop_best_genome = -math.inf, None
        for _, genome in population_genomes:
            if genome.fitness > pop_best:
                pop_best = genome.fitness
                pop_best_genome = genome

        self.reporter.run_post_batch(lambda: nn_master.showcase_genome(pop_best_genome, config))
        # if (self.stats.generation % SHOWCASE_EVERY_GEN) == 0:


def shutdown(signal_received=None, frame=None, msg='exit'):
    print('\n{}'.format(msg))
    exit(0)


if __name__ == '__main__':
    signal(SIGINT, shutdown)
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'training.cfg')
    Trainer().run(config_path)
