import pathlib
from typing import Any, Iterable

LOG_DIR = 'log'
BATCH_SIZE = 10

FILE_KEY = 'file'
VALS_KEY = 'values'
LINES_KEY = 'lines'
SIZE_KEY = 'size'


def csv_line(values):
    return ','.join(str(s) for s in values) + '\n'


class DataSink:
    def __init__(self, run_id, log_dir=LOG_DIR, batch_size=BATCH_SIZE):
        self.__log_dir = f'{log_dir}/{run_id}'
        self.__graphs = {}
        self.__batch_size = batch_size
        log_path = pathlib.Path(self.__log_dir)
        if log_path.exists():
            raise AssertionError(f'duplicate run-id, log-dir: {self.__log_dir}')
        log_path.mkdir(parents=True, exist_ok=True)

    def add_graph_header(self, graph_id, fields: Iterable[Any]):
        if graph_id in self.__graphs.keys():
            raise AssertionError(f'duplicate graph name: {graph_id}')

        self.__graphs[graph_id] = {
            FILE_KEY: f'{self.__log_dir}/{graph_id}.csv',
            VALS_KEY: [],
            LINES_KEY: [],
            SIZE_KEY: len(fields)
        }
        self.__write_file_line(graph_id, csv_line(fields))

    def add_data(self, graph_id, values: Iterable[Any]):
        if graph_id not in self.__graphs:
            raise AssertionError(f'unknown graph: {graph_id}')

        graph_data = self.__graphs[graph_id]
        if not len(values) == graph_data[SIZE_KEY]:
            raise AssertionError(f'expected {graph_data[SIZE_KEY]} values, received: {values}')

        graph_vals, file_lines = graph_data[VALS_KEY], graph_data[LINES_KEY]
        graph_vals.append(values)
        file_lines.append(csv_line(values))

        if len(graph_vals) >= self.__batch_size:
            self.__drain_graph_data(graph_id)

    def drain_data(self):
        for graph_id in self.__graphs.keys():
            self.__drain_graph_data(graph_id)

    def __drain_graph_data(self, graph_id):
        graph_data = self.__graphs[graph_id]
        graph_vals, file_lines = graph_data[VALS_KEY], graph_data[LINES_KEY]
        data = ''.join(file_lines)
        self.__write_file_line(graph_id, data)
        graph_vals.clear()
        file_lines.clear()

    def __write_file_line(self, graph_id, data):
        with open(self.__graphs[graph_id][FILE_KEY], 'a+') as graph_f:
            graph_f.write(data)
