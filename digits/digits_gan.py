from __future__ import print_function, division

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, Model, utils
from tensorflow.keras.layers import Input, Dense

DEFAULT_SOURCE_FILE = os.path.join(os.path.dirname(__file__), 'data', 'train.csv')
LABEL_COLUMN = 'label'

NUM_CLASSES = 10
NOISE_INPUT_SHAPE = (None, 200)
LABEL_INPUT_SHAPE = (None, NUM_CLASSES)

IMAGE_SHAPE = 28, 28
FLAT_IMAGE_SHAPE = (np.multiply(*IMAGE_SHAPE),)


def build_generator():
    noise_in = Input(shape=(200,), name='noise_in')
    # label = Input(shape=(NUM_CLASSES,), name='label_in')
    # combined_in = [noise_in, label]
    # inputs = layers.concatenate(combined_in)

    x = layers.Dense(7 * 7 * 64, activation=tf.nn.relu)(noise_in)
    x = layers.Reshape((7, 7, 64))(x)
    x = layers.UpSampling2D(size=2)(x)
    x = layers.Conv2D(filters=128, kernel_size=3, padding='same', activation=tf.nn.relu)(x)
    x = layers.BatchNormalization()(x)
    x = layers.UpSampling2D(size=2)(x)
    x = layers.Conv2D(filters=128, kernel_size=3, padding='same', activation=tf.nn.relu)(x)
    x = layers.Flatten()(x)
    image_output = layers.Dense(FLAT_IMAGE_SHAPE[0], activation=tf.nn.relu)(x)

    # model = Model(combined_in, image_output)
    model = Model(noise_in, image_output, name='Generator')
    # model.summary()
    return model


def build_discriminator():
    inputs = Input(shape=FLAT_IMAGE_SHAPE)
    x = layers.Reshape(IMAGE_SHAPE + (1,))(inputs)
    x = layers.Conv2D(filters=32, kernel_size=3, activation=tf.nn.relu)(x)
    x = layers.Dropout(0.2)(x)
    x = layers.Conv2D(filters=64, kernel_size=3, activation=tf.nn.relu)(x)
    x = layers.MaxPooling2D(pool_size=2)(x)
    x = layers.Dropout(0.2)(x)
    x = layers.Flatten()(x)
    x = layers.Dense(64, activation=tf.nn.relu)(x)
    # outputs = layers.Dense(NUM_CLASSES, activation=tf.nn.softmax)(x)
    is_real = Dense(1, activation=tf.nn.sigmoid)(x)

    model = Model(inputs, is_real, name='Discriminator')
    # model.summary()
    return model


def show_image(img_data):
    if np.shape(img_data) == FLAT_IMAGE_SHAPE:
        img_data = np.reshape(img_data, (28, 28))
    plt.imshow(img_data, cmap='gray')
    plt.show()


def get_real_trainings_data(source_file):
    df = pd.read_csv(source_file)
    in_ds = df.drop(columns=[LABEL_COLUMN]) / 255
    label_ds = df[[LABEL_COLUMN]]
    label_ds = utils.to_categorical(label_ds, NUM_CLASSES)
    return in_ds, label_ds


class DigitsGanTraining:
    def __init__(self, source_file=DEFAULT_SOURCE_FILE, batch_size=32):
        self.batch_size = batch_size
        self.real_trainings_data, self.real_labels = get_real_trainings_data(source_file)
        self.generator = build_generator()

    def create_discriminator_batches(self):
        real_imgs = self.real_trainings_data.sample(self.batch_size)
        random_input = np.random.normal(0, 1, (self.batch_size, 200))
        gen_imgs = self.generator.predict(random_input)
        return real_imgs, gen_imgs

    def train(self, epochs=1, batch_size=32):
        # generator = build_generator()

        # real_indicators = np.ones((batch_size, 1))
        # fake_indicators = np.zeros((batch_size, 1))
        #
        # discriminator = build_discriminator()
        # for epoch in range(epochs):
        pass
