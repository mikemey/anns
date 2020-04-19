from multiprocessing import Pool
from signal import signal, SIGINT
from typing import List

import neat

from best_player_keep import BestPlayerKeep, PlayerData, load_player_data
from game.racer_engine import PlayerState
from game.racer_window import RaceController, RacerWindow
from neural_player import NeuralPlayer
from training_configs import load_configs
from training_dts import LIMIT_HIGH
from training_reporter import TrainingReporter

DT_IGNORE_LIMIT = LIMIT_HIGH


class NeuralMaster:
    def __init__(self):
        self.neat_config, self.training_config = load_configs()
        self.reporter = TrainingReporter(self.training_config.showcase_batch_size)
        self.best_keep = BestPlayerKeep(self.training_config)

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
        genome_configs = [(genome, config, self.training_config) for genome in genomes]
        eval_result = self.pool.starmap(NeuralPlayer.evaluate_genome, genome_configs)

        pop_result = []
        for (fitness, *game_stats), genome in zip(eval_result, genomes):
            genome.fitness = fitness
            pop_result.append((genome, config, *game_stats))
        self.best_keep.add_population_result(pop_result)

        def showcase_best():
            sorted_results = sorted(pop_result, key=lambda result: result[0].fitness, reverse=True)
            top_results = sorted_results[:self.training_config.showcase_racer_count]
            self.showcase([PlayerData(*result) for result in top_results])

        self.reporter.run_post_batch(showcase_best)

    def showcase_from_files(self, player_files):
        players = [data for file in player_files for data in load_player_data(file)]
        unique_keys, unique_players = [], []
        for player in sorted(players, key=lambda data: data.genome.fitness, reverse=True):
            if player.genome.key not in unique_keys:
                unique_keys.append(player.genome.key)
                unique_players.append(player)
        self.showcase(unique_players[:self.training_config.showcase_racer_count])

    def showcase(self, players: List[PlayerData]):
        fitness_sps_log = ['{:.0f}/{:.1f}'.format(data.genome.fitness, data.score_per_second) for data in players]
        print('Showcase: {} players (fit/sps) {}'.format(len(players), ', '.join(fitness_sps_log)))
        try:
            ShowcaseController(players, self.pool).showcase()
            print('Showcases finished, waiting {} seconds to exit...'.format(ShowcaseController.DELAY_AUTO_CLOSE_SECS))
        except Exception as e:
            msg = 'no screen available' if str(e) == 'list index out of range' else e
            print('Showcase error:', msg)


class ShowcaseController(RaceController):
    DELAY_AUTO_CLOSE_SECS = 3

    def __init__(self, players: List[PlayerData], pool):
        super().__init__()
        self.__neural_player = [NeuralPlayer(data.genome, data.config) for data in players]
        self.__pool = pool

        self.window = RacerWindow(self, show_traces=False, show_fps=True)
        self.seconds_to_close = self.DELAY_AUTO_CLOSE_SECS
        self.closing = False

    def showcase(self):
        self.window.start()

    def get_score_text(self):
        highest_score = max([player.score for player in self.__neural_player])
        return 'max: {:.0f}'.format(highest_score)

    def get_ranking(self):
        ranking = sorted(self.__neural_player, key=lambda pl: pl.score, reverse=True)
        names = scores = ''
        for player in ranking:
            names += '{}\n'.format(player.name)
            scores += '{:.0f}\n'.format(player.score)
        return names, scores

    def update_player_states(self, dt):
        if self.closing or dt > DT_IGNORE_LIMIT:
            return

        if self.show_end_screen:
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
        return '', 'waiting {} seconds to exit...'.format(self.DELAY_AUTO_CLOSE_SECS), ''


def update_player_state(player, dt):
    if not player.engine.game_over:
        player.next_step(dt)
    return player
