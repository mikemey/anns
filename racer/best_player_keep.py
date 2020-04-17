import math
import os
import pickle
from datetime import datetime

from training_configs import TrainingConfig

LOCAL_DIR = os.path.dirname(__file__)
TRAININGS_DIR = os.path.join(LOCAL_DIR, 'player_store')
if not os.path.exists(TRAININGS_DIR):
    os.mkdir(TRAININGS_DIR)


class BestPlayerKeep:
    def __init__(self, neat_config, train_config: TrainingConfig):
        self.config = neat_config
        self.file_name = create_training_file_name()
        self.top_list = [PlayerStats()] * train_config.keep_best_players
        self.min_ix = 0
        self.limit = train_config.game_limit

    def add_population_result(self, population_result):
        top_list_updated = self.__update_top_list(population_result)
        if top_list_updated:
            self.__store_top_list()

    def __update_top_list(self, population_result):
        updated = False
        for eval_result in filter(lambda result: result[0].fitness >= self.limit, population_result):
            if self.__insert_result(*eval_result):
                updated = True
        return updated

    def __insert_result(self, genome, score_per_second):
        if score_per_second < self.top_list[self.min_ix].score_per_second:
            return False

        self.top_list[self.min_ix] = PlayerStats(genome, score_per_second)
        current_min = math.inf
        for ix, stats in enumerate(self.top_list):
            if stats.score_per_second < current_min:
                self.min_ix = ix
                current_min = stats.score_per_second
        return True

    def __store_top_list(self):
        top_stats = list(filter(lambda s: s.genome, self.top_list))
        store_format = self.config, *[stats.genome for stats in top_stats]
        with open(self.file_name, 'wb') as f:
            pickle.dump(store_format, f, protocol=pickle.HIGHEST_PROTOCOL)


class PlayerStats:
    def __init__(self, genome=None, score_per_second=None):
        self.genome = genome
        self.score_per_second = score_per_second or -math.inf


def load_top_list(file_name):
    print('loading genome file: <{}>'.format(file_name))
    with open(file_name, 'rb') as f:
        config, *genomes = pickle.load(f)
        return config, genomes


def create_training_file_name():
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    file_name = '{}_best.genomes'.format(ts)
    return os.path.join(TRAININGS_DIR, file_name)
