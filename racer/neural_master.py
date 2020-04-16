import math
import os
from configparser import ConfigParser
from multiprocessing import Pool
from signal import signal, SIGINT
from typing import List

import neat

from game.racer_engine import PlayerState
from game.racer_window import RaceController, RacerWindow
from neural_player import NeuralPlayer
from training_reporter import TrainingReporter

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
        self.showcase_batch_size = parameters.getint(self.SECTION, 'showcase_every_gen')
        self.showcase_racer_count = parameters.getint(self.SECTION, 'showcase_racer_count')


class NeuralMaster:
    def __init__(self):
        self.neat_config, self.training_config = load_configs()
        self.population = neat.Population(self.neat_config)
        self.reporter = TrainingReporter(self.training_config.showcase_batch_size)
        self.population.add_reporter(self.reporter)
        self.best_racers = []

        self.pool = None
        signal(SIGINT, self.stop)
        self.pool = Pool(processes=self.training_config.processes)

    def run(self):
        try:
            winner = self.population.run(self.eval_population, 100000)
            print('\nWinner fitness:', winner.fitness)
            ShowcaseController(winner, self.neat_config, self.pool).showcase()
        except Exception as ex:
            print('Training error:', ex)
        finally:
            self.stop()

    def stop(self, signal_received=None, frame=None):
        if self.pool:
            self.pool.close()
            self.pool.join()
            self.pool = None
            print('process pool closed.')
            exit(0)

    def eval_population(self, key_genomes, config: neat.config.Config):
        separated_tup = list(zip(*key_genomes))
        genomes = list(separated_tup[1])
        genome_configs = [(genome, config) for genome in genomes]
        pop_fitness = self.pool.starmap(NeuralPlayer.play_game, genome_configs)

        for fitness, genome in zip(pop_fitness, genomes):
            genome.fitness = fitness

        def showcase_best():
            racer = sorted(genomes, key=lambda gen: gen.fitness, reverse=True)[:self.training_config.showcase_racer_count]
            print('Showcase racer fitness:', [math.floor(r.fitness) for r in racer])
            try:
                ShowcaseController(racer, config, self.pool).showcase()
            except Exception as e:
                msg = 'no screen available' if str(e) == 'list index out of range' else e
                print('Showcase error:', msg)

        self.reporter.run_post_batch(showcase_best)


class ShowcaseController(RaceController):
    DELAY_AUTO_CLOSE_SECS = 3

    def __init__(self, genomes, config, pool):
        super().__init__()
        self.__neural_racer = [NeuralPlayer(genome, config) for genome in genomes]
        self.__pool = pool

        self.window = RacerWindow(self, show_traces=False, show_fps=True)
        self.seconds_to_close = self.DELAY_AUTO_CLOSE_SECS
        self.closing = False

    def showcase(self):
        self.window.start()

    def get_score_text(self):
        highest_score = max([racer.score for racer in self.__neural_racer])
        return 'max: {:.0f}'.format(highest_score)

    def update_player_states(self, dt):
        if self.closing:
            return

        if self.show_end_screen:
            if self.seconds_to_close == self.DELAY_AUTO_CLOSE_SECS:
                print('Showcases finished, waiting {} seconds to exit...'.format(self.DELAY_AUTO_CLOSE_SECS))
            self.seconds_to_close -= dt
            if self.seconds_to_close < 0:
                self.window.close()
                self.closing = True
        else:
            pool_params = [(racer, dt) for racer in self.__neural_racer]
            self.__neural_racer = self.__pool.starmap(update_player_state, pool_params)
            self.show_end_screen = all([racer.engine.game_over for racer in self.__neural_racer])

    def get_player_states(self) -> List[PlayerState]:
        return [racer.get_state() for racer in self.__neural_racer]

    def get_player_count(self):
        return len(self.__neural_racer)

    def get_end_text(self):
        return '', 'waiting {} seconds to exit...'.format(self.DELAY_AUTO_CLOSE_SECS), ''

    # TODO add stats text on screen


def update_player_state(racer, dt):
    if not racer.engine.game_over:
        racer.next_step(dt)
    return racer
