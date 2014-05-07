import os
import glob
from collections import defaultdict

from ctf.levelconfig import RedVersusBlue
from tests.helpers import *

import mycmd
import examples


class TestLevels(TestSuite):

    @classmethod
    def setUpClass(cls):
        cls.statistics = defaultdict(lambda: 0)

    @classmethod
    def tearDownClass(cls):
        stats = cls.statistics
        assert stats[MatchCombatEvent.TYPE_KILLED] > 3000
        assert stats[MatchCombatEvent.TYPE_FLAG_PICKEDUP] > 300
        assert stats[MatchCombatEvent.TYPE_FLAG_DROPPED] > 150
        assert stats[MatchCombatEvent.TYPE_FLAG_CAPTURED] > 75
        assert stats[MatchCombatEvent.TYPE_FLAG_RESTORED] > 100
        assert stats[MatchCombatEvent.TYPE_RESPAWN] > 3000

    def runLevelTestWithCommanders(self, level, count, cmd):
        cmd1, cmd2 = cmd
        self.config = RedVersusBlue()
        self.config.map = level
        self.config.configure(os.path.splitext(level)[0])
        self.config.red.numberBots = count * 2
        self.config.red.commander = lambda *args, **kwargs: cmd1(*args, **kwargs)
        self.config.blue.numberBots = count
        self.config.blue.commander = lambda *args, **kwargs: cmd2(*args, **kwargs)

        self.config.gameLength = 120.0
        self.config.endOfGameCallback = self.checkCombatEvents

    def checkCombatEvents(self, state, commanders):
        for commander in commanders:
            for e in commander.game.match.combatEvents:
                self.statistics[e.type] += 1


def initialize():
    """Extend the test case above with custom methods for interesting commanders.  The resulting class will be picked
    up by `unittest` automatically.
    """
    commanders = [examples.GreedyCommander, examples.RandomCommander, examples.DefenderCommander,                      \
                  examples.BalancedCommander, mycmd.PlaceholderCommander]

    def runLevelTest(l, c, s):
        return lambda self: TestLevels.runLevelTestWithCommanders(self, l, c, s)

    for level in [os.path.basename(l) for l in glob.glob(os.path.join(os.path.dirname(examples.__file__), 'assets', 'map??.png'))]:
        count = random.randint(5,10)
        selected = random.sample(commanders, 2)
        cmdNames = [s.__name__.replace('Commander', '') for s in selected]
        funcName = 'test_{}_{}_Bots{}'.format(os.path.splitext(level)[0].capitalize(), 'Vs'.join(cmdNames), count)
        setattr(TestLevels, funcName, runLevelTest(level, count, selected))

initialize()
