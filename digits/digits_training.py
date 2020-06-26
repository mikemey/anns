import os

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, Input, Model, utils, optimizers, losses

DEFAULT_SOURCE_FILE = f'{os.path.dirname(__file__)}/data/test.csv'
DEFAULT_BATCH_SIZE = 10
DEFAULT_VALIDATION_RATIO = 0.9

IMAGE_SHAPE = 28, 28
LINE_SHAPE = (np.multiply(*IMAGE_SHAPE),)
NUM_CLASSES = 10
LABEL_COLUMN = 'label'


def build_model():
    inputs = Input(shape=LINE_SHAPE)
    x = layers.experimental.preprocessing.Rescaling(1 / 255)(inputs)
    x = layers.Reshape(IMAGE_SHAPE + (1,))(x)
    x = layers.Conv2D(filters=32, kernel_size=3, activation=tf.nn.relu)(x)
    x = layers.Dropout(0.1)(x)
    x = layers.Conv2D(filters=32, kernel_size=3, activation=tf.nn.relu)(x)
    x = layers.MaxPooling2D(pool_size=2)(x)
    x = layers.MaxPooling2D(pool_size=2)(x)
    x = layers.Flatten()(x)
    x = layers.Dense(128, activation=tf.nn.relu)(x)
    outputs = layers.Dense(NUM_CLASSES, activation=tf.nn.softmax)(x)

    model = Model(inputs, outputs)
    model.compile(optimizer=optimizers.Adam(),
                  loss=losses.categorical_crossentropy,
                  metrics=['accuracy'])
    return model


def get_trainings_data(source_file=DEFAULT_SOURCE_FILE):
    df = pd.read_csv(source_file)
    input_ds = df.drop(columns=[LABEL_COLUMN])
    target_ds = df[[LABEL_COLUMN]]
    target_ds = utils.to_categorical(target_ds, NUM_CLASSES)
    return input_ds, target_ds
