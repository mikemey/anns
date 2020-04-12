from game.racer_engine import RacerEngine
from game.racer_window import RacerWindow


class ManualMaster:
    def run(self):
        w = RacerWindow(RacerEngine())
        w.start()
