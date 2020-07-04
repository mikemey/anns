from __future__ import print_function, division

import os
import pathlib
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from PIL import Image
from tensorflow.keras import layers, Model, utils, optimizers, losses

from data_sink import DataSink

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
LOG_DIR = os.path.join(os.path.dirname(__file__), 'log', f'run_{int(time.time())}')
LOSS_DATA_ID = 'loss'


def data_file_path(file_name):
    return os.path.join(DATA_DIR, file_name)


def log_file_path(file_name):
    return os.path.join(LOG_DIR, file_name)


LABEL_COLUMN = 'label'

NUM_CLASSES = 10
NOISE_INPUT_LEN = 128
LABEL_INPUT_SHAPE = (None, NUM_CLASSES)

IMAGE_SHAPE = 28, 28
IMAGE_SHAPE_3D = (*IMAGE_SHAPE, 1)
FLAT_IMAGE_SHAPE = (np.multiply(*IMAGE_SHAPE),)


def build_generator():
    noise_in = layers.Input(shape=(NOISE_INPUT_LEN,), name='noise_in')
    label = layers.Input(shape=(NUM_CLASSES,), name='label_in')

    x = layers.Concatenate()([noise_in, label])
    x = layers.Dense(7 * 7 * 128, activation=tf.nn.relu)(x)
    x = layers.Reshape((7, 7, 128))(x)
    x = layers.BatchNormalization(momentum=0.8)(x)
    x = layers.Dropout(0.2)(x)
    x = layers.UpSampling2D(size=2)(x)
    x = layers.Conv2D(filters=128, kernel_size=3, padding='same', activation=tf.nn.relu)(x)
    x = layers.BatchNormalization(momentum=0.8)(x)
    x = layers.UpSampling2D(size=2)(x)
    x = layers.Conv2D(filters=64, kernel_size=3, padding='same', activation=tf.nn.relu)(x)
    x = layers.BatchNormalization(momentum=0.8)(x)
    image_output = layers.Conv2D(filters=1, kernel_size=3, padding='same', activation=tf.nn.sigmoid)(x)

    return Model([noise_in, label], image_output, name='Generator')


def build_discriminator():
    inputs = layers.Input(shape=IMAGE_SHAPE_3D)
    x = layers.Reshape(IMAGE_SHAPE + (1,))(inputs)
    x = layers.Conv2D(filters=64, kernel_size=3, activation=tf.nn.relu)(x)
    x = layers.Dropout(0.2)(x)
    x = layers.Conv2D(filters=32, kernel_size=3, activation=tf.nn.relu)(x)
    x = layers.MaxPooling2D(pool_size=2)(x)
    x = layers.Dropout(0.2)(x)
    x = layers.Flatten()(x)
    x = layers.Dense(128, activation=tf.nn.relu)(x)
    is_real = layers.Dense(1, name='real-fake-indicator', activation=tf.nn.sigmoid)(x)
    label_out = layers.Dense(NUM_CLASSES, name='predicted_label', activation=tf.nn.softmax)(x)

    return Model(inputs, [is_real, label_out], name='Discriminator')


def show_image(img_data):
    if np.shape(img_data) == FLAT_IMAGE_SHAPE:
        img_data = np.reshape(img_data, IMAGE_SHAPE)
    plt.imshow(img_data, cmap='gray')
    plt.show()


def get_real_trainings_data(source_file):
    df = pd.read_csv(source_file)
    in_ds = df.drop(columns=[LABEL_COLUMN]) / 255
    label_ds = df[[LABEL_COLUMN]]
    return in_ds, label_ds


def load_and_convert(img_file):
    img_data = list(Image.open(img_file).convert('L').getdata())
    img_data = np.reshape(img_data, IMAGE_SHAPE_3D)
    return tf.convert_to_tensor([img_data])


