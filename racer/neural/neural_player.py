from signal import signal, SIGINT

import neat

from game.racer_engine import RacerEngine, PlayerOperation
from game.tracers import TracerLines
from .training_dts import random_dt

MIN_SCORE_PER_SECOND = 20
MIN_SPS_OFFSET = 3

SCORE_CHECK_TIME = 2
SCORE_CHECK_DIFF = 4

UPDATE_FREQUENCY = 0.1


class NeuralPlayer:
    STOPPING = False

    @staticmethod
    def sigint_received(signal_received=None, frame=None):
        NeuralPlayer.STOPPING = True

    @staticmethod
    def evaluate_genome(genome, neat_config, level, limit):
        if NeuralPlayer.STOPPING:
            return 0

        signal(SIGINT, NeuralPlayer.sigint_received)
        return NeuralPlayer(genome, neat_config, level, limit).__evaluate()

    def __init__(self, genome, config, level, limit, name=None):
        self.name = name if name else '{}'.format(genome.key)
        self.engine = RacerEngine(level)
        self.tracers = TracerLines(level)
        self.net = neat.nn.FeedForwardNetwork.create(genome, config)
        self.operations = PlayerOperation()
        self.check_time = self.time = 0
        self.score = 0
        self.score_limit = limit
        self.score_history = ScoreHistory()

    def get_state(self):
        return self.engine.player_state

    def __evaluate(self):
        while not (self.engine.game_over or NeuralPlayer.STOPPING):
            dt = random_dt()
            self.next_step(dt)
        fitness = self.score
        if self.__under_sps_limit():
            fitness /= 2
        return round(fitness)

    def next_step(self, dt):
        self.time += dt
        self.check_time += dt
        if self.check_time > UPDATE_FREQUENCY:
            self.check_time -= UPDATE_FREQUENCY
            state = self.engine.player_state
            # net_input = self.tracers.get_trace_distances((state.x, state.y), state.rotation)
            net_input = [dt] + self.tracers.get_trace_distances((state.x, state.y), state.rotation)
            net_output = self.net.activate(net_input)
            self.__update_operations(*net_output)

        self.engine.update(dt, self.operations)
        self.score = self.engine.player_state.distance // 10

        if not self.score_history.changed_score(dt, self.score):
            self.score *= 0.75
            self.engine.game_over = True

        if self.__under_sps_limit() or self.__score_out_of_bounds():
            self.engine.game_over = True

    def __update_operations(self, acc_break, right_left):
        self.operations.stop_all()
        if acc_break > 0.5:
            self.operations.accelerate()
        if acc_break < -0.5:
            self.operations.reverse()
        if right_left > 0.5:
            self.operations.turn_right()
        if right_left < -0.5:
            self.operations.turn_left()

    def __score_out_of_bounds(self):
        return self.score < 0 or \
               (self.score_limit and self.score >= self.score_limit)

    def __get_score_per_second(self):
        return self.score / self.time

    def __under_sps_limit(self):
        if self.time > MIN_SPS_OFFSET:
            return self.__get_score_per_second() < MIN_SCORE_PER_SECOND
        return False


class ScoreHistory:
    def __init__(self):
        self.time = 0
        self.prev_score = 0

    def changed_score(self, dt, score):
        self.time += dt
        if self.time > SCORE_CHECK_TIME:
            self.time -= SCORE_CHECK_TIME
            if abs(score - self.prev_score) < SCORE_CHECK_DIFF:
                return False
            self.prev_score = score
        return True
