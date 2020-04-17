import sys

from best_player_keep import load_top_list
from demo_player import DemoMaster
from manual_player import ManualMaster
from neural_master import NeuralMaster


def print_help():
    print('Parameters:')
    print('\t[none]     \tsingle-player mode')
    print('\t2          \t2-player mode')
    print('\tdemo       \tdemo mode')
    print('\ttrain      \ttraining mode')
    print('\tplay <file]\tload players from <file> and showcase a race')


if len(sys.argv) > 1:
    cmd = sys.argv[1]
    if cmd == 'demo':
        DemoMaster().run()
    elif cmd == '2':
        ManualMaster(True).run()
    elif cmd == 'train':
        NeuralMaster().train()
    elif cmd == 'play' and len(sys.argv) > 2:
        player_file = sys.argv[2]
        NeuralMaster().showcase(*load_top_list(player_file))
    else:
        print_help()
else:
    ManualMaster().run()
