import sys

from demo_player import DemoMaster
from manual_player import ManualMaster


def print_help():
    print('Parameters:')
    print('\t[none]\tstart manual mode')
    print('\tdemo\tstart demo mode')


if len(sys.argv) > 1:
    cmd = sys.argv[1]
    if cmd == 'demo':
        DemoMaster().run()
    else:
        print_help()
else:
    ManualMaster().run()
