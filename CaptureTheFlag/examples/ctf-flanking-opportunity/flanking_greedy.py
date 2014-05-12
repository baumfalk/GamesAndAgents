from api import commander
from api import orders
from api.vector2 import Vector2


class GreedyCommander(commander.Commander):
    """This default AI implementation sends its bots on the shortest path.
    """

    def tick(self):
        for bot in self.game.bots_available:
            self.issue(orders.Charge, bot, self.game.enemyTeam.flag.position)

