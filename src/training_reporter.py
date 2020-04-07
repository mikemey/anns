import math
from datetime import datetime

from neat.reporting import BaseReporter

FITNESS_FORMAT = '{:5.1f}'
POP_GAME_STATS_TEMPLATE = 'g:[{:5}], bm: {:6,}, w/l: {:6,} / {:6,}'
TRAINING_STATS_TEMPLATE = \
    ' ───  p/s: {{}}/{{:2}}, avg: {0} max a/f: {0}[{{:4}}] / {0}[{{:4}}], gen a/b: {0} / {0} ({{:2}}-{{:2}})'.format(FITNESS_FORMAT)
BATCH_GAME_STATS_TEMPLATE = '_' * 50 + '▏batch bm: {:8,}, w/l: {:7,} / {:7,}'


class TrainingReporter(BaseReporter):
    def __init__(self, batch_size):
        self.batch_size = batch_size

        self.generations = self.total_fit = self.total_pop = 0
        self.pop_stats = GameStats()
        self.batch_stats = GameStats()
        self.max_avg = [-math.inf, 0]
        self.max_fit = [-math.inf, 0]
        self.post_batch_hook = None
        self.__report__('--- START ---')

    def add_pop_game_stats(self, *game_stats):
        self.pop_stats.add(*game_stats)
        self.batch_stats.add(*game_stats)

    def start_generation(self, generation):
        self.generations += 1

    def complete_extinction(self):
        self.__report__('--------------------')
        self.__report__('Complete extinction!')

    def post_evaluate(self, config, population, species_set, best_genome):
        pop_fitness = [genome.fitness for genome in population.values()]
        pop_fit_sum = sum(pop_fitness)
        pop_count = len(pop_fitness)

        self.total_fit += pop_fit_sum
        self.total_pop += pop_count
        rolling_fit_mean = self.total_fit / self.total_pop

        self.keep_max_gen(self.max_avg, rolling_fit_mean, self.generations)
        self.keep_max_gen(self.max_fit, best_genome.fitness, self.generations)

        self.__dump_pop_game_stats__()
        print(TRAINING_STATS_TEMPLATE.format(
            pop_count, len(species_set.species), rolling_fit_mean,
            self.max_avg[0], self.max_avg[1],
            self.max_fit[0], self.max_fit[1],
            pop_fit_sum / pop_count,
            best_genome.fitness, best_genome.size()[0], best_genome.size()[1]
        ))
        if (self.generations % self.batch_size) == 0:
            self.__dump_batch_game_stats__()
            if self.post_batch_hook:
                self.post_batch_hook()

    def __dump_pop_game_stats__(self):
        self.__report__(POP_GAME_STATS_TEMPLATE.format(
            self.generations, self.pop_stats.box_moves, self.pop_stats.wins, self.pop_stats.lost
        ))
        self.pop_stats = GameStats()

    def __dump_batch_game_stats__(self):
        print(BATCH_GAME_STATS_TEMPLATE.format(
            self.batch_stats.box_moves, self.batch_stats.wins, self.batch_stats.lost
        ))
        self.batch_stats = GameStats()

    def run_post_batch(self, post_batch_hook):
        self.post_batch_hook = post_batch_hook

    @staticmethod
    def __report__(msg):
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print('[{}] {}'.format(ts, msg))

    @staticmethod
    def keep_max_gen(current_max, new_val, gen):
        if new_val > current_max[0]:
            current_max[0] = new_val
            current_max[1] = gen


class GameStats:
    def __init__(self):
        self.box_moves = self.goals = self.wins = self.lost = 0

    def add(self, box_moves, goals, wins, lost):
        self.box_moves += box_moves
        self.goals += goals
        self.wins += wins
        self.lost += lost
