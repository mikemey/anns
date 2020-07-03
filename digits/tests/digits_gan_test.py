import os
import unittest

import numpy as np
import tensorflow as tf

import digits_gan as gan

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '5'

TEST_TRAINING_DATA = os.path.join(os.path.dirname(__file__), 'test_data', 'all_pixels.csv')


class TrainingTestCase(unittest.TestCase):
    def test_create_discriminator_batches(self):
        np.random.seed(34)

        batch_size = 5
        gan_training = gan.DigitsGanTraining(TEST_TRAINING_DATA, batch_size)
        img_data, rf_ind, labels = gan_training.create_discriminator_batches()
        self.assertEqual((batch_size * 2, 28, 28, 1), img_data.shape)

        real_pixels_col0 = img_data[:batch_size, 0, 0]
        self.__assert_matrix([[0], [0.2], [0.4], [0.6], [0.8]], real_pixels_col0)
        self.__assert_matrix([1, 1, 1, 1, 1, 0, 0, 0, 0, 0], rf_ind)

        expected_labels = [0, 7, 0, 0, 4, 5, 2, 9, 8, 6]
        self.__assert_matrix(tf.keras.utils.to_categorical(expected_labels, 10), labels)

    def __assert_matrix(self, expected, actual):
        eq_matrix = tf.math.equal(expected, actual)
        self.assertTrue(np.all(eq_matrix), f'\tExpected:\n{expected}\n\tActual:\n{actual}')

    def test_build_generator(self):
        model = gan.build_generator()

        noise_input = model.layers[0]
        label_input = model.layers[1]
        self.assertEqual([(None, 200)], noise_input.input_shape)
        self.assertEqual([(None, 10)], label_input.input_shape)

        gen_img_output = model.layers[-1]
        self.assertEqual((None, 28, 28, 1), gen_img_output.output_shape)
        self.assertEqual(tf.nn.sigmoid, gen_img_output.activation)

    def test_build_discriminator(self):
        model = gan.build_discriminator()

        first_layer = model.layers[0]
        self.assertEqual([(None, 28, 28, 1)], first_layer.input_shape)

        rf_ind_layer = model.layers[-2]
        label_layer = model.layers[-1]

        self.assertEqual((None, 1), rf_ind_layer.output_shape)
        self.assertEqual(tf.nn.sigmoid, rf_ind_layer.activation)
        self.assertEqual((None, 10), label_layer.output_shape)
        self.assertEqual(tf.nn.softmax, label_layer.activation)
