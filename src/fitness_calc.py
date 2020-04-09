from game_engine import BoxPusherEngine, GameListener
from training_levels import Level, distance_between, distance_sum_between


def get_axis_neighbours(goal_coord, box_coord):
    box_goal_diff = goal_coord - box_coord
    if box_goal_diff == 0:
        return None
    if box_goal_diff < 0:
        return box_coord + 1, box_coord - 1
    else:
        return box_coord - 1, box_coord + 1


def create_fitness_calculator(engine, level, verbose=False):
    return StepFitnessCalculator(engine, verbose)


class FitnessCalculator(GameListener):
    def __init__(self, engine: BoxPusherEngine, start_score, verbose):
        super().__init__()
        self.engine = engine
        self.engine.listeners.add(self)
        self.verbose = verbose
        self.score = start_score
        self.__log__('-- start --')
        self.box_moves = 0
        self.box_in_goals = 0

    def __log__(self, *data):
        if self.verbose:
            print('score: {:8.2f}'.format(self.score), *data)

    def new_position(self, pos):
        self.__log__('new pos:', pos)

    def box_move(self):
        self.box_moves += 1
        self.__log__('box move')

    def box_in_goal(self):
        self.box_in_goals += 1
        self.__log__('box in goal')

    def invalid_move(self):
        self.__log__('invalid move')

    def get_fitness(self):
        return self.score


class StepFitnessCalculator(FitnessCalculator):
    def __init__(self, engine: BoxPusherEngine, verbose):
        super().__init__(engine, 0, verbose)
        self.last_distances = self.__position_distances__()
        self.covered_positions = CoveredPositions()

    def __position_distances__(self):
        return (
            distance_between(self.engine.player, self.engine.boxes[0]),
            distance_sum_between(self.engine.boxes, self.engine.goal)
        )

    def __pref_pos_distances__(self):
        push_positions = []
        box_goal_positions = []
        for box in self.engine.boxes:
            x_n = get_axis_neighbours(self.engine.goal[0], box[0])
            y_n = get_axis_neighbours(self.engine.goal[1], box[1])
            if x_n is None:
                push_positions.append((box[0], y_n[0]))
                box_goal_positions.append((box[0], y_n[1]))
            else:
                push_positions.append((x_n[0], box[1]))
                box_goal_positions.append((x_n[1], box[1]))
            if y_n is None:
                push_positions.append((x_n[1], box[1]))
                box_goal_positions.append((x_n[1], box[1]))
            else:
                push_positions.append((box[0], y_n[0]))
                box_goal_positions.append((box[0], y_n[1]))
        return (
            [distance_between(pos, self.engine.player) for pos in push_positions],
            [distance_between(pos, self.engine.goal) for pos in box_goal_positions]
        )

    def new_position(self, pos):
        covered_count = self.covered_positions.count_on(pos)
        if covered_count > 0:
            self.score -= 0.6 * covered_count
            self.__log__('fields covered:', covered_count)

        if len(self.engine.boxes) > 0:
            new_distances = self.__position_distances__()
            player_closer = self.last_distances[0] - new_distances[0]
            if player_closer != 0:
                amp = 2 if player_closer > 0 else 3
                self.score += player_closer * amp
                self.__log__('player closer:', player_closer)
            box_closer = self.last_distances[1] - new_distances[1]
            if box_closer != 0:
                amp = 3 if box_closer > 0 else 5
                self.score += box_closer * amp
                self.__log__('box closer:', box_closer)
            self.last_distances = new_distances

        super().new_position(pos)

    @staticmethod
    def closer_to_positions(last_distances, new_distances):
        diffs = [last - current for last, current in zip(last_distances, new_distances)]
        if all([diff == 0 for diff in diffs]):
            return 0
        if any([diff > 0 for diff in diffs]):
            return 1
        return -1

    def box_move(self):
        self.score += 1
        super().box_move()

    def box_in_goal(self):
        self.score += 5
        super().box_in_goal()

    def invalid_move(self):
        self.score -= 0.2
        super().invalid_move()

    def get_fitness(self):
        if self.engine.game_won:
            self.score += 50
            self.__log__('winning bonus')
        if self.box_moves > 0:
            self.score += 3
            self.__log__('box moved bonus')
        return self.score


class DistanceFitnessCalculator(FitnessCalculator):
    def __init__(self, engine: BoxPusherEngine, level: Level, verbose):
        super().__init__(engine, level.max_points, verbose)
        self.covered_positions = CoveredPositions()
        self.level_box_error = self.__current_box_error_to__(self.engine.goal)
        self.level_player_error = self.__current_box_error_to__(self.engine.player)

    def __current_box_error_to__(self, pos):
        return distance_sum_between(self.engine.boxes, pos)

    def new_position(self, pos):
        super().new_position(pos)
        self.score -= 1
        covered_count = self.covered_positions.count_on(pos)
        if covered_count > 0:
            self.score -= 2 * covered_count
            self.__log__('field covered')

    def box_move(self):
        self.score += 20
        super().box_move()

    def box_in_goal(self):
        self.score += 50
        super().box_in_goal()

    def invalid_move(self):
        self.score -= 10
        super().invalid_move()

    def get_fitness(self):
        box_error = self.__get_box_error__(self.engine.goal, self.level_box_error)
        player_error = self.__get_box_error__(self.engine.player, self.level_player_error)
        self.__log__('box    error:', box_error, 100)
        self.__log__('player error:', player_error, 10)

        self.score += 100 if self.engine.game_won else 0
        return self.score - box_error - player_error

    def __get_box_error__(self, pos, level_error, potential=50):
        error_ratio = self.__current_box_error_to__(pos) / level_error
        return potential * error_ratio ** 2


class CoveredPositions:
    def __init__(self):
        self.covered_positions = []

    def count_on(self, pos):
        count = 0
        for p in self.covered_positions:
            if (p == pos).all():
                count += 1
        self.covered_positions.append(pos.copy())
        return count
