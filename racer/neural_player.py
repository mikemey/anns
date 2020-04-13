import math
import os
from configparser import ConfigParser
from multiprocessing import Pool
from signal import signal, SIGINT
from typing import Tuple, List

import neat
from neat import CompleteExtinctionException

from game.racer_engine import RacerEngine, PlayerOperation
from game.racer_window import RaceController, RacerWindow
from game.tracers import get_trace_distances
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
    DELAY_AUTO_CLOSE_SECS = 5

    def __init__(self, genomes, config):
        super().__init__()
        self.players = [NeuralRacer(genome, config) for genome in genomes]
        self.window = RacerWindow(self, False)
        self.seconds_to_close = self.DELAY_AUTO_CLOSE_SECS

    def showcase(self):
        self.window.start()

    def get_score_text(self):
        highest_score = max([player.score for player in self.players])
        return 'max: {:.0f}'.format(highest_score)

    def update_players(self, dt) -> List[Tuple[float, float, float]]:
        if not self.show_lost_screen:
            all_lost = True
            for player in self.players:
                if not player.game_over():
                    all_lost = False
                    player.next_step(dt)
            self.show_lost_screen = all_lost

        if self.show_lost_screen:
            if self.seconds_to_close == self.DELAY_AUTO_CLOSE_SECS:
                print('showcases finished, waiting {} seconds to exit...'.format(self.DELAY_AUTO_CLOSE_SECS))
            self.seconds_to_close -= dt
            if self.seconds_to_close < 0:
                self.window.close()

        return [player.get_position() for player in self.players]

    def get_player_count(self):
        return len(self.players)


class NeuralRacer:
    TRAINING_DT = 1 / 60
    NOOP_TIMEOUT_SECS = 2
    MIN_SCORE_PER_SECOND = 1
    MIN_SPS_OFFSET = 2

    @staticmethod
    def play_game(genome, config):
        return NeuralRacer(genome, config).get_fitness()

    def __init__(self, genome, config):
        self.engine = RacerEngine()
        self.net = neat.nn.FeedForwardNetwork.create(genome, config)
        self.operations = PlayerOperation()
        self.noop_timeout = self.NOOP_TIMEOUT_SECS
        self.time = 0
        self.score = 0

    def get_position(self):
        return self.engine.player.position[0], \
               self.engine.player.position[1], \
               self.engine.player.rotation

    def game_over(self):
        return self.score < 0 \
               or self.engine.game_over \
               or self.noop_timeout < 0 \
               or self.__under_score_per_seconds_limit()

    def get_fitness(self):
        while not self.game_over():
            self.next_step(self.TRAINING_DT)
            self.time += self.TRAINING_DT

        fitness = self.score
        if self.noop_timeout < 0:
            fitness -= 20
        if self.__under_score_per_seconds_limit():
            fitness -= 10
        return fitness

    def next_step(self, dt):
        distances = get_trace_distances(self.engine.player.position, self.engine.player.rotation)
        output = self.net.activate(distances)
        self.__update_operations(dt, *output)
        self.engine.update(dt, self.operations)
        self.__update_score()

    def __update_operations(self, dt, fwd, back, left, right):
        self.operations.stop_all()
        self.noop_timeout -= dt
        if fwd > 0.5 or back > 0.5:
            self.noop_timeout = self.NOOP_TIMEOUT_SECS
            if fwd > back:
                self.operations.accelerate()
            else:
                self.operations.reverse()
        if left > 0.5 or right > 0.5:
            if left > right:
                self.operations.turn_left()
            else:
                self.operations.turn_right()

    def __update_score(self):
        relevant_speed = self.engine.player.relevant_speed
        amp = 0.002 if relevant_speed < 0 else 0.001
        self.score += relevant_speed * amp

    def __under_score_per_seconds_limit(self):
        if self.time > self.MIN_SPS_OFFSET:
            return self.score / self.time < self.MIN_SCORE_PER_SECOND
        return False


MIN_DISTANCE = 10
DISTANCE_RANGE = 650


def normalized_distances(self):
    distances = get_trace_distances(self.engine.player.position, self.engine.player.rotation)
    return [(dist - MIN_DISTANCE) / DISTANCE_RANGE for dist in distances]
