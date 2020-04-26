import random
import traceback
from multiprocessing import Pool
from signal import signal, SIGINT
from typing import List

import neat

from game.racer_engine import PlayerState
from game.racer_window import RaceController, RacerWindow
from game.tracks import Level, Trainings, SHOWCASE_FROM_FILE_LEVEL
from neural.best_player_keep import BestPlayerKeep, PlayerData, load_player_data
from neural.neural_player import NeuralPlayer
from neural.training_configs import load_configs
from neural.training_dts import LIMIT_HIGH
from neural.training_reporter import TrainingReporter

DT_IGNORE_LIMIT = LIMIT_HIGH
LEVEL_COUNT_FMT = '[{:>10}]: {:5}'

class NeuralMaster:
    def __init__(self):
        self.neat_config, self.training_config = load_configs()
        self.reporter = TrainingReporter(self.training_config.showcase_batch_size)
        self.best_keep = BestPlayerKeep(self.training_config)
        self.trainings = Trainings()

        self.pool = None
        signal(SIGINT, self.stop)
        self.pool = Pool(processes=self.training_config.processes)

    def train(self):
        population = neat.Population(self.neat_config)
        population.add_reporter(self.reporter)
        try:
            population.run(self.eval_population)
        except Exception as ex:
            print('Training error:', ex)
            traceback.print_tb(ex.__traceback__)
        finally:
            self.stop()

    def stop(self, signal_received=None, frame=None):
        if self.pool:
            self.pool.close()
            self.pool.join()
            self.pool = None
            print('process pool closed.')
            exit(0)

    def eval_population(self, key_genome_tuples, config: neat.config.Config):
        genomes = list(zip(*key_genome_tuples))[1]
        for genome in genomes:
            genome.fitness = 0

        remaining_genomes = list(genomes)
        level_ix = 0
        passing_counts = ['Levels played:']
        while len(remaining_genomes) and level_ix < self.trainings.count:
            level, limit = self.trainings.get(level_ix)
            passing_counts.append(LEVEL_COUNT_FMT.format(level.name, len(remaining_genomes)))
            remaining_genomes = self.evaluate_genomes_passing(remaining_genomes, config, level, limit)
            level_ix += 1

        print(' '.join(passing_counts))
        self.best_keep.add_population_result([(genome, config) for genome in genomes])
        self.reporter.run_post_batch(self.showcase_best(genomes, config, level_ix))

    def evaluate_genomes_passing(self, genomes, config, level, limit):
        passing_genomes = []
        eval_params = [(genome, config, level, limit) for genome in genomes]
        eval_result = self.pool.starmap(NeuralPlayer.evaluate_genome, eval_params)

        for fitness, genome in zip(eval_result, genomes):
            genome.fitness += fitness
            if fitness >= limit:
                passing_genomes.append(genome)
        return passing_genomes

    def showcase_best(self, genomes, config, level_limit):
        def showcase():
            sorted_genomes = sorted(genomes, key=lambda gen: gen.fitness, reverse=True)
            top_players = [PlayerData(genome, config)
                           for genome in sorted_genomes[:self.training_config.showcase_racer_count]]
            for level_ix in range(level_limit):
                level, limit = self.trainings.get(level_ix)
                self.showcase(top_players, level, limit=limit)

        return showcase

    def showcase_from_files(self, player_files, select_random=False):
        players = [player_data for pl_file in player_files for player_data in load_player_data(pl_file)]
        if select_random:
            random.shuffle(players)
        else:
            players = sorted(players, key=lambda data: data.fitness, reverse=True)
        players = players[:self.training_config.showcase_racer_count]
        self.showcase(players, SHOWCASE_FROM_FILE_LEVEL, auto_close=False)

    def showcase(self, players: List[PlayerData], level, limit=None, auto_close=True):
        fitness_log = ['{:.0f} (#{})'.format(data.fitness, data.genome.key) for data in players]
        print('Showcase: {} players, fitness (key): {}'.format(len(players), ', '.join(fitness_log)))
        try:
            ShowcaseController(players, self.pool, level, limit, auto_close).showcase()
            print('Showcases finished, waiting {} seconds to exit...'.format(ShowcaseController.DELAY_AUTO_CLOSE_SECS))
        except Exception as e:
            if str(e) == 'list index out of range':
                print('Showcase error: no screen available')
            else:
                print('Showcase error:', e)
                traceback.print_tb(e.__traceback__)


class ShowcaseController(RaceController):
    DELAY_AUTO_CLOSE_SECS = 3

    def __init__(self, players: List[PlayerData], pool: Pool, level: Level, limit: int, auto_close: bool):
        super().__init__(level)
        self.__neural_player = [NeuralPlayer(data.genome, data.config, level, limit, name=data.name)
                                for data in players]
        self.__pool = pool
        self.window = RacerWindow(self, show_fps=True)
        self.auto_close = auto_close
        self.seconds_to_close = self.DELAY_AUTO_CLOSE_SECS
        self.closing = False

    def showcase(self):
        self.window.start()

    def get_score_text(self):
        highest_score = max([player.score for player in self.__neural_player])
        return 'max: {:.0f}'.format(highest_score)

    def get_ranking(self):
        ranking = sorted(enumerate(self.__neural_player), key=lambda pl: pl[1].score, reverse=True)
        names, scores = '#  name\n────────────\n', 'score\n\n'
        for ix, player in ranking:
            names += '{}  {}\n'.format(ix + 1, player.name)
            scores += '{:.0f}\n'.format(player.score)
        return names, scores

    def update_player_states(self, dt):
        if self.closing or dt > DT_IGNORE_LIMIT:
            return

        if self.show_end_screen and self.auto_close:
            self.seconds_to_close -= dt
            if self.seconds_to_close < 0:
                self.window.close()
                self.closing = True
        else:
            pool_params = [(player, dt) for player in self.__neural_player]
            self.__neural_player = self.__pool.starmap(update_player_state, pool_params)
            self.show_end_screen = all([player.engine.game_over for player in self.__neural_player])

    def get_player_states(self) -> List[PlayerState]:
        return [player.get_state() for player in self.__neural_player]

    def get_player_count(self):
        return len(self.__neural_player)

    def get_end_text(self):
        if self.auto_close:
            return '', 'waiting {} seconds to exit...'.format(self.DELAY_AUTO_CLOSE_SECS), ''
        else:
            return '', ''


def update_player_state(player, dt):
    if not player.engine.game_over:
        player.next_step(dt)
    return player
