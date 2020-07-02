import os
import unittest

import numpy as np
import tensorflow as tf

import digits_gan as gan

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '5'

TEST_TRAINING_DATA = os.path.join(os.path.dirname(__file__), 'test_data', 'all_pixels.csv')


class TrainingTestCase(unittest.TestCase):
    # Test trainings-data:
    #   label,pixel0,...
    #   1,0,...
    #   0,0,...
    #   1,102,...
    #   4,0,...
    #   0,204,...
    #   0,153,...
    #   7,0,...
    #   3,51,...
    #   5,0,...
    def test_create_discriminator_batches(self):
        np.random.seed(0)
        gan_training = gan.DigitsGanTraining(TEST_TRAINING_DATA, 5)
        real_imgs, gen_imgs = gan_training.create_discriminator_batches()
        self.assertEqual((5, 784), gen_imgs.shape)
        self.assertEqual((5, 784), real_imgs.shape)

        eq_matrix = tf.math.equal([0, 0.2, 0.4, 0.6, 0.8], real_imgs['pixel0'].values)
        self.assertTrue(np.all(eq_matrix), eq_matrix)

    def test_build_generator(self):
        model = gan.build_generator()

        first_layer = model.layers[0]
        self.assertEqual([(None, 200)], first_layer.input_shape)

        final_layer = model.layers[-1]
        self.assertEqual((None, 784), final_layer.output_shape)
        self.assertEqual(tf.nn.relu, final_layer.activation)

    # def test_build_discriminator(self):
    #     model = gan.build_discriminator()
    #     self.assertTrue(model._is_compiled, 'model not compiled')
    #
    #     first_layer = model.layers[0]
    #     self.assertEqual([(None, 784)], first_layer.input_shape)
    #
    #     final_layer = model.layers[-1]
    #     self.assertEqual((None, 10, 1), final_layer.output_shape)
    #     self.assertEqual(tf.nn.softmax, final_layer.activation)
