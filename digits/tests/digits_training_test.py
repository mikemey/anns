import os
import unittest

import numpy as np
import tensorflow as tf

import digits_training as dt

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '5'
TEST_TRAINING_DATA = f'{os.path.dirname(__file__)}/test_data/digits.csv'


class TrainingTestCase(unittest.TestCase):
    def test_build_model(self):
        model = dt.build_model()
        self.assertTrue(model._is_compiled, 'model not compiled')

        first_layer = model.layers[0]
        self.assertEqual([(None, 784)], first_layer.input_shape)

        final_layer = model.layers[-1]
        self.assertEqual((None, 10), final_layer.output_shape)
        self.assertEqual(tf.nn.softmax, final_layer.activation)

    # Test trainings-data:
    #   label,pixel0,pixel1,pixel2
    #   1,99,0,255
    #   0,98,0,255
    #   4,97,0,255
    #   9,96,0,255
    def test_trainings_data(self):
        input_ds, target_ds = dt.get_trainings_data(TEST_TRAINING_DATA)

        self.assertEqual((4, 3), input_ds.shape)
        self.__assert_data_vals(input_ds.values, [
            [99, 0, 255], [98, 0, 255], [97, 0, 255], [96, 0, 255]
        ])

        self.assertEqual((4, 10), target_ds.shape)
        self.__assert_data_vals(target_ds, [
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        ])

    def __assert_data_vals(self, data, expected_data):
        eq_matrix = tf.math.equal(expected_data, data)
        self.assertTrue(np.all(eq_matrix), 'data mismatch')
