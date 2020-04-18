import math
import os
import pickle
from datetime import datetime
from typing import List

from training_configs import TrainingConfig

LOCAL_DIR = os.path.dirname(__file__)
TRAININGS_DIR = os.path.join(LOCAL_DIR, 'player_store')
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
        self.min_ix = 0
        self.limit = train_config.game_limit

    def add_population_result(self, population_result):
        top_list_updated = self.__update_top_list(population_result)
        if top_list_updated:
            self.__store_player_data()

    def __update_top_list(self, population_result):
        updated = False
        for eval_result in filter(lambda result: result[0].fitness >= self.limit, population_result):
            if self.__insert_result(*eval_result):
                updated = True
        return updated

    def __insert_result(self, genome, config, score_per_second):
        if score_per_second < self.top_list[self.min_ix].score_per_second:
            return False

        self.top_list[self.min_ix] = PlayerData(genome, config, score_per_second)
        current_min = math.inf
        for ix, player_data in enumerate(self.top_list):
            if player_data.score_per_second < current_min:
                self.min_ix = ix
                current_min = player_data.score_per_second
        return True

    def __store_player_data(self):
        top_players = list(filter(lambda s: s.genome, self.top_list))
        with open(self.file_name, 'wb') as f:
            pickle.dump(top_players, f, protocol=pickle.HIGHEST_PROTOCOL)


class PlayerData:
    def __init__(self, genome=None, config=None, score_per_second=None):
        self.genome = genome
        self.config = config
        self.score_per_second = score_per_second or -math.inf


def load_player_data(file_name) -> List[PlayerData]:
    with open(file_name, 'rb') as f:
        player_data = pickle.load(f)
        print('genome file read: {}'.format(file_name))
        return player_data
