import os
import sys

from demo_player import DemoMaster
from game.track_builder import TrackBuilderWindow
from manual_player import ManualMaster
from neural_master import NeuralMaster

LOCAL_DIR = os.path.dirname(__file__)
TOP_PLAYERS_FILE = os.path.join(LOCAL_DIR, 'examples', 'top_players.pd')


def __print_help():
    print('Parameters:')
    print('\t[none]      \tsingle-player mode')
    print('\t2           \ttwo-player mode')
    print('\tdemo        \tdemo mode')
    print('\ttrain       \ttraining mode')
    print('\tplay <files>\tshowcase best players from <files>')
    print('\ttop         \tshowcase random players from \'{}\''.format(TOP_PLAYERS_FILE))
    print('\tbuild       \topen track builder')


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
    elif cmd == 'top':
        NeuralMaster().showcase_from_files([TOP_PLAYERS_FILE], select_random=True)
    elif cmd == 'build':
        TrackBuilderWindow().run()
    else:
        __print_help()
else:
    ManualMaster().run()
