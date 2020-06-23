import os
import shutil
import unittest

from data_sink import DataSink

test_log_dir = f'{os.path.dirname(__file__)}/log'
field_x, field_y1, field_y2 = 'field_x', 'field_y_1', 'field_y_2'


class TestDataSink(DataSink):
    def __init__(self, run_id):
        super().__init__(run_id, test_log_dir)


class DataSinkTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        shutil.rmtree(test_log_dir, ignore_errors=True)

    def test_creates_log_files(self):
        run_test_id, graph_id_1, graph_id_2 = 'run-1', 'graph1', 'graph2'
        sink = TestDataSink(run_test_id)
        sink.add_graph_header(graph_id_1, field_x, field_y2)
        sink.add_graph_header(graph_id_2, field_x, field_y1, field_y2)

        def assert_header_line(graph_id, expected_header):
            with open(f'{test_log_dir}/{run_test_id}/{graph_id}.csv') as f:
                lines = f.readlines()
                self.assertEqual(1, len(lines))
                self.assertEqual(expected_header, lines[0])

        assert_header_line(graph_id_1, f'{field_x},{field_y2}\n')
        assert_header_line(graph_id_2, f'{field_x},{field_y1},{field_y2}\n')

    def test_reject_duplicate_run_id(self):
        dup_run_id = 'duplicate-name'
        TestDataSink(dup_run_id)
        with self.assertRaises(AssertionError) as ctx:
            TestDataSink(dup_run_id)
        self.assertIn(f'{dup_run_id}', str(ctx.exception))

    def test_reject_duplicate_graph_id(self):
        sink = TestDataSink('run-2')
        dup_graph_id = 'dup-graph'
        sink.add_graph_header(dup_graph_id, 'x')
        with self.assertRaises(AssertionError) as ctx:
            sink.add_graph_header(dup_graph_id, 'x')
        self.assertIn(f'{dup_graph_id}', str(ctx.exception))

    # def test_writes_to_file_in_batches(self):
    #     pass
