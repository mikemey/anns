import unittest

from data_sink import DataSink


class LogTestCase(unittest.TestCase):
    def setUp(self):
        print('hello')

    def test_blabla(self):
        sink = DataSink()
        self.assertEqual(sink.name, 'hello world')
        print('\n-- test DONE\n')
