import os
from configparser import ConfigParser

import neat

LOCAL_DIR = os.path.dirname(__file__)


def load_configs(file_name='training.cfg'):
    config_path = os.path.join(LOCAL_DIR, file_name)
    print('loading config file: <{}>'.format(os.path.abspath(config_path)))
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    return config, TrainingConfig(config_path)


class TrainingConfig:
    SECTION = 'TRAINING'

    def __init__(self, config_path):
        parameters = ConfigParser()
        with open(config_path, 'r') as f:
            parameters.read_file(f)
        if not parameters.has_section(self.SECTION):
            raise RuntimeError('"{}" section not found in NEAT configuration file.'.format(self.SECTION))

        self.processes = parameters.getint(self.SECTION, 'processes')
        self.keep_best_players = parameters.getint(self.SECTION, 'keep_best_players')
        self.keep_fitness_threshold = parameters.getint(self.SECTION, 'keep_fitness_threshold')
        self.showcase_batch_size = parameters.getint(self.SECTION, 'showcase_every_gen')
        self.showcase_racer_count = parameters.getint(self.SECTION, 'showcase_racer_count')
