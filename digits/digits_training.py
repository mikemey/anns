import os
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, Input, Model, optimizers, utils

# from tensorflow.python.keras.layers.preprocessing import image_preprocessing
DEFAULT_SOURCE_FILE = f'{os.path.dirname(__file__)}/data/test.csv'
DEFAULT_IMAGE_COUNT = 42000
DEFAULT_BATCH_SIZE = 10
DEFAULT_VALIDATION_RATIO = 0.9

IMAGE_SHAPE = 28, 28
LINE_SHAPE = np.multiply(*IMAGE_SHAPE),
LABEL_COLUMN = 'label'
CSV_COLUMNS = [LABEL_COLUMN] + [f'pixel{i}' for i in range(LINE_SHAPE[0])]


class DigitsModel:
    def __init__(self,
                 source_file=DEFAULT_SOURCE_FILE,
                 train_valid_p=DEFAULT_VALIDATION_RATIO,
                 batch_size=DEFAULT_BATCH_SIZE
                 ):
        # inputs = Input(shape=LINE_SHAPE, dtype='float32')
        # x = layers.experimental.preprocessing.Normalization()(inputs)
        # x = layers.Reshape(IMAGE_SHAPE, input_shape=LINE_SHAPE)(x)
        # outputs = layers.Dense(10, input_shape=IMAGE_SHAPE, activation="softmax")(x)

        inputs = Input(shape=(794,))
        x = layers.experimental.preprocessing.Rescaling(1 / 255)(inputs)
        x = layers.Reshape((28, 28, 1))(x)
        x = layers.Conv2D(filters=32, kernel_size=3, activation="relu")(x)
        x = layers.Conv2D(filters=32, kernel_size=3, activation="relu")(x)
        x = layers.MaxPooling2D(pool_size=2)(x)
        x = layers.Dropout(0.1)(x)
        x = layers.Flatten()(x)
        x = layers.Dense(128, activation='relu')(x)
        outputs = layers.Dense(10, activation="softmax")(x)
        model = Model(inputs, outputs)

        model.summary()

        df = pd.read_csv(source_file)
        input_ds = df.drop(columns=[LABEL_COLUMN])
        target_ds = df[[LABEL_COLUMN]]
        target_ds = utils.to_categorical(target_ds, 10)

        print('-- IS COMPILED --')
        print(model.layers)
        model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=['accuracy'])
        print(model._is_compiled)
        # history = model.fit(input_ds, target_ds, epochs=1, verbose=1)
        # print(model.predict(input_ds))

        # test_d = [list(range(0, 250, 30)),
        #           [100, 100, 100, 100, 100, 100, 100, 100, 100],
        #           [255, 255, 255, 255, 255, 255, 255, 255, 255]]
        # print(model.predict(test_d))

        # history = model.fit(input_ds, target_ds, epochs=1)
        print(history.history)
        print('-- done --')

        # ================================================================================
        # inputs = Input(shape=(150, 150, 3))
        # # Rescale images to [0, 1]
        # x = layers.experimental.preprocessing.Normalization()(inputs)
        # x = layers.Conv2D(filters=32, kernel_size=3, activation="relu")(x)
        # x = layers.MaxPooling2D(pool_size=(3, 3))(x)
        # x = layers.Conv2D(filters=32, kernel_size=3, activation="relu")(x)
        # x = layers.MaxPooling2D(pool_size=(3, 3))(x)
        # x = layers.Conv2D(filters=32, kernel_size=3, activation="relu")(x)
        #
        # x = layers.GlobalAveragePooling2D()(x)
        # outputs = layers.Dense(10, activation="softmax")(x)
        #
        # model = Model(inputs=inputs, outputs=outputs)
        # model.summary()
        # ================================================================================
        # inputs = Input(shape=(784 ,))
        # x = layers.experimental.preprocessing.Normalization()(inputs)
        # x = layers.Reshape(image_shape, input_shape=line_shape)
        # x = layers.Conv2D(input_shape=image_shape, filters=10, kernel_size=3, activation="relu")(x)
        # x = layers.MaxPooling2D(input_shape=(26, 26, 10), inpool_size=(3, 3))(x)
        # outputs = layers.Dense(10, activation="softmax")(x)
        # model = Model(inputs, outputs)
        # model.summary()

        # ================================================================================
        # Compile the model
        # model.compile(optimizer="adam", loss="sparse_categorical_crossentropy")

        # (x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()
        # Train the model for 1 epoch from Numpy data
        # batch_size = 64
        # print("Fit on NumPy data")
        # history = model.fit(x_train, y_train, batch_size=batch_size, epochs=1)

        # Train the model for 1 epoch using a dataset
        # dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train)).batch(batch_size)
        # print("Fit on Dataset")
        # history = model.fit(dataset, epochs=1)

        # print(imgs.apply())
        # for features, labels in imgs:
        #     print(len(features), len(labels))
        # imgs = tf.reshape(imgs, shape=(4, *image_size))
        # print(imgs)
        # for data, labels in imgs:
        #     print(data.shape)  # (64, 200, 200, 3)
        # print(data.dtype)  # float32
        # print(labels.shape)  # (64,)
        # print(labels.dtype)  # int32
        # val_dataset = tf.data.Dataset.from_tensor_slices((x_test, y_test)).batch(batch_size)
        # history = model.fit(dataset, epochs=1, validation_data=val_dataset)
        #
