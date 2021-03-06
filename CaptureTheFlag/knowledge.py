"""
The knowledge base of a commander. This has a few
generic methods to track and find useful information
about the game that could help your commander.
"""

from api.gameinfo import BotInfo
from api.vector2 import Vector2
import random
import sys

class Knowledge:
    """
    Initialises some fields, just to be sure.
    """
    def __init__(self):
        self.commander = None #The commander of our team (to get information from).
        self.teamSize = 0     #Number of bots in a team.
        self.lastTickTime = 0 #Time of previous tick (to measure the velocities of enemy bots).

        self.level = None     # level information
        self.lastEnemyPositions = {}         #Last seen locations of enemy bots.
        self.lastEnemyVelocities = {}        #Last measured velocities of enemy bots.
        self.enemyInView = {}                #Whether an enemy bot is currently in view.
        self.avgEnemyBotSpawn = Vector2(0,0) #Centre of the enemy spawn area.
        self.levelCentre = Vector2(0,0)      #Centre of the entire level.
        self.ourFlagCaptured = False         #Our flag is currently being carried by the enemy.

    """
    Call this after the game has been initialised.
    It will fill some fields with initial info.
    """
    def initialize(self,commander):
        self.commander = commander
        self.teamSize = len(commander.game.enemyTeam.members) #Assuming team sizes are equal at init.
        self.level = self.commander.level
        #Initialise the enemy bot locations at the centre of their spawn area.
        botSpawnArea = commander.game.enemyTeam.botSpawnArea
        self.avgEnemyBotSpawn = botSpawnArea[0] + botSpawnArea[1] / 2
        for bot in commander.game.enemyTeam.members:
            self.lastEnemyPositions[bot] = self.avgEnemyBotSpawn
            self.lastEnemyVelocities[bot] = Vector2(0,0) #Assume they are standing still there.
            self.enemyInView[bot] = False
        self.levelCentre = Vector2(self.level.width / 2,self.level.height / 2)
    
    """
    Call this at every tick of the game. It will
    update the knowledge base by making new
    observations.
    To make further queries to this knowledge base
    more accurate, this method should be called at
    the beginning of a tick.
    """
    def tick(self):
        wasInView = {}
        for theirbot in self.enemyInView.keys():
            wasInView[theirbot] = self.enemyInView[theirbot]
        self.enemyInView[theirbot] = False # <-- should that be indented?
        
        for mybot in self.commander.game.bots_alive:
            for theirbot in mybot.visibleEnemies:
                self.enemyInView[theirbot] = True
                if(wasInView[theirbot]): #Enemy was in view last tick, so we can estimate its speed with the difference in position
                    self.lastEnemyVelocities[theirbot] = (theirbot.position - self.lastEnemyPositions[theirbot]) / (self.commander.game.match.timePassed - self.lastTickTime)
                else: #Use their orientation. Less reliable.
                    if(theirbot.state == BotInfo.STATE_UNKNOWN | theirbot.state == BotInfo.STATE_IDLE | theirbot.state == BotInfo.STATE_DEFENDING | theirbot.state == BotInfo.STATE_TAKINGORDERS | theirbot.state == BotInfo.STATE_HOLDING):
                        self.lastEnemyVelocities[theirbot] = Vector2(0,0)
                    elif(theirbot.state == BotInfo.STATE_MOVING | theirbot.state == BotInfo.STATE_ATTACKING):
                        self.lastEnemyVelocities[theirbot] = theirbot.facingDirection * self.commander.level.walkingSpeed
                    elif(theirbot.state == BotInfo.STATE_CHARGING):
                        self.lastEnemyVelocities[theirbot] = theirbot.facingDirection * self.commander.level.runningSpeed
                    elif(theirbot.state == BotInfo.STATE_DEAD): #Treat the dead as if they already respawned.
                        self.lastEnemyVelocities[theirbot] = Vector2(0,0)
                        self.lastEnemyPositions[theirbot] = self.avgEnemyBotSpawn
                    else:
                        self.lastEnemyVelocities[theirbot] = Vector2(0,0)
                if(theirbot.state != BotInfo.STATE_DEAD): #If dead, their position was already changed.
                    self.lastEnemyPositions[theirbot] = theirbot.position
        
        self.lastTickTime = self.commander.game.match.timePassed
        
        self.ourFlagCaptured = self.commander.game.team.flag.carrier != None
        self.theirFlagCaptured = self.commander.game.enemyTeam.flag.carrier != None

        # Added these variables: Barend
        self.enemyBase = self.commander.game.enemyTeam.botSpawnArea[0] #LOL
        if( not self.ourFlagCaptured and self.commander.game.team.flag.carrier != None ):
            self.enemyCarrierPos = self.commander.game.team.flag.carrier.position
        if(self.commander.game.team.flag.position == self.commander.game.team.flagSpawnLocation):
            self.flagInBase = True
        self.flagDroppedInField =  (not self.flagInBase and not self.ourFlagCaptured)
    
    """
    Attempts to predict the current position of a
    specific bot, whether or not it is in view. It does
    this by taking the last known position and velocity
    of the bot and extrapolating the velocity from that
    position.
    """
    def predictPosition(self,bot):
        if(self.lastEnemyPositions.has_key(bot)):
            return self.lastEnemyPositions[bot] + self.lastEnemyVelocities[bot] * bot.seenlast
        else:
            return bot.position
    
    """
    Predict which enemy bot is closest to the given bot.
    You can then get the position by calling:
    predictPosition(predictNearestBot(mybot))
    """
    def predictNearestEnemy(self,mybot):
        myPosition = mybot.position
        nearestBot = None
        nearestDistance = sys.float_info.max
        for bot in self.lastEnemyPositions.keys():
            distance = mybot.position.distance(self.predictPosition(bot))
            if(distance < nearestDistance):
                nearestBot = bot
                nearestDistance = distance
        
        return nearestBot
    
    """
    Predict the average position of the enemy team.
    """
    def predictAverageEnemyPosition(self):
        avgPosition = Vector2(0,0)
        for bot in self.lastEnemyPositions.keys():
            avgPosition += self.predictPosition(bot)
        return avgPosition / self.teamSize
    
    """
    Returns the average position of our entire team.
    """
    def teamAveragePosition(self):
        avgPosition = Vector2(0,0)
        for bot in self.commander.game.team.members:
            avgPosition += bot.position
        return avgPosition / self.teamSize
    
	"""
    Returns the score of our team
    """
    def teamOurScore(self):
        scoreDict = self.commander.game.match.scores
        myScore = scoreDict[self.commander.game.team.name]
        return myScore
		
	"""
    Returns the score of the enemy team
    """
    def teamEnemyScore(self):
        scoreDict = self.commander.game.match.scores
        enemyScore = scoreDict[self.commander.game.enemyTeam.name]
        return enemyScore	
	
    """
    Returns which bot from our team is closest to the
    specified bot.
    """
    def teamNearestFriend(self,mybot):
        myPosition = mybot.position
        nearestBot = None
        nearestDistance = sys.float_info.max
        for bot in self.commander.game.team.members:
            if(bot != mybot):
                distance = mybot.position.distance(bot.position)
                if(distance < nearestDistance):
                    nearestBot = bot
                    nearestDistance = distance
        
        return nearestBot
    
    """
    Returns whether a certain bot (enemy or friendly) is
    in the middle area of the level.
    """
    def atMidsection(self,bot):
        return self.predictPosition(bot).distance(self.levelCentre) < self.commander.level.width / 2


    # Added this rule: Barend
    """
    Returns the location of the middle of your flag stand and the enemy flag return point. 
    """
    def getMidsection(self):
        return (self.commander.game.enemyTeam.flagScoreLocation + self.commander.game.team.flagSpawnLocation / 2)
    
    """
    Returns the position nearest to the edge of the level
    to a bot.
    """
    def nearestSideEdge(self,bot):
        x = bot.position.x
        y = bot.position.y
        botPos = self.predictPosition(bot)
        #Top edge
        distToEdge = y
        result = Vector2(x,0)
        #Left edge
        if(x < distToEdge):
            distToEdge = x
            result = Vector2(0,y)
        #Bottom edge
        if(self.level.height - y < distToEdge):
            distToEdge = self.level.height - y
            result = Vector2(x,self.level.height)
        #Right edge
        if(self.level.width - x < distToEdge):
            distToEdge = self.level.width - x
            result = Vector2(self.level.width,y)
        
        #Take some distance from the edge of the level.
        if distToEdge > self.commander.level.firingDistance: #But don't go walking further away from the edge either.
            diff = bot.position - result
            diff = diff.normalized() * self.commander.level.firingDistance
            result += diff
        
        return result

    def getSign(self,start,target):
        import math
        return math.copysign(1, target-start)

    def createShortFlankingPath(self,botPos,target):
        # if they have same x then they differ in the y coordinate thus the one is up and the other is down :P
        if(abs(botPos.x - target.x)<=abs(botPos.y - target.y)):
            # relative positions between bot and target
            # its either up and down or right and left, depending on that the capper
            # approaches in a different way
            upDown = True
            # 1 or -1 depending on the scoring pos and enemy flag spawn pos
            # want to know if we are going up or down the x or y coords when going to flag or back
            # in order to build the path
            middlesign = self.getSign(botPos.y,target.y)
        else:
            upDown = False
            middlesign = self.getSign(botPos.x,target.x)
        middle = botPos.midPoint(target)
        if (not upDown):
            # find closest side
            if self.level.height - botPos.y > self.level.height/2:
                path = [
                        self.commander.level.findNearestFreePosition(Vector2(middle.x - (middlesign*middle.x)/2,5)),
                         self.commander.level.findNearestFreePosition(Vector2(middle.x,5)),
                         self.commander.level.findNearestFreePosition(Vector2(middle.x + (middlesign*middle.x)/2,5)),
                         target,
                         self.commander.level.findRandomFreePositionInBox([target-2.5,target+2.5])
                         ]
            else:
                path = [ self.commander.level.findNearestFreePosition(Vector2(middle.x - (middlesign*middle.x)/2,self.level.height-5)),
                         self.commander.level.findNearestFreePosition(Vector2(middle.x,self.level.height-5)),
                         self.commander.level.findNearestFreePosition(Vector2(middle.x + (middlesign*middle.x)/2,self.level.height-5)),
                         target,
                         self.commander.level.findRandomFreePositionInBox([target-2.5,target+2.5])
                        ]
        else:
            # find closest side
            if self.level.width - botPos.x > self.level.width/2:
                    path = [ self.commander.level.findNearestFreePosition(Vector2(5,middle.y - (middlesign*middle.y)/2)),
                         self.commander.level.findNearestFreePosition(Vector2(5,middle.y)),
                         self.commander.level.findNearestFreePosition(Vector2(5,middle.y + (middlesign*middle.y)/2)),
                         target,
                         self.commander.level.findRandomFreePositionInBox([target-2.5,target+2.5])
                    ]
            else:
                path = [self.commander.level.findNearestFreePosition(Vector2(self.level.width-5,middle.y - (middlesign*middle.y)/2)),
                         self.commander.level.findNearestFreePosition(Vector2(self.level.width-5,middle.y)),
                         self.commander.level.findNearestFreePosition(Vector2(self.level.width-5,middle.y + (middlesign*middle.y)/2)),
                         target,
                         self.commander.level.findRandomFreePositionInBox([target-2.5,target+2.5])
                    ]
        # in case the capper has picked the flag from a fallen capper and the flag is near
        # the scoring base then it is better to approach straight away
        while True:
            if botPos.squaredDistance(path[0]) > botPos.squaredDistance(path[-1]):
                path = [path[-1]]
                break
            elif len(path) > 2 and Vector2.distance(botPos,path[-1]) < Vector2.distance(path[0],path[-1]):
                path.pop(0)
            else:
                break

        return path

    def createLongFlankingPath(self,botPos,target):
         # if they have same x then they differ in the y coordinate thus the one is up and the other is down :P
        if(abs(botPos.x - target.x)<=abs(botPos.y - target.y)):
            # relative positions between bot and target
            # its either up and down or right and left, depending on that the capper
            # approaches in a different way
            upDown = True
            # 1 or -1 depending on the scoring pos and enemy flag spawn pos
            # want to know if we are going up or down the x or y coords when going to flag or back
            # in order to build the path
            middlesign = self.getSign(botPos.y,target.y)
        else:
            upDown = False
            middlesign = self.getSign(botPos.x,target.x)
        middle = botPos.midPoint(target)
        if (not upDown):
            # find furthest side
            if self.level.height - botPos.y < self.level.height/2:
                path = [self.commander.level.findNearestFreePosition(Vector2(middle.x - (middlesign*middle.x)/2,5)),
                             self.commander.level.findNearestFreePosition(Vector2(middle.x,5)),
                             self.commander.level.findNearestFreePosition(Vector2(middle.x + (middlesign*middle.x)/2,5)),
                             target,
                             self.commander.level.findRandomFreePositionInBox([target-2.5,target+2.5])
                        ]
            else:
                path = [ self.commander.level.findNearestFreePosition(Vector2(middle.x - (middlesign*middle.x)/2,self.level.height-5)),
                             self.commander.level.findNearestFreePosition(Vector2(middle.x,self.level.height-5)),
                             self.commander.level.findNearestFreePosition(Vector2(middle.x + (middlesign*middle.x)/2,self.level.height-5)),
                             target,
                             self.commander.level.findRandomFreePositionInBox([target-2.5,target+2.5])
                            ]
        else:
            # find furthest side
            if self.level.width - botPos.x < self.level.width/2:
                path = [ self.commander.level.findNearestFreePosition(Vector2(5,middle.y - (middlesign*middle.y)/2)),
                             self.commander.level.findNearestFreePosition(Vector2(5,middle.y)),
                             self.commander.level.findNearestFreePosition(Vector2(5,middle.y + (middlesign*middle.y)/2)),
                             target,
                             self.commander.level.findRandomFreePositionInBox([target-2.5,target+2.5])
                        ]
            else:
                path = [ self.commander.level.findNearestFreePosition(Vector2(self.level.width-5,middle.y - (middlesign*middle.y)/2)),
                             self.commander.level.findNearestFreePosition(Vector2(self.level.width-5,middle.y)),
                             self.commander.level.findNearestFreePosition(Vector2(self.level.width-5,middle.y + (middlesign*middle.y)/2)),
                             target,
                             self.commander.level.findRandomFreePositionInBox([target-2.5,target+2.5])
                        ]
            # in case the capper has picked the flag from a fallen capper and the flag is near
            # the scoring base then it is better to approach straight away
        while True:
            if botPos.squaredDistance(path[0]) > botPos.squaredDistance(path[-1]):
                path = [path[-1]]
                break
            elif len(path) > 2 and Vector2.distance(botPos,path[-1]) < Vector2.distance(path[0],path[-1]):
                path.pop(0)
            else:
                break

        return path
    
    """
    Returns a random direction vector.
    """
    def randomDirection(self):
        while(True):
            result = Vector2(random.random() * 2 - 1,random.random() * 2 - 1)
            if(result.length() <= 1):
                break
        result.normalize()
        return result
    
    """
    Finds a camping spot that has the specified position
    in its visor. Useful for defending a specific tactical
    location. Finds a secluded spot with lots of cover.
    """
    def findCampSpot(self,target):
        maxdist = int(self.level.firingDistance) - 2
        bestSpot = None
        bestCover = -1
        for x in range(-maxdist,maxdist):
            for y in range(-maxdist,maxdist):
                candidate = Vector2(x,y) + target
                intx = int(round(candidate.x))
                inty = int(round(candidate.y))
                if not self.isInLevel(candidate): #Not in level.
                    continue
                if intx >= len(self.level.blockHeights) or inty >= len(self.level.blockHeights[intx]): #Rounded is not in level
                    continue
                if Vector2(x,y).length() > maxdist: #Too far.
                    continue
                if self.level.blockHeights[intx][inty] > 0: #Can't move here.
                    continue
                if not self.canShootTo(target,candidate): #Vision is obstructed from here.
                    continue
                #Count the number of blocks that provide cover.
                cover = 0
                if intx + 1 >= len(self.level.blockHeights) or self.level.blockHeights[intx + 1][inty] > 1.5:
                    cover += 1
                if inty - 1 < 0 or self.level.blockHeights[intx][inty - 1] > 1.5:
                    cover += 1
                if intx - 1 < 0 or self.level.blockHeights[intx - 1][inty] > 1.5:
                    cover += 1
                if inty + 1 >= len(self.level.blockHeights[intx]) or self.level.blockHeights[intx][inty + 1] > 1.5:
                    cover += 1
                if cover > bestCover:
                    bestCover = cover
                    bestSpot = candidate
        if bestSpot == None:
            return target
        return bestSpot
    
    """
    Checks whether there is line of sight for firing
    to a target position from  a certain location
    """
    def canShootTo(self,target,origin):
        targetDistance = origin.distance(target)
        if targetDistance < 0.1:
            return True
        smallDiff = target - origin
        smallDiff.normalize()
        smallDiff = smallDiff * 0.1
        canShoot = True
        pos = origin
        posx = int(round(pos.x))
        posy = int(round(pos.y))
        while pos.distance(origin) < targetDistance and canShoot and self.isInLevel(pos) and posx < len(self.level.blockHeights) and posy < len(self.level.blockHeights[posx]):
            if self.level.blockHeights[posx][posy] > 1.5:
                canShoot = False
            pos += smallDiff
            posx = int(round(pos.x))
            posy = int(round(pos.y))
        return canShoot
    
    """
    Returns whether a position vector is in the level bounds.
    """
    def isInLevel(self,position):
        return position.x > 0 and position.y > 0 and position.x < self.level.width and position.y < self.level.height
    
    def isFree(self,position):
        if int(position.x) >= len(self.level.blockHeights):
            return False
        if int(position.y) >= len(self.level.blockHeights[int(position.x)]):
            return False
        return self.level.blockHeights[int(position.x)][int(position.y)] <= 0

    """
    Finds a close spot that has the specified position in
    its visor. Useful for defending or attacking a target
    quickly.
    """
    def findCloseSpot(self,target,botPosition):
        maxdist = int(self.level.firingDistance) - 2
        bestSpot = None
        bestDistance = -1
        for x in range(-maxdist,maxdist):
            for y in range(-maxdist,maxdist):
                candidate = Vector2(x,y) + target
                intx = int(round(candidate.x))
                inty = int(round(candidate.y))
                if not self.isInLevel(candidate): #Not in level.
                    continue
                if intx >= len(self.level.blockHeights) or inty >= len(self.level.blockHeights[intx]): #Rounded is not in level
                    continue
                if Vector2(x,y).length() > maxdist: #Too far.
                    continue
                if self.level.blockHeights[intx][inty] > 0: #Can't move here.
                    continue
                if not self.canShootTo(target,candidate): #Vision is obstructed from here.
                    continue
                #Count the number of blocks that provide cover.
                distance = botPosition.distance(candidate)
                if distance < bestDistance:
                    bestDistance = cover
                    bestSpot = candidate
        if bestSpot == None:
            return target
        return bestSpot