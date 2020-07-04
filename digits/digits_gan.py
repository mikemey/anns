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
    # combined_in =
    # inputs = layers.concatenate(combined_in)

    x = layers.Concatenate()([noise_in, label])  # (7 * 7 * 128, activation=tf.nn.relu)(inputs)
    x = layers.Dense(7 * 7 * 128, activation=tf.nn.relu)(x)
    x = layers.Reshape((7, 7, 128))(x)
    x = layers.BatchNormalization(momentum=0.8)(x)
    x = layers.UpSampling2D(size=2)(x)
    x = layers.Conv2D(filters=128, kernel_size=3, padding='same', activation=tf.nn.relu)(x)
    x = layers.BatchNormalization(momentum=0.8)(x)
    x = layers.UpSampling2D(size=2)(x)
    x = layers.Conv2D(filters=64, kernel_size=3, padding='same', activation=tf.nn.relu)(x)
    x = layers.BatchNormalization(momentum=0.8)(x)
    image_output = layers.Conv2D(filters=1, kernel_size=3, padding='same', activation=tf.nn.sigmoid)(x)

    return Model([noise_in, label], image_output, name='Generator')


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
    is_real = layers.Dense(1, name='real-fake-indicator', activation=tf.nn.sigmoid)(x)
    label_out = layers.Dense(NUM_CLASSES, name='predicted_label', activation=tf.nn.softmax)(x)

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


def load_and_convert(img_file):
    img_data = list(Image.open(img_file).convert('L').getdata())
    img_data = np.reshape(img_data, (28, 28, 1))
    return tf.convert_to_tensor([img_data])


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

    def create_discriminator_batches(self, noise, gen_label_cats):
        idx = np.random.randint(0, self.real_trainings_data.shape[0], self.batch_size)
        real_imgs = self.real_trainings_data.take(idx)
        real_imgs = real_imgs.values.reshape(self.batch_size, 28, 28, 1)
        real_labels = self.real_labels.take(idx)

        gen_imgs = self.generator.predict([noise, gen_label_cats])

        all_imgs = np.concatenate([real_imgs, gen_imgs])
        rf_indicator = np.ones(2 * self.batch_size)
        rf_indicator[self.batch_size:] = 0
        all_labels = utils.to_categorical(real_labels.values[:, 0], NUM_CLASSES)
        all_labels = np.concatenate([all_labels, gen_label_cats])

        return all_imgs, rf_indicator, all_labels

    def train(self, iterations):
        gan = Model(self.generator.inputs, self.discriminator(self.generator.output))
        gan.compile(optimizer=optimizers.Adam(),
                    loss=losses.binary_crossentropy)

        valid = np.ones(self.batch_size)

        for it in range(iterations):
            noise = self.noise_for_batch()
            gen_labels = np.random.randint(0, 10, self.batch_size)

            img_data, rf_indicator, labels = self.create_discriminator_batches(noise, gen_labels)
            self.discriminator.trainable = True
            _, rf_loss, disc_label_loss = self.discriminator.train_on_batch(img_data, [rf_indicator, labels])

            self.discriminator.trainable = False
            _, valid_loss, gen_label_loss = gan.train_on_batch([noise, gen_labels], [valid, gen_labels])

            print(f'{it:4} D:[rf-loss: {rf_loss:7.3f}, lbl-loss: {disc_label_loss:7.3f}] --'
                  f'G:[valid-loss: {valid_loss:7.3f}, lbl-loss: {gen_label_loss:7.3f}')

            # print(f'{it:4} [D-L: {d_loss:7.3f}, [G-L: {g_loss:7.3f}]')
            # if g_loss < 0.5:
            #     self.sample_images()

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
    def predict_own_digits(self):
        print('predictions:')
        files = [('data/weird_5.png', True, 5), ('data/an_8.png', True, 8),
                 ('data/a_3.png', True, 3), ('data/random.png', False, -1)]

        for file, expect_rf, expect_label in files:
            rf_ind, label_pred = self.discriminator.predict(load_and_convert(file))
            rf_ind = rf_ind[0][0] > 0.5
            label_pred = label_pred.reshape((10,)).argmax()
            print(f'expected [real: {expect_rf}, label: {expect_label}] - '
                  f'predicted [real: {rf_ind}, label: {label_pred}]')


def store_image_from_prediction(prediction):
    prediction = np.reshape(prediction, (28, 28))
    img = Image.fromarray(prediction, mode='I;16')
    img.save('data/random.png')


if __name__ == '__main__':
    training = DigitsGanTraining()
    training.train(20)
    training.predict_own_digits()
