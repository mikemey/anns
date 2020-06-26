import os
import unittest

from digits_model import DigitsModel

TEST_TRAINING_DATA = f'{os.path.dirname(__file__)}/test_data/digits_model.csv'


# dataset = keras.preprocessing.image.(/
#     'path/to/main_directory', batch_size=64, image_size=(200, 200))

# For demonstration, iterate over the batches yielded by the dataset.
# for data, labels in dataset:
#     print(data.shape)  # (64, 200, 200, 3)
#     print(data.dtype)  # float32
#     print(labels.shape)  # (64,)
#     print(labels.dtype)  # int32

class ModelTestCase(unittest.TestCase):
    def test_creates_dataset(self):
        model = DigitsModel(TEST_TRAINING_DATA, 0.8)
        # self.__assert_dataset(model.training_ds, 3, [0.0, 1.0, 0.0], [9, 4, 0])
        # self.__assert_dataset(model.validation_ds, 1, [0.0], [1])

    @staticmethod
    def __assert_dataset(dataset, exp_len, exp_first_vals, exp_labels):
        data, labels = dataset
        print(data.shape)  # (64, 200, 200, 3)
        print(data.dtype)  # float32
        print(labels.shape)  # (64,)
        print(labels.dtype)  # int32
