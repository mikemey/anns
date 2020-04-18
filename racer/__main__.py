import sys

from demo_player import DemoMaster
from manual_player import ManualMaster
from neural_master import NeuralMaster


def __print_help():
    print('Parameters:')
    print('\t[none]     \tsingle-player mode')
    print('\t2          \t2-player mode')
    print('\tdemo       \tdemo mode')
    print('\ttrain      \ttraining mode')
    print('\tplay <files>\tshowcase best players from <files>')


if len(sys.argv) > 1:
    cmd = sys.argv[1]
    if cmd == 'demo':
        DemoMaster().run()
    elif cmd == '2':
        ManualMaster(True).run()
    elif cmd == 'train':
        NeuralMaster().train()
    elif cmd == 'play' and len(sys.argv) > 2:
        files = sys.argv[2:]
        NeuralMaster().showcase_from_files(files)
    else:
        __print_help()
else:
    ManualMaster().run()
