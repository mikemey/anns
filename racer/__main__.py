import sys

from manual_player import ManualMaster


def print_help():
    print('Parameters:')
    print('\t[none]\tstart manual mode')
    print('\tdemo\tstart demo mode')


if len(sys.argv) > 1:
    print(sys.argv[1])
    print_help()
else:
    ManualMaster().run()
