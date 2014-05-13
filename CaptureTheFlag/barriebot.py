"""A set of example Commanders with simple AI.
"""

import random
import os

from api import gameinfo
from api.commander import Commander
from api import orders
from api.vector2 import Vector2


def contains(area, position):
    start, finish = area
    return position.x >= start.x and position.y >= start.y and position.x <= finish.x and position.y <= finish.y


class BarrieCommander(Commander):
    """
    Barrie is the union of Jetze and Barend.
    """
    
    def initialize(self):
        self.verbose = True  
        
    def tick(self):
        """Process all the bots that are done with their orders and available for taking orders."""
        self.logInfo()
        # The 'bots_available' list is a dynamically calculated list of bots that are done with their orders.
        for bot in self.game.bots_available:
            # Determine a place to run randomly...
            target = random.choice(
                          # 1) Either a random choice of *current* flag locations, ours or theirs.
                          [f.position for f in self.game.flags.values()]
                          # 2) Or a random choice of the goal locations for returning flags.
                        + [s for s in self.level.flagScoreLocations.values()]
                          # 3) Or a random position in the entire level, one that's not blocked.
                        + [self.level.findRandomFreePositionInBox(self.level.area)]
            )
            # Pick random movement style between going fast or moving carefully.
            cmd = random.choice([orders.Attack, orders.Charge])
            if target:
                self.issue(cmd, bot, target, description = 'random')


        # These bots were given an Attack order, but encountered defensive resistance and are waiting...
        for bot in self.game.bots_holding:
            cmd = random.choice([orders.Attack, orders.Charge, None])
            params = {'description': 'random (after holding)'}

            # If attacking, pick an enemy and strafe around a bit to break the holding pattern. 
            if cmd == orders.Attack:
                params['lookAt'] = random.choice([b.position for b in bot.visibleEnemies])
                target = self.level.findRandomFreePositionInBox((bot.position-5.0, bot.position+5.0))

            # Can also charge one of the visible enemies to try to break the pattern...
            elif cmd == orders.Charge:
                target = random.choice([b.position for b in bot.visibleEnemies])

            if cmd and target:
                self.issue(cmd, bot, target, **params)
    

    def logInfo(self):
        scoreDict = self.game.match.scores
        ourScore = scoreDict[self.game.team.name]
        theirScore = scoreDict[self.game.enemyTeam.name]
        
        events = self.game.match.combatEvents
        
        self.log.info("#")
        self.log.info("Our Score:"+str(ourScore))
        self.log.info("Their Score:"+str(theirScore))
       # self.log.info("combatEvents:"+str(events))

    def shutdown(self):
        scoreDict = self.game.match.scores
        ourScore = scoreDict[self.game.team.name]
        theirScore = scoreDict[self.game.enemyTeam.name]
        self.log.info("HI shutdown")
        self.log.info("Our Score:"+str(ourScore))
        self.log.info("Their Score:"+str(theirScore))
        #random statistics

        #team effectivity:
        #score
    
        #number of captures
        #number of teamwipes of enemy
        #gamelength
        #respawntime
        #enemy flag carrier killed
        
        #bot effectivity:
        #for each bot: number of deaths
        #for each bot: kills
        #for each bot: deaths
        #for each bot: idle time
        #for each bot: captures
        
        self.log.info("test")