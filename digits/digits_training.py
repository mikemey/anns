import os

import numpy as np
import pandas as pd
import tensorflow as tf
from PIL import Image
from tensorflow.keras import layers, Input, Model, utils, optimizers, losses

DEFAULT_SOURCE_FILE = os.path.join(os.path.dirname(__file__), 'data', 'train.csv')
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
    in_ds = df.drop(columns=[LABEL_COLUMN])
    label_ds = df[[LABEL_COLUMN]]
    label_ds = utils.to_categorical(label_ds, NUM_CLASSES)
    return in_ds, label_ds


def train_model(model=None):
    if not model:
        model = build_model()
    input_ds, target_ds = get_trainings_data()
    history = model.fit(input_ds, target_ds, epochs=1, validation_split=0.2)
    print(history.history)
    return model


def load_and_convert(img_file):
    return list(Image.open(img_file).convert('L').getdata())


def predict_digits_with(model):
    print('predictions:')
    files = [('data/weird_5.png', 5), ('data/an_8.png', 8), ('data/a_3.png', 3)]
    for file, expectation in files:
        data = tf.convert_to_tensor([load_and_convert(file)])
        prediction = model.predict(data)
        print(f'expected: {expectation} - prediction: {prediction.argmax()}')


if __name__ == '__main__':
    # m = build_model()
    m = train_model()
    predict_digits_with(m)
