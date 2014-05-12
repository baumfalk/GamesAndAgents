import math
from itertools import izip, tee

from api import commander
from api import orders
from api.vector2 import Vector2


def pairwise(iter):
    a, b = tee(iter)
    next(b, None)
    return izip(a, b)


class FlankingFloodFill(commander.Commander):
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

        d = (self.source - theirs).normalized()

        flanks = []

        for cell, dist in self.bfs(theirs):
            if dist < 5 or dist > 25:
                continue

            dirToCell = (cell - theirs).normalized()
            dp = d.dotProduct(dirToCell)

            if dp < 0 or dp > math.cos(math.pi/3.0):
                continue

            flanks.append((cell, dp))

        self.flank, dp = min(flanks, key=lambda x: x[0])
        self.target = theirs


    def tick(self):
        """Update the bots that have no commands yet, or who just finished. *dt* is not used here."""
        for bot in self.game.bots_available:
            path = [self.flank, self.target]
            path = self.getPathSubsetByProximity(bot, path)
            self.issue(orders.Charge, bot, path)


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


    def onGrid(self, cell):
        return cell.x >= 0.5 and cell.x < (self.level.width-0.5) and cell.y >= 0.5 and cell.y < (self.level.height - 0.5)


    def bfs(self, start):
        expanded = set()
        queue = [(Vector2(int(start.x) + 0.5, int(start.y) + 0.5), 0)]

        while len(queue) > 0:
            cell, length = queue.pop(0)

            yield cell, length

            for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nei = cell + Vector2(*offset)

                if (nei.x, nei.y) in expanded:
                    continue

                if not self.onGrid(nei):
                    continue

                if self.level.blockHeights[int(nei.x-0.5)][int(nei.y-0.5)] > 0.0:
                    continue

                expanded.add((nei.x, nei.y))

                queue.append((nei, length + 1))
