import math
from datetime import datetime

from neat.reporting import BaseReporter

LOG_TEMPLATE = '{{:5}}:{{:2}}, avg: {0} max a/f {0}[{{:4}}] / {0}[{{:4}}], gen a/b: {0} ({0} {{:2}}-{{:2}})'


class TrainingReporter(BaseReporter):
    def __init__(self, fitness_log_format="{:4.0f}"):
        self.generations, self.total_fit, self.total_pop = 0, 0, 0
        self.__report__('--- START ---')
        self.max_avg = [-math.inf, 0]
        self.max_fit = [-math.inf, 0]
        self.log_format = LOG_TEMPLATE.format(fitness_log_format)

    def start_generation(self, generation):
        self.generations += 1

    def post_evaluate(self, config, population, species_set, best_genome):
        gen_fitness = [genome.fitness for genome in population.values()]
        gen_fit_sum = sum(gen_fitness)
        gen_count = len(gen_fitness)

        self.total_fit += gen_fit_sum
        self.total_pop += gen_count
        rolling_fit_mean = self.total_fit / self.total_pop

        self.keep_max_gen(self.max_avg, rolling_fit_mean, self.generations)
        self.keep_max_gen(self.max_fit, best_genome.fitness, self.generations)
        self.__report__(self.log_format.format(
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

    @staticmethod
    def keep_max_gen(current_max, new_val, gen):
        if new_val > current_max[0]:
            current_max[0] = new_val
            current_max[1] = gen
