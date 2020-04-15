import numpy as np

MEANS = [0.0168, 0.025, 0.037]
DEVIATIONS = [0.0006, [0.01, 0.02], 0.003]
DISTRIBUTION_RATIOS = [0.72, 0.87]
PICK_DIST_0_RATIO = 0.7
PICK_DIST_1_RATIO = 0.85

HARD_LIMIT_DIGITS = 3
HARD_LIMIT_LOW = 0.010
HARD_LIMIT_HIGH = 0.060


def random_dt():
    return __random_dt()


def __random_dt(ix=None):
    ix = __pick_ix(ix)
    dt = np.random.normal(MEANS[ix], DEVIATIONS[ix], 1)[0]
    round_dt = np.round(dt, HARD_LIMIT_DIGITS)
    if round_dt < HARD_LIMIT_LOW:
        return __random_dt(ix)
    if round_dt > HARD_LIMIT_HIGH:
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
SAMPLE_SIZE = 1000
DELTA_TIME_STEP = 0.001

DT_FORMAT = '{:.3f}'
LOG_HEADER = 'time\tdist_1\tdist_2\tdist_3\ttotal'
DT_LOG = DT_FORMAT + '\t{}\t{}\t{}\t{}'
EMPTY_DT_LOG = DT_FORMAT + '\t0\t0\t0\t0'


def __print_dts_distribution():
    distribution = {}
    for _ in range(0, SAMPLE_SIZE):
        ix = __pick_ix()
        dt = np.round(__random_dt(ix), HARD_LIMIT_DIGITS)
        times = distribution.setdefault(dt, [0, 0, 0])
        times[ix] += 1
        distribution.update(({dt: times}))

    print(LOG_HEADER)
    last_time = HARD_LIMIT_LOW
    sorted_dist = sorted(list(distribution.items()))
    for key, [dist_1, dist_2, dist_3] in sorted_dist:
        curr_time = float(key)
        while curr_time > last_time:
            print(EMPTY_DT_LOG.format(last_time))
            last_time += DELTA_TIME_STEP
        print(DT_LOG.format(key, dist_1, dist_2, dist_3, sum((dist_1, dist_2, dist_3))))
        last_time += DELTA_TIME_STEP

    while last_time <= HARD_LIMIT_HIGH + DELTA_TIME_STEP:
        print(EMPTY_DT_LOG.format(last_time))
        last_time += DELTA_TIME_STEP


if __name__ == '__main__':
    __print_dts_distribution()

# Recorded delta-times to replicate:
# 0.009	1
# 0.010	1
# 0.011	0
# 0.012	0
# 0.013	1
# 0.014	3
# 0.015	5
# 0.016	67
# 0.017	84
# 0.018	16
# 0.019	6
# 0.020	2
# 0.021	2
# 0.023	2
# 0.024	3
# 0.025	1
# 0.026	1
# 0.027	1
# 0.028	1
# 0.029	1
# 0.030	0
# 0.031	4
# 0.032	1
# 0.033	3
# 0.034	3
# 0.035	2
# 0.036	4
# 0.037	7
# 0.038	2
# 0.039	4
# 0.04	1
