import math
from datetime import datetime

from neat.reporting import BaseReporter

SUMMARIZE_GENS = 10


class TrainingReporter(BaseReporter):
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
