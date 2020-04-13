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


class NeuralMaster:
    def __init__(self):
        neat_config, self.training_config = load_configs()
        self.population = neat.Population(neat_config)
        self.reporter = TrainingReporter(self.training_config.showcase_batch_size)
        self.population.add_reporter(self.reporter)

        self.pool = None
        signal(SIGINT, self.stop)
        self.pool = Pool(processes=self.training_config.processes)

    def stop(self, signal_received=None, frame=None):
        if self.pool:
            self.pool.close()
            self.pool.join()
            print('process pool closed.')
            exit(0)

    def run(self):
        try:
            winner = self.population.run(self.eval_population, 100000)
            print('\nWinner fitness:', winner.fitness)
        except ValueError or CompleteExtinctionException:
            self.stop()

    def eval_population(self, population_genomes, config: neat.config.Config):
        # genome_configs = [(genome, config) for _, genome in population_genomes]
        #
        # pop_fitness = self.pool.starmap(NeuralRacer.play_game, genome_configs)
        # for fitness, (genome, _) in zip(pop_fitness, genome_configs):
        #     genome.fitness = fitness
        #
        # pop_best = sorted([g for _, g in population_genomes], key=lambda g: g.fitness)[:4]
        first_ten = [g for _, g in population_genomes][:4]
        ShowcaseController(first_ten, config).showcase()
        # self.reporter.run_post_batch(lambda: controller.showcase_genome(pop_best_genome, config))


# class BestRacers:
#     SIZE = 10
#     def __init__(self):
#         self.racer = [None] * self.SIZE

class ShowcaseController(RaceController):
    DELAY_AUTO_CLOSE_SECS = 3

    def __init__(self, genomes, config):
        super().__init__()
        self.players = [NeuralRacer(genome, config) for genome in genomes]
        self.window = RacerWindow(self)
        self.seconds_to_close = self.DELAY_AUTO_CLOSE_SECS

    def showcase(self):
        self.window.start()

    def get_score_text(self):
        highest_score = max([player.engine.score for player in self.players])
        return 'max: {}'.format(highest_score)

    def update_players(self, dt) -> List[Tuple[float, float, float]]:
        if not self.show_lost_screen:
            self.show_lost_screen = True
            for player in self.players:
                if not player.game_over():
                    self.show_lost_screen = False
                    player.next_step(dt)

        if self.show_lost_screen:
            if self.seconds_to_close == self.DELAY_AUTO_CLOSE_SECS:
                print('all games ended, waiting {} seconds to exit...'.format(self.DELAY_AUTO_CLOSE_SECS))
            self.seconds_to_close -= dt
            if self.seconds_to_close < 0:
                self.window.close()

        return [player.get_position() for player in self.players]

    def get_player_count(self):
        return len(self.players)


class NeuralRacer:
    TRAINING_DT = 1 / 60
    MIN_DISTANCE = 10
    DISTANCE_RANGE = 650
    NOOP_TIMEOUT_SECS = 3

    @staticmethod
    def play_game(genome, config):
        return NeuralRacer(genome, config).get_fitness()

    def __init__(self, genome, config):
        self.engine = RacerEngine()
        self.net = neat.nn.FeedForwardNetwork.create(genome, config)
        self.operations = PlayerOperation()
        self.noop_timeout = self.NOOP_TIMEOUT_SECS

    def get_position(self):
        return self.engine.player.position[0], \
               self.engine.player.position[1], \
               self.engine.player.rotation

    def game_over(self):
        return self.engine.score < 0 or self.engine.game_over or self.noop_timeout < 0

    def get_fitness(self):
        max_fitness = 0
        while not self.game_over():
            self.next_step(self.TRAINING_DT)
            if self.engine.score > max_fitness:
                max_fitness = self.engine.score
        return max_fitness

    def next_step(self, dt):
        distances = get_trace_distances(self.engine.player.position, self.engine.player.rotation)
        output = self.net.activate(distances)
        self.update_operations(dt, *output)
        self.engine.update(dt, self.operations)

    def update_operations(self, dt, fwd, back, left, right):
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


def normalized_distances(self):
    distances = get_trace_distances(self.engine.player.position, self.engine.player.rotation)
    return [(dist - self.MIN_DISTANCE) / self.DISTANCE_RANGE for dist in distances]
