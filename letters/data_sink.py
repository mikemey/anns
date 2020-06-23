import pathlib
from functools import reduce

LOG_DIR = 'log'

FNAME = 'file_name'


def comma_separated(total, current):
    return f'{total},{current}'


class DataSink:
    def __init__(self, run_id, log_dir=LOG_DIR):
        self.log_dir = f'{log_dir}/{run_id}'
        self.graphs = {}
        log_path = pathlib.Path(self.log_dir)
        if log_path.exists():
            raise AssertionError(f'duplicate run-id, log-dir: {self.log_dir}')
        log_path.mkdir(parents=True, exist_ok=True)

    def add_graph_header(self, graph_name, *fields):
        if graph_name in self.graphs.keys():
            raise AssertionError(f'duplicate graph name: {graph_name}')

        fname = f'{self.log_dir}/{graph_name}.csv'
        self.graphs[graph_name] = {FNAME: fname}
        header = reduce(comma_separated, fields)
        with open(fname, 'a+') as graph_f:
            graph_f.write(f'{header}\n')
