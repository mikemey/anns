import math
import os
import pickle
from datetime import datetime
from typing import List

from .training_configs import TrainingConfig

LOCAL_DIR = os.path.dirname(__file__)
TRAININGS_DIR = os.path.join(LOCAL_DIR, '..', 'best-players')
if not os.path.exists(TRAININGS_DIR):
    os.mkdir(TRAININGS_DIR)


def create_training_file_name():
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    file_name = '{}_best.pd'.format(ts)
    return os.path.join(TRAININGS_DIR, file_name)


class BestPlayerKeep:
    def __init__(self, train_config: TrainingConfig):
        self.file_name = create_training_file_name()
        self.top_list = [PlayerData()] * train_config.keep_best_players
        self.limit = train_config.keep_fitness_threshold
        self.genome_keys = []
        self.min_ix = 0

    def add_population_result(self, population_result):
        if self.__top_list_updated(population_result):
            self.__store_top_list()

    def __top_list_updated(self, population_result):
        updated = False
        for genome, config in filter(lambda result: result[0].fitness >= self.limit, population_result):
            if self.__insert_result(genome, config):
                updated = True
        return updated

    def __insert_result(self, genome, config):
        if genome.fitness < self.top_list[self.min_ix].fitness:
            return False

        existing_ix = self.genome_keys.index(genome.key) if genome.key in self.genome_keys else -1
        if existing_ix >= 0:
            if genome.fitness > self.top_list[existing_ix].fitness:
                self.__replace_position(existing_ix, genome, config)
                return True
            return False

        self.__replace_position(self.min_ix, genome, config)
        return True

    def __replace_position(self, data_ix, genome, config):
        self.top_list[data_ix] = PlayerData(genome, config)
        current_min = math.inf
        for ix, player_data in enumerate(self.top_list):
            if player_data.fitness < current_min:
                self.min_ix = ix
                current_min = player_data.fitness
        self.genome_keys = [data.genome.key for data in self.top_list if data.genome]

    def __store_top_list(self):
        top_players = list(filter(lambda s: s.genome, self.top_list))
        with open(self.file_name, 'wb') as f:
            pickle.dump(top_players, f, protocol=pickle.HIGHEST_PROTOCOL)


class PlayerData:
    def __init__(self, genome=None, config=None, name=None):
        self.genome = genome
        self.name = name
        self.config = config
        self.fitness = genome.fitness if genome else -math.inf


def load_player_data(file_name) -> List[PlayerData]:
    with open(file_name, 'rb') as f:
        player_data = pickle.load(f)
        print('genome file read: {}'.format(file_name))
        return player_data
