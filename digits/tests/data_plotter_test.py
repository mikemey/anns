import time
import unittest

import numpy as np

from data_plotter import DataPlotter


@unittest.skip('only run manually')
class DataPlotTestCase(unittest.TestCase):
    @staticmethod
    def test_live_plot():
        plotter = DataPlotter('step', 'v1', 'v2')
        step = 0
        print()
        while step < 10:
            v1 = np.round(np.random.random() * 10, 1)
            v2 = np.round(np.random.random() * 12, 1)
            print(f'new points ({step:5d}: {v1} ++ {v2})')
            plotter.add_data(step, v1, v2)
            step += 1
            time.sleep(1.2)

    def test_reject_one_dim_data(self):
        pass
