import numpy as np

MEANS = [0.017, 0.017, 0.032]
DEVIATIONS = [0.0005, 0.002, 0.01]
DISTRIBUTION_RATIOS = [0.6, 0.96]

LIMITS_DIGITS = 3
LIMIT_LOW = 0.010
LIMIT_HIGH = 0.060


def random_dt():
    return __random_dt()


def __random_dt(ix=None):
    ix = __pick_ix(ix)
    dt = np.random.normal(MEANS[ix], DEVIATIONS[ix], 1)[0]
    round_dt = np.round(dt, LIMITS_DIGITS)
    if round_dt < LIMIT_LOW:
        return __random_dt(ix)
    if round_dt > LIMIT_HIGH:
        return __random_dt(ix)
    return dt


def __pick_ix(ix=None):
    if ix is None:
        ix = 0
        r = np.random.random()
        for ratio_limit in DISTRIBUTION_RATIOS:
            if r < ratio_limit:
                return ix
            ix += 1
    return ix


# Distribution sample printing:
SAMPLE_SIZE = 5000
INIT_COUNTERS = [0] * len(MEANS)


def __print_training_distribution():
    distribution = {}
    for _ in range(0, SAMPLE_SIZE):
        # ix = 0
        ix = __pick_ix()
        dt = np.round(__random_dt(ix), LIMITS_DIGITS)
        times = distribution.setdefault(dt, INIT_COUNTERS.copy())
        times[ix] += 1
        distribution.update(({dt: times}))

    __print_distribution(distribution)


def __print_distribution_from(file):
    with open(file) as f:
        distribution = {}
        for line in f.readlines():
            dt = round(float(line), 3)
            times = distribution.setdefault(dt, [0])
            times[0] += 1
            distribution.update(({dt: times}))
        __print_distribution(distribution)


DELTA_TIME_STEP = 0.001
DT_FORMAT = '{:.3f}'


# LOG_HEADER = 'time\t' + '\t'.join(['dist_{}'.format(i + 1) for i in range(len(MEANS))]) + '\ttotal'
# DT_LOG = DT_FORMAT + '\t{}' * (len(MEANS) + 1)
# EMPTY_DT_LOG = DT_FORMAT + '\t0' * (len(MEANS) + 1)


def __create_table_templates(distribution):
    distribution_width = len(list(distribution.values())[0])
    header = 'time\t' + '\t'.join(['dist_{}'.format(i + 1) for i in range(distribution_width)]) + '\ttotal'
    distribution_and_total_width = distribution_width + 1
    log_line = DT_FORMAT + '\t{}' * distribution_and_total_width
    empty_log = DT_FORMAT + '\t0' * distribution_and_total_width
    return header, log_line, empty_log


def __print_distribution(distribution):
    header, dt_log_line, empty_dt_log = __create_table_templates(distribution)
    print(header)
    total_count = 0
    last_time = LIMIT_LOW
    sorted_dist = sorted(list(distribution.items()))
    for key, counters in sorted_dist:
        curr_time = float(key)
        if curr_time > LIMIT_HIGH:
            continue
        while curr_time > last_time:
            print(empty_dt_log.format(last_time))
            last_time += DELTA_TIME_STEP
        time_counts = sum(counters)
        total_count += time_counts
        print(dt_log_line.format(key, *counters, time_counts))
        last_time += DELTA_TIME_STEP

    while last_time <= LIMIT_HIGH + DELTA_TIME_STEP:
        print(empty_dt_log.format(last_time))
        last_time += DELTA_TIME_STEP
    print('Total count:', total_count)


if __name__ == '__main__':
    __print_training_distribution()
    # __print_distribution_from('real-dts.txt')
