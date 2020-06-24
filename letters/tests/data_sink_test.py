import os
import shutil
import unittest

from data_sink import DataSink

TEST_BATCH_SIZE = 3
TEST_LOG_DIR = f'{os.path.dirname(__file__)}/log'
FIELD_X, FIELD_Y1, FIELD_Y2 = 'field_x', 'field_y_1', 'field_y_2'


class TestDataSink(DataSink):
    def __init__(self, run_id):
        super().__init__(run_id, TEST_LOG_DIR, TEST_BATCH_SIZE)


def test_log(run_id, graph_id):
    return f'{TEST_LOG_DIR}/{run_id}/{graph_id}.csv'


class DataSinkTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        shutil.rmtree(TEST_LOG_DIR, ignore_errors=True)

    def test_creates_log_files(self):
        run_id, graph_id_1, graph_id_2 = 'run-1', 'graph1', 'graph2'
        sink = TestDataSink(run_id)
        sink.add_graph_header(graph_id_1, (FIELD_X, FIELD_Y2))
        sink.add_graph_header(graph_id_2, (FIELD_X, FIELD_Y1, FIELD_Y2))

        def assert_header_line(graph_id, expected_header):
            with open(test_log(run_id, graph_id)) as f:
                lines = f.readlines()
                self.assertEqual(1, len(lines))
                self.assertEqual(expected_header, lines[0])

        assert_header_line(graph_id_1, f'{FIELD_X},{FIELD_Y2}\n')
        assert_header_line(graph_id_2, f'{FIELD_X},{FIELD_Y1},{FIELD_Y2}\n')

    def test_reject_duplicate_run_id(self):
        dup_run_id = 'duplicate-name'
        TestDataSink(dup_run_id)
        with self.assertRaises(AssertionError) as ctx:
            TestDataSink(dup_run_id)
        self.assertIn(f'{dup_run_id}', str(ctx.exception))

    def test_reject_duplicate_graph_id(self):
        sink = TestDataSink('run-2')
        dup_graph_id = 'dup-graph'
        sink.add_graph_header(dup_graph_id, ('x',))
        with self.assertRaises(AssertionError) as ctx:
            sink.add_graph_header(dup_graph_id, ('x',))
        self.assertIn(f'{dup_graph_id}', str(ctx.exception))

    def test_writes_data_in_batches(self):
        run_id, graph_id = 'run-3', 'graph'
        log_file = test_log(run_id, graph_id)
        expected = []
        sink = TestDataSink(run_id)
        sink.add_graph_header(graph_id, (FIELD_X, FIELD_Y2))

        def add_test_data(line_id):
            fields = f'{line_id}_x', f'{line_id}_y2'
            sink.add_data(graph_id, fields)
            expected.append(','.join(fields))

        for i in range(TEST_BATCH_SIZE - 1):
            add_test_data(i)
        self.__assert_data_lines(run_id, graph_id, 0)

        add_test_data(2)
        self.__assert_data_lines(run_id, graph_id, len(expected))

        for i in range(TEST_BATCH_SIZE):
            add_test_data(i + 10)
        with open(log_file) as f:
            lines = f.readlines()
            self.assertEqual(len(expected) + 1, len(lines))
            self.assertEqual('\n'.join(expected) + '\n', ''.join(lines[1:]))

    def test_drain_batches(self):
        run_id, g_1, g_2, g_3 = 'run-4', 'graph1', 'graph2', 'graph3'
        sink = TestDataSink(run_id)
        sink.add_graph_header(g_1, (FIELD_X, FIELD_Y2))
        sink.add_graph_header(g_2, (FIELD_X, FIELD_Y1, FIELD_Y2))
        sink.add_graph_header(g_3, (FIELD_X, FIELD_Y1, FIELD_Y2, FIELD_X))

        sink.add_data(g_1, (1, 2))
        for i in range(TEST_BATCH_SIZE):
            sink.add_data(g_2, (1, 2, 3))
            sink.add_data(g_3, (1, 2, 3, 1))
        sink.add_data(g_3, (1, 2, 3, 1))

        self.__assert_data_lines(run_id, g_1, 0)
        self.__assert_data_lines(run_id, g_2, 3)
        self.__assert_data_lines(run_id, g_3, 3)

        sink.drain_data()
        self.__assert_data_lines(run_id, g_1, 1)
        self.__assert_data_lines(run_id, g_2, 3)
        self.__assert_data_lines(run_id, g_3, 4)

    def test_reject_invalid_graph_id(self):
        run_id, g_1 = 'run-5', 'graph1'
        sink = TestDataSink(run_id)
        with self.assertRaises(AssertionError) as ctx:
            sink.add_data(g_1, (42,))
        self.assertIn(f'unknown graph: {g_1}', str(ctx.exception))

    def test_reject_invalid_field_count(self):
        run_id, graph_id = 'run-6', 'graph'
        sink = TestDataSink(run_id)
        sink.add_graph_header(graph_id, (FIELD_X, FIELD_Y2))

        with self.assertRaises(AssertionError) as ctx:
            sink.add_data(graph_id, (42,))
        self.assertIn(f'expected 2 values, received: (42,)', str(ctx.exception))

    def __assert_data_lines(self, run_id, graph_id, expected_data_lines):
        with open(test_log(run_id, graph_id)) as f:
            data_count = len(f.readlines()) - 1
            self.assertEqual(expected_data_lines, data_count)