class DigitsGanTraining:
    def __init__(self, source_file=data_file_path('train.csv'), batch_size=32):
        self.batch_size = batch_size
        self.real_trainings_data, self.real_labels = get_real_trainings_data(source_file)
        self.sink = DataSink('stats', log_dir=LOG_DIR)
        self.sink.add_graph_header(LOSS_DATA_ID, ['iteration', 'd-loss', 'g-loss'])

        comb_losses = [losses.binary_crossentropy, losses.categorical_crossentropy]
        self.generator = build_generator()
        self.discriminator = build_discriminator()
        self.discriminator.compile(optimizer=optimizers.Adam(), loss=comb_losses)

        self.gan = Model(self.generator.inputs, self.discriminator(self.generator.output))
        self.gan.compile(optimizer=optimizers.Adam(), loss=comb_losses)

    def create_discriminator_batches(self, noise, gen_label_cats):
        idx = np.random.randint(0, self.real_trainings_data.shape[0], self.batch_size)
        real_imgs = self.real_trainings_data.take(idx)
        real_imgs = real_imgs.values.reshape(self.batch_size, *IMAGE_SHAPE_3D)
        real_labels = self.real_labels.take(idx)

        gen_imgs = self.generator.predict([noise, gen_label_cats])

        all_imgs = np.concatenate([real_imgs, gen_imgs])
        rf_indicator = np.ones(2 * self.batch_size)
        rf_indicator[self.batch_size:] = 0
        rf_indicator += 0.05 * tf.random.uniform(tf.shape(rf_indicator))

        all_labels = utils.to_categorical(real_labels.values[:, 0], NUM_CLASSES)
        all_labels = np.concatenate([all_labels, gen_label_cats])

        return all_imgs, rf_indicator, all_labels

    def train(self, iterations, show_case_every=50):
        valid = np.ones(self.batch_size)

        for it in range(iterations):
            noise = np.random.normal(0, 1, (self.batch_size, NOISE_INPUT_LEN))
            gen_labels = utils.to_categorical(np.random.randint(0, 10, self.batch_size), NUM_CLASSES)

            img_data, rf_indicator, labels = self.create_discriminator_batches(noise, gen_labels)
            self.discriminator.trainable = True
            d_tot_l, d_rf_l, d_label_l = self.discriminator.train_on_batch(img_data, [rf_indicator, labels])

            self.discriminator.trainable = False
            gan_tot_l, gan_rf_l, gan_label_l = self.gan.train_on_batch([noise, gen_labels], [valid, gen_labels])

            print(f'{it:4} Dis [tot-l: {d_tot_l:7.3f}, rf-l: {d_rf_l:7.3f}, lbl-l: {d_label_l:7.3f}] -- '
                  f'Gen [tot-l: {gan_tot_l:7.3f}, rf-l: {gan_rf_l:7.3f}, lbl-l: {gan_label_l:7.3f}')

            self.sink.add_data(LOSS_DATA_ID, [it, d_tot_l, gan_tot_l])
            if (it % show_case_every) == (show_case_every - 1):
                self.store_images(it)
        self.sink.drain_data()

    def store_images(self, identifier):
        rows, cols = 10, 10
        noise = np.random.normal(0, 1, (rows * cols, NOISE_INPUT_LEN))
        labels = utils.to_categorical([num for _ in range(rows) for num in range(cols)])
        gen_imgs = self.generator.predict([noise, labels])

        fig, axs = plt.subplots(rows, cols)
        cnt = 0
        for row in range(rows):
            for col in range(cols):
                img = np.reshape(gen_imgs[cnt], IMAGE_SHAPE)
                axs[row, col].imshow(img, cmap='gray')
                axs[row, col].axis('off')
                cnt += 1
        fig.savefig(log_file_path(f'it_{identifier}.png'))
        plt.close(fig)
        # plt.show()

    def predict_own_digits(self):
        print('predictions:')
        files = [(data_file_path('weird_5.png'), True, 5), (data_file_path('an_8.png'), True, 8),
                 (data_file_path('a_3.png'), True, 3), (data_file_path('random.png'), False, -1)]

        for file, expect_rf, expect_label in files:
            rf_ind, label_pred = self.discriminator.predict(load_and_convert(file))
            rf_ind = rf_ind[0][0] > 0.5
            label_pred = label_pred.reshape((10,)).argmax()
            print(f'expected [real: {expect_rf}, label: {expect_label}] - '
                  f'predicted [real: {rf_ind}, label: {label_pred}]')


def store_image_from_prediction(prediction):
    prediction = np.reshape(prediction, IMAGE_SHAPE)
    img = Image.fromarray(prediction, mode='I;16')
    img.save(data_file_path('random.png'))


if __name__ == '__main__':
    pathlib.Path(LOG_DIR).mkdir(parents=True, exist_ok=False)
    training = DigitsGanTraining()
    training.train(2000, show_case_every=25)
    training.predict_own_digits()
