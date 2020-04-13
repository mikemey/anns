import math
from datetime import datetime

import neat

FITNESS_FORMAT = '{:5f}'
TRAINING_STATS_TEMPLATE = 'g:[{{:5}}], p/s: {{}}/{{:2}}, avg: {0} max a/f: {0}[{{:4}}] / {0}[{{:4}}], ' \
                          'gen a/b: {0} / {0} ({{:2}}-{{:2}})'.format(FITNESS_FORMAT)
BATCH_STATS_TEMPLATE = '_' * 50 + '▏total distance: {:8,}'


class TrainingReporter(neat.reporting.BaseReporter):
    def __init__(self, batch_size):
        self.batch_size = batch_size
        self.generations = self.total_fit = self.total_pop = self.batch_fit = 0
        self.max_avg = [-math.inf, 0]
        self.max_fit = [-math.inf, 0]
        self.post_batch_hook = None
        self.__report__('--- START ---')

    def start_generation(self, generation):
        self.generations = generation + 1

    def complete_extinction(self):
        self.__report__('--------------------')
        self.__report__('Complete extinction!')

    def post_evaluate(self, config, population, species_set, best_genome):
        pop_fitness = [genome.fitness for genome in population.values()]
        pop_fit_sum = sum(pop_fitness)
        pop_count = len(pop_fitness)

        self.total_fit += pop_fit_sum
        self.batch_fit += pop_fit_sum
        self.total_pop += pop_count
        rolling_fit_mean = self.total_fit / self.total_pop

        self.keep_max_gen(self.max_avg, rolling_fit_mean, self.generations)
        self.keep_max_gen(self.max_fit, best_genome.fitness, self.generations)

        print(TRAINING_STATS_TEMPLATE.format(
            self.generations, pop_count, len(species_set.species), rolling_fit_mean,
            self.max_avg[0], self.max_avg[1],
            self.max_fit[0], self.max_fit[1],
            pop_fit_sum / pop_count,
            best_genome.fitness, best_genome.size()[0], best_genome.size()[1]
        ))
        if (self.generations % self.batch_size) == 0:
            self.__dump_batch_stats__()
            if self.post_batch_hook:
                self.post_batch_hook()

    def __dump_batch_stats__(self):
        print(BATCH_STATS_TEMPLATE.format(self.batch_fit))
        self.batch_fit = 0

    def run_post_batch(self, post_batch_hook):
        self.post_batch_hook = post_batch_hook

    def clear_post_batch_hook(self):
        self.post_batch_hook = None

    @staticmethod
    def __report__(msg):
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print('[{}] {}'.format(ts, msg))

    @staticmethod
    def keep_max_gen(current_max, new_val, gen):
        if new_val > current_max[0]:
            current_max[0] = new_val
            current_max[1] = gen
