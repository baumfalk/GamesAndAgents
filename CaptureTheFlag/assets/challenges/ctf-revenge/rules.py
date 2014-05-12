
from ctf.events import CombatEvent
from ctf.challenges import ChallengeRules
from ctf.levelconfig import Challenge


class Rules(ChallengeRules):

    CHALLENGE_ID = "ctf-revenge"
    CHALLENGE_FILE = __file__

    @staticmethod
    def calculateIndividualScore(stats):
        if len(stats) == 0:
            return 0.0

        if stats['scores'][0] > stats['scores'][1]:
            return 100.0

        if stats['scores'][0] == stats['scores'][1]:
            return 50.0

        return 0.0


    def _onCombatKilledEvent(self, event):
        pass


    def initialize(self):
        self.scores = [0, 0]


    def getStatistics(self):
        return {'scores': self.scores}


    def onScoreChangedEvent(self, event):
        candidateScore = event.scores[self.candidateTeamName]
        teamNames = event.scores.keys()
        teamNames.remove(self.candidateTeamName)
        challengerScore = event.scores[teamNames[0]]
        self.scores = [candidateScore, challengerScore]
