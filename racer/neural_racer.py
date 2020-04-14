import neat

from game.racer_engine import RacerEngine, PlayerOperation
from game.tracers import get_trace_distances

TRAINING_DT = 1 / 60
NOOP_TIMEOUT_SECS = 2
MIN_SCORE_PER_SECOND = 1
MIN_SPS_OFFSET = 2


class NeuralRacer:
    @staticmethod
    def play_game(genome, config):
        return NeuralRacer(genome, config).get_fitness()

    def __init__(self, genome, config):
        self.engine = RacerEngine()
        self.net = neat.nn.FeedForwardNetwork.create(genome, config)
        self.operations = PlayerOperation()
        self.noop_timeout = NOOP_TIMEOUT_SECS
        self.time = 0
        self.score = 0

    def get_state(self):
        return self.engine.player_state

    def get_fitness(self):
        while not self.engine.game_over:
            self.next_step()
            self.time += TRAINING_DT

        fitness = self.score
        if self.noop_timeout < 0:
            fitness -= 20
        if self.__under_sps_limit():
            fitness -= 10
        return fitness

    def next_step(self):
        state = self.engine.player_state
        distances = get_trace_distances((state.x, state.y), state.rotation)
        output = self.net.activate(distances)
        self.__update_operations(*output)
        self.engine.update(TRAINING_DT, self.operations)
        self.__update_score()
        if self.__under_sps_limit():
            self.engine.game_over = True

    def __update_operations(self, fwd, back, left, right):
        self.operations.stop_all()
        self.noop_timeout -= TRAINING_DT
        if fwd > 0.5 or back > 0.5:
            self.noop_timeout = NOOP_TIMEOUT_SECS
            if fwd > back:
                self.operations.accelerate()
            else:
                self.operations.reverse()
        if left > 0.5 or right > 0.5:
            if left > right:
                self.operations.turn_left()
            else:
                self.operations.turn_right()
        if self.noop_timeout < 0:
            self.engine.game_over = True

    def __update_score(self):
        relevant_speed = self.engine.player_state.relevant_speed
        amp = 0.002 if relevant_speed < 0 else 0.001
        self.score += relevant_speed * amp
        if self.score < 0:
            self.engine.game_over = True

    def __under_sps_limit(self):
        if self.time > MIN_SPS_OFFSET:
            return self.score / self.time < MIN_SCORE_PER_SECOND
        return False


# TODO experiment with normalized inputs:
MIN_DISTANCE = 10
DISTANCE_RANGE = 650


def normalized_distances(self):
    state = self.engine.player_state
    distances = get_trace_distances((state.x, state.y), state.rotation)
    return [(dist - MIN_DISTANCE) / DISTANCE_RANGE for dist in distances]
