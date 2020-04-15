import math
import os
from configparser import ConfigParser
from multiprocessing import Pool
from signal import signal, SIGINT
from typing import List

import neat
from neat import CompleteExtinctionException

from game.racer_engine import PlayerState
from game.racer_window import RaceController, RacerWindow
from neural_racer import NeuralRacer
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
        neat_config, self.training_config = load_configs()
        self.population = neat.Population(neat_config)
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
        except ValueError or CompleteExtinctionException as ex:
            print(ex)
        finally:
            self.stop()

    def stop(self, signal_received=None, frame=None):
        if self.pool:
            self.pool.close()
            self.pool.join()
            print('process pool closed.')
            exit(0)

    def eval_population(self, key_genomes, config: neat.config.Config):
        separated_tup = list(zip(*key_genomes))
        genomes = list(separated_tup[1])
        genome_configs = [(genome, config) for genome in genomes]
        pop_fitness = self.pool.starmap(NeuralRacer.play_game, genome_configs)

        for fitness, genome in zip(pop_fitness, genomes):
            genome.fitness = fitness

        def showcase_best():
            racer = sorted(genomes, key=lambda gen: gen.fitness, reverse=True)[:self.training_config.showcase_racer_count]
            print('Showcase racer fitness:', [math.floor(r.fitness) for r in racer])
            ShowcaseController(racer, config).showcase()

        self.reporter.run_post_batch(showcase_best)


class ShowcaseController(RaceController):
    DELAY_AUTO_CLOSE_SECS = 3

    def __init__(self, genomes, config):
        super().__init__()
        self.neural_racer = [NeuralRacer(genome, config) for genome in genomes]
        self.window = RacerWindow(self, show_traces=False)
        self.seconds_to_close = self.DELAY_AUTO_CLOSE_SECS

    def showcase(self):
        self.window.start()

    def get_score_text(self):
        highest_score = max([racer.score for racer in self.neural_racer])
        return 'max: {:.0f}'.format(highest_score)

    # TODO use NeuralMaster.pool to distribute player updates
    def update_player_states(self, dt):
        if not self.show_end_screen:
            all_lost = True
            for racer in self.neural_racer:
                if not racer.engine.game_over:
                    all_lost = False
                    racer.next_step(dt)
            self.show_end_screen = all_lost

        if self.show_end_screen:
            if self.seconds_to_close == self.DELAY_AUTO_CLOSE_SECS:
                print('Showcases finished, waiting {} seconds to exit...'.format(self.DELAY_AUTO_CLOSE_SECS))
            self.seconds_to_close -= dt
            if self.seconds_to_close < 0:
                self.window.close()

    def get_player_states(self) -> List[PlayerState]:
        return [racer.get_state() for racer in self.neural_racer]

    def get_player_count(self):
        return len(self.neural_racer)

    def get_end_text(self):
        return '', 'waiting {} seconds to exit...'.format(self.DELAY_AUTO_CLOSE_SECS), ''

    # TODO add stats text on screen
