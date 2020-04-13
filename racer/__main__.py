import sys

from demo_player import DemoMaster
from manual_player import ManualMaster
from neural_player import NeuralMaster


def print_help():
    print('Parameters:')
    print('\t[none] \tsingle-player mode')
    print('\t2      \t2-player mode')
    print('\tdemo   \tdemo mode')
    print('\ttrain  \ttraining mode')


if len(sys.argv) > 1:
    cmd = sys.argv[1]
    if cmd == 'demo':
        DemoMaster().run()
    elif cmd == '2':
        ManualMaster(True).run()
    elif cmd == 'train':
        NeuralMaster().run()
    else:
        print_help()
else:
    ManualMaster().run()
