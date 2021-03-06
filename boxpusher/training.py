import math
import os
import pickle
import sys
from datetime import datetime
from multiprocessing import Pool
from signal import signal, SIGINT

import neat
from neat.population import CompleteExtinctionException

from nn_player import NeuralNetMaster
from training_reporter import TrainingReporter

SHOWCASE_EVERY_GEN = 20
EVAL_PROCESSES = 4
RECORD_BEST_AFTER_GEN = 100
LOCAL_DIR = os.path.dirname(__file__)
TRAININGS_DIR = os.path.join(LOCAL_DIR, 'trainings')


class Trainer:
    def __init__(self, population: neat.Population = None):
        self.population = population if population is not None else neat.Population(load_config())
        self.reporter = TrainingReporter(self.population.config, SHOWCASE_EVERY_GEN)
        self.population.add_reporter(self.reporter)
        self.best_fitness = -math.inf
        self.eval_counter = 0

        self.pool = None
        signal(SIGINT, self.stop)
        self.pool = Pool(processes=EVAL_PROCESSES)

    def run(self):
        try:
            winner = self.population.run(self.eval_population, 100000)
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
        self.eval_counter += 1
        genome_configs = [(genome, config) for _, genome in population_genomes]
        nn_master = NeuralNetMaster()

        pop_fitness = self.pool.starmap(nn_master.eval_genome, genome_configs)
        for (fitness, *pop_stats), (genome, _) in zip(pop_fitness, genome_configs):
            genome.fitness = fitness
            self.reporter.add_pop_game_stats(*pop_stats)

        pop_best, pop_best_genome = -math.inf, None
        for _, genome in population_genomes:
            if genome.fitness > pop_best:
                pop_best = genome.fitness
                pop_best_genome = genome

        if pop_best > self.best_fitness:
            self.best_fitness = pop_best
            if self.eval_counter > RECORD_BEST_AFTER_GEN:
                self.reporter.clear_post_batch_hook()
                store_training(self.population, config, pop_best)

        self.reporter.run_post_batch(lambda: nn_master.showcase_genome(pop_best_genome, config))


def shutdown(signal_received=None, frame=None, msg='exit'):
    print('\n{}'.format(msg))
    exit(0)


def store_training(population: neat.Population, config: neat.Config, best_fitness):
    training_state = config, population.population, population.species, population.generation
    file_name = create_training_file_name(population.generation + 1, best_fitness)
    print('storing training file: <{}>'.format(file_name))
    with open(file_name, 'wb') as f:
        pickle.dump(training_state, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_config(file_name='training.cfg'):
    print('loading config file: <{}>'.format(file_name))
    config_path = os.path.join(LOCAL_DIR, file_name)
    with open(config_path, 'r') as f:
        print(f.read())
    return neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                       neat.DefaultSpeciesSet, neat.DefaultStagnation,
                       config_path)


def load_training(file_name):
    print('loading training file: <{}>'.format(file_name))
    with open(file_name, 'rb') as f:
        config, *population_state = pickle.load(f)
        pop = neat.Population(config, population_state)
        return pop


def create_training_file_name(generation, fitness):
    if not os.path.exists(TRAININGS_DIR):
        os.mkdir(TRAININGS_DIR)
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    file_name = '{}_gen_{}_fit_{:.0f}.pop'.format(ts, generation, fitness)
    return os.path.join(TRAININGS_DIR, file_name)


if __name__ == '__main__':
    signal(SIGINT, shutdown)
    training = load_training(sys.argv[1]) if len(sys.argv) > 1 else None
    Trainer(training).run()
