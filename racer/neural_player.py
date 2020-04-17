from signal import signal, SIGINT

import neat

from game.racer_engine import RacerEngine, PlayerOperation
from game.tracers import get_trace_distances
from training_dts import random_dt

MIN_SCORE_PER_SECOND = 20
MIN_SPS_OFFSET = 3


class NeuralPlayer:
    STOPPING = False

    @staticmethod
    def sigint_received(signal_received=None, frame=None):
        NeuralPlayer.STOPPING = True

    @staticmethod
    def play_game(genome, config):
        if NeuralPlayer.STOPPING:
            return 0

        signal(SIGINT, NeuralPlayer.sigint_received)
        return NeuralPlayer(genome, config, config.fitness_threshold * 1.5).get_fitness()

    def __init__(self, genome, config, limit=None):
        self.engine = RacerEngine()
        self.net = neat.nn.FeedForwardNetwork.create(genome, config)
        self.operations = PlayerOperation()
        self.time = 0
        self.score = 0
        self.limit = limit

    def get_state(self):
        return self.engine.player_state

    def get_fitness(self):
        while not (self.engine.game_over or NeuralPlayer.STOPPING):
            dt = random_dt()
            self.next_step(dt)
        fitness = self.score
        if self.__under_sps_limit():
            fitness -= 10
        return fitness

    def next_step(self, dt):
        self.time += dt
        state = self.engine.player_state
        net_input = [dt] + get_trace_distances((state.x, state.y), state.rotation)
        net_output = self.net.activate(net_input)

        self.__update_operations(*net_output)
        self.engine.update(dt, self.operations)
        self.__update_score()
        if self.__under_sps_limit():
            self.engine.game_over = True

    def __update_operations(self, fwd, back, left, right):
        self.operations.stop_all()
        if fwd > 0.5 or back > 0.5:
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
        self.score = self.engine.player_state.distance // 10
        if self.score < 0:
            self.engine.game_over = True
        if self.limit and self.score >= self.limit:
            self.engine.game_over = True

    def __under_sps_limit(self):
        if self.time > MIN_SPS_OFFSET:
            return self.score / self.time < MIN_SCORE_PER_SECOND
        return False
