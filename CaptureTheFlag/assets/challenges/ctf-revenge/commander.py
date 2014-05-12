import random
import os

from api import gameinfo
from api.commander import Commander
from api import orders
from api.vector2 import Vector2


class ChallengeCommander(Commander):
    """An example commander that has one bot attacking, one defending and the rest randomly searching the level for enemies"""

    def initialize(self):
        self.attacker = None
        self.defender = None
        self.verbose = False

        # Calculate flag positions and store the middle.
        ours = self.game.team.flag.position
        theirs = self.game.enemyTeam.flag.position
        self.middle = (theirs + ours) * 0.5

        # Now figure out the flaking directions, assumed perpendicular.
        d = (ours - theirs)
        self.left = Vector2(-d.y, d.x).normalized()
        self.right = Vector2(d.y, -d.x).normalized()
        self.front = Vector2(d.x, d.y).normalized()

        self.panicMode = False

    # Add the tick function, called each update
    # This is where you can do any logic and issue new orders.
    def tick(self):
        if self.attacker and self.attacker.health <= 0:
            # the attacker is dead we'll pick another when available
            self.attacker = None

        if self.defender and (self.defender.health <= 0 or self.defender.flag):
            # the defender is dead we'll pick another when available
            self.defender = None

        if not self.game.team.flag.carrier:
            self.panicMode = False
        else:
            if not self.panicMode:
                self.panicMode = True
                
                targetPosition = (self.game.team.flag.position + self.game.enemyTeam.flagScoreLocation) * 0.5
                targetMin = targetPosition - Vector2(6.0, 6.0)
                targetMax = targetPosition + Vector2(6.0, 6.0)
                goal = self.level.findRandomFreePositionInBox([targetMin, targetMax])
                    
                if goal:
                    for bot in self.game.bots_alive:           
                        if bot == self.defender or bot == self.attacker:
                            continue
                    
                        self.issue(orders.Attack, bot, goal, description = 'running to intercept', lookAt=targetPosition)
        
        # In this example we loop through all living bots without orders (self.game.bots_available)
        # All other bots will wander randomly
        for bot in self.game.bots_available:           
            if (self.defender == None or self.defender == bot) and not bot.flag:
                self.defender = bot

                # Stand on a random position in a box of 4m around the flag.             
                targetPosition = self.game.team.flag.position
                targetMin = targetPosition - Vector2(2.0, 2.0)
                targetMax = targetPosition + Vector2(2.0, 2.0)
                goal = self.level.findRandomFreePositionInBox([targetMin, targetMax])
                
                if not goal:
                    continue

                if (goal - bot.position).length() > 8.0:
                    self.issue(orders.Charge, self.defender, goal, description = 'running to defend')
                else:
                    self.issue(orders.Defend, self.defender, (self.middle - bot.position), description = 'turning to defend')

            elif self.attacker == None or self.attacker == bot or bot.flag:
                self.attacker = bot

                if bot.flag:
                    # Tell the flag carrier to run home!
                    target = self.game.team.flagScoreLocation
                    self.issue(orders.Charge, bot, target, description = 'running home')
                else:
                    target = self.game.enemyTeam.flag.position
                    flank = self.getFlankingPosition(bot, target)
                    if (target - flank).length() > (bot.position - target).length():
                        self.issue(orders.Attack, bot, target, description = 'attack from flank', lookAt=target)
                    else:
                        flank = self.level.findNearestFreePosition(flank)
                        self.issue(orders.Charge, bot, flank, description = 'running to flank')

            else:
                # All our other (random) bots

                # pick a random position in the level to move to                               
                halfBox = 0.4 * min(self.level.width, self.level.height) * Vector2(1, 1)
                
                target = self.level.findRandomFreePositionInBox((self.middle - halfBox, self.middle + halfBox))

                # issue the order
                if target:
                    self.issue(orders.Attack, bot, target, description = 'random patrol')

        for bot in self.game.bots_holding:
            target = self.level.findRandomFreePositionInBox((bot.position-5.0, bot.position+5.0))
            if target:
                self.issue(orders.Attack, bot, target, lookAt = random.choice([b.position for b in bot.visibleEnemies]))


    def getFlankingPosition(self, bot, target):
        """Return simple flanking positions calculated based on the flanking vectors.

        Args:
            bot (object): The bot for which to calculate the flanking position.
            target (vector2): The location that should be flanked.

        Returns:
            The calculated flanking position as a vector2 object.
        """
        flanks = [target + f * 16.0 for f in [self.left, self.right]]
        options = map(lambda f: self.level.findNearestFreePosition(f), flanks)
        return sorted(options, key = lambda p: (bot.position - p).length())[0]
