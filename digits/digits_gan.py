from __future__ import print_function, division

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from PIL import Image
from tensorflow.keras import layers, Model, utils, optimizers, losses

DEFAULT_SOURCE_FILE = os.path.join(os.path.dirname(__file__), 'data', 'train.csv')
LABEL_COLUMN = 'label'

NUM_CLASSES = 10
NOISE_INPUT_SHAPE = (None, 200)
LABEL_INPUT_SHAPE = (None, NUM_CLASSES)

IMAGE_SHAPE = 28, 28
FLAT_IMAGE_SHAPE = (np.multiply(*IMAGE_SHAPE),)


def build_generator():
    noise_in = layers.Input(shape=(200,), name='noise_in')
    label = layers.Input(shape=(NUM_CLASSES,), name='label_in')
    combined_in = [noise_in, label]
    inputs = layers.concatenate(combined_in)

    x = layers.Dense(7 * 7 * 128, activation=tf.nn.relu)(inputs)
    x = layers.Reshape((7, 7, 128))(x)
    x = layers.BatchNormalization(momentum=0.8)(x)
    x = layers.UpSampling2D(size=2)(x)
    x = layers.Conv2D(filters=128, kernel_size=3, padding='same', activation=tf.nn.relu)(x)
    x = layers.BatchNormalization(momentum=0.8)(x)
    x = layers.UpSampling2D(size=2)(x)
    x = layers.Conv2D(filters=64, kernel_size=3, padding='same', activation=tf.nn.relu)(x)
    x = layers.BatchNormalization(momentum=0.8)(x)
    image_output = layers.Conv2D(filters=1, kernel_size=3, padding='same', activation=tf.nn.sigmoid)(x)

    return Model(combined_in, image_output, name='Generator')


def build_discriminator():
    inputs = layers.Input(shape=(28, 28, 1))
    x = layers.Reshape(IMAGE_SHAPE + (1,))(inputs)
    x = layers.Conv2D(filters=32, kernel_size=3, activation=tf.nn.relu)(x)
    x = layers.Dropout(0.2)(x)
    x = layers.Conv2D(filters=64, kernel_size=3, activation=tf.nn.relu)(x)
    x = layers.MaxPooling2D(pool_size=2)(x)
    x = layers.Dropout(0.2)(x)
    x = layers.Flatten()(x)
    x = layers.Dense(64, activation=tf.nn.relu)(x)
    is_real = layers.Dense(1, activation=tf.nn.sigmoid)(x)
    label_out = layers.Dense(NUM_CLASSES, activation=tf.nn.softmax)(x)

    return Model(inputs, [is_real, label_out], name='Discriminator')


def show_image(img_data):
    if np.shape(img_data) == FLAT_IMAGE_SHAPE:
        img_data = np.reshape(img_data, (28, 28))
    plt.imshow(img_data, cmap='gray')
    plt.show()


def get_real_trainings_data(source_file):
    df = pd.read_csv(source_file)
    in_ds = df.drop(columns=[LABEL_COLUMN]) / 255
    label_ds = df[[LABEL_COLUMN]]
    return in_ds, label_ds


class DigitsGanTraining:
    def __init__(self, source_file=DEFAULT_SOURCE_FILE, batch_size=32):
        self.batch_size = batch_size
        self.real_trainings_data, self.real_labels = get_real_trainings_data(source_file)
        self.generator = build_generator()
        self.discriminator = build_discriminator()
        self.discriminator.compile(optimizer=optimizers.Adam(),
                                   loss=losses.binary_crossentropy)

    def noise_for_batch(self, count=None):
        if not count:
            count = self.batch_size
        return np.random.normal(0, 1, (count, 200))

    def create_discriminator_batches(self):
        idx = np.random.randint(0, self.real_trainings_data.shape[0], self.batch_size)
        real_imgs = self.real_trainings_data.take(idx)
        real_imgs = real_imgs.values.reshape(self.batch_size, 28, 28, 1)
        real_labels = self.real_labels.take(idx)

        gen_labels = np.random.randint(0, 10, self.batch_size)
        gen_imgs = self.generator.predict([
            self.noise_for_batch(), utils.to_categorical(gen_labels, NUM_CLASSES)
        ])

        all_imgs = np.concatenate([real_imgs, gen_imgs])
        rf_indicator = np.ones(2 * self.batch_size)
        rf_indicator[self.batch_size:] = 0
        all_labels = np.concatenate([real_labels.values[:, 0], gen_labels])
        all_labels = utils.to_categorical(all_labels, NUM_CLASSES)

        return all_imgs, rf_indicator, all_labels

    # def train(self, iterations):
    #     self.discriminator.trainable = False
    #     gan = Model(self.generator.input, self.discriminator(self.generator.output))
    #     gan.compile(optimizer=optimizers.Adam(),
    #                 loss=losses.binary_crossentropy)
    #
    #     valid = np.ones(self.batch_size)
    #
    #     # print()
    #     # print('=================== GENERATOR =====================')
    #     # self.generator.summary()
    #     # print('=================== DISCRIMINATOR =====================')
    #     # self.discriminator.summary()
    #     # print('=================== COMBINED =====================')
    #     # gan.summary()
    #     for it in range(iterations):
    #         img_data, rf_indicator = self.create_discriminator_batches()
    #         self.discriminator.trainable = True
    #         d_loss = self.discriminator.train_on_batch(img_data, rf_indicator)
    #         self.discriminator.trainable = False
    #         g_loss = gan.train_on_batch(self.noise_for_batch(), valid)
    #
    #         print(f'{it:4} [D-L: {d_loss:7.3f}, [G-L: {g_loss:7.3f}]')
    #         if g_loss < 0.5:
    #             self.sample_images()

    # def sample_images(self, grid=(5, 5)):
    #     gen_imgs = self.generator.predict(self.noise_for_batch(25))
    #     gen_imgs = 0.5 * gen_imgs + 0.5
    #
    #     fig, axs = plt.subplots(grid[0], grid[1])
    #     cnt = 0
    #     for i in range(grid[0]):
    #         for j in range(grid[1]):
    #             img = np.reshape(gen_imgs[cnt], (28, 28))
    #             axs[i, j].imshow(img, cmap='gray')
    #             axs[i, j].axis('off')
    #             cnt += 1
    #     plt.show()
    #     plt.close()


def store_image_from_prediction(prediction):
    prediction = np.reshape(prediction, (28, 28))
    img = Image.fromarray(prediction, mode='I;16')
    img.save('data/random.png')


def load_and_convert(img_file):
    return list(Image.open(img_file).convert('L').getdata())


def predict_digits_with(model):
    print('predictions:')
    files = [('data/weird_5.png', 5), ('data/an_8.png', 8), ('data/a_3.png', 3), ('data/random.png', -1)]
    for file, expectation in files:
        data = tf.convert_to_tensor([load_and_convert(file)])
        prediction = model.predict(data)
        print(f'expected: {expectation} - prediction: {prediction}')


if __name__ == '__main__':
    training = DigitsGanTraining(batch_size=5)
    # training.create_discriminator_batches()
    # training.train(2000)
    # predict_digits_with(training.discriminator)
