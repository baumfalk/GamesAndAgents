
from ctf.events import CombatEvent
from ctf.challenges import ChallengeRules
from ctf.levelconfig import Challenge
from ctf.gameconfig import GameConfig


GameConfig.ORDER_DELAY = 0
GameConfig.ORDER_FROM_IDLE_DELAY = 0
GameConfig.ORDER_DEFEND_DELAY = 0
GameConfig.ORDER_REPEAT_ORDER_DELAY = 0
GameConfig.ORDER_HOLDING_DELAY = 0


class Rules(ChallengeRules):

    CHALLENGE_ID = "ctf-operation-dragnet"
    CHALLENGE_FILE = __file__


    def __init__(self, cmdName, evtDisp):
        super(Rules, self).__init__(cmdName, evtDisp)
        self.distances = {}
        self.seenTimes = {}


    @staticmethod
    def configure(cls, config):
        pass


    def getStatistics(self):
        stats = {}
        stats['elapsed'] = self.seenTimes.values()

        # TODO: Track proximity to help beginners improve.
        # stats['distances'] = self.distances.values()
        return stats


    @staticmethod
    def calculateIndividualScore(stats):
        if len(stats) == 0:
            return 0.0

        ranges = [(0.0, 25.0), (10.0, 25.0), (45.0, 15.0), (90.0, 10.0), (120.0, 5.0)]

        result = 0.0
        for timestamp in stats['elapsed']:
            for (t1, p1), (t2, p2) in zip(ranges, ranges[1:]):
                if timestamp >= t1 and timestamp < t2:
                    k = (timestamp - t1) / (t2 - t1)
                    result += p1 * (1.0-k) + p2 * (k)
                    break

        return result


    def onPerceivedEvent(self, event):
        name = event.whom.characterComponent.name
        team = event.whom.characterComponent.team

        if team.name != self.candidateTeamName and name not in self.seenTimes:
            self.seenTimes[name] = self.gameState.timePassed
            # self.distances[name] = 'N/A'

        if len(self.seenTimes) == len(team.members):
            self._terminate()

