import random
from itertools import izip, tee

from api import commander
from api import orders
from api.vector2 import Vector2


def pairwise(iter):
    a, b = tee(iter)
    next(b, None)
    return izip(a, b)


class FlankingVectorCommander(commander.Commander):
    """
    Uses vector math to calculate flanking approach points.
    """

    def initialize(self):
        """Perform minor initializations like calculating flanking vectors. based on flag positions"""

        # First calculate flag positions and store the middle.
        base = self.game.team.botSpawnArea
        self.source = (base[0] + base[1]) / 2.0

        theirs = self.game.enemyTeam.flag.position
        self.middle = (theirs + self.source) / 2.0

        # Now figure out the flaking directions, assumed perpendicular.
        d = (theirs - self.source) / 2.5
        self.flank = random.choice([Vector2(-d.y, d.x), Vector2(d.y, -d.x)])


    def tick(self):
        """Update the bots that have no commands yet, or who just finished. *dt* is not used here."""

        for bot in self.game.bots_available:

            target = self.game.enemyTeam.flag.position

            # Regroup on the flank and attack slowly...
            if (target+self.flank - bot.position).length() < 5.0:
                self.issue(orders.Attack, bot, target)
                continue

            # Tell  bots to run to the flag via an arbitrary flank...
            path = [self.source, self.middle + self.flank, target + self.flank, target]
            path = self.getPathSubsetByProximity(bot, path)
            # Don't actually go to the target, stop at the nearby flank.
            del path[-1]

            if len(path) == 0: # In this case, attack was already underway!
                self.issue(orders.Attack, bot, target)
                self.log.info('Attack (direct): %s', target)
            else:
                self.issue(orders.Charge, bot, path)
                self.log.info('Running (path): %s', path)


    def getPathSubsetByProximity(self, bot, corridor):
        distances = [(bot.position - p).length() for p in corridor]
        spans = [(t - s).length() for s, t in pairwise([bot.position] + corridor)]

        path = []
        for p, dist, span in zip(corridor, distances, spans):
            p = self.level.findNearestFreePosition(p)
            if dist < span:
                path = [p]
            else:
                path.append(p)
        return path

