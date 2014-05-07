from tests.helpers import *

import mycmd
import examples


class ScoreTests(TestSuite):

    def runCommander(self, commander):
        self.config.red.numberBots = 5
        self.config.red.commander = lambda nick, **kwargs: commander(nick, **kwargs)
        self.config.gameLength = 20.0
        self.config.endOfGameCallback = self.checkCommander

    def checkCommander(self, state, commanders):
        assert state.teams["Red"].score > 0
        assert state.teams["Blue"].score == 0
        for commander in commanders:
            assert scoresAccordingToCommander(commander) == {name: team.score for name, team in state.teams.items()}


def subclasses(cls):
    """Scan for derived classes so they can be picked up automatically without manual annotations...
    """
    children = cls.__subclasses__()
    if len(children) == 0:
        return [cls]

    result = []
    for item in children:
        result.extend(subclasses(item))
    return result


def initialize():
    """Extend the test case above with custom methods for interesting commanders.  The resulting class will be picked
    up by `unittest` automatically.
    """
    for commander in subclasses(api.commander.Commander):
        if commander.__name__ in ['NetworkCommander', 'ScriptedCommander', 'RandomCommander', 'ReplayCommander']:
            # Filter out commanders we know can't score, including internal commanders or those used for unit testing
            # less predictable commanders, or purposely buggy commanders.
            continue

        funcName = 'test_{}'.format(commander.__name__.replace('.', '_'))
        setattr(ScoreTests, funcName, lambda self: ScoreTests.runCommander(self, commander))

initialize()

