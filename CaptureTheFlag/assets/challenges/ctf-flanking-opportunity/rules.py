
from ctf.events import CombatEvent
from ctf.challenges import ChallengeRules
from ctf.levelconfig import Challenge


class Rules(ChallengeRules):

    CHALLENGE_ID = "ctf-flanking-opportunity"
    CHALLENGE_FILE = __file__


    @staticmethod
    def calculateIndividualScore(stats):
        if len(stats) == 0:
            return 0.0

        total = 0.0
        if stats['elapsed'] != 'N/A':
            total += 0.5 * (100.0 - stats['elapsed'])
            total += 10.0 * (4 - stats['losses'])
        total += 2.5 * stats['hits']
        return total


    def onCombatEvent(self, event):
        if event.type == CombatEvent.TYPE_FLAG_PICKEDUP:
            self.elapsed = self.gameState.timePassed
            self._terminate()
