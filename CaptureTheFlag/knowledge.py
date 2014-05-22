"""
The knowledge base of a commander. This has a few
generic methods to track and find useful information
about the game that could help your commander.
"""

from api.gameinfo import BotInfo
from api.vector2 import Vector2
import sys

class Knowledge:
    """
    Initialises some fields, just to be sure.
    """
    def __init__(self):
        self.commander = None #The commander of our team (to get information from).
        self.teamSize = 0     #Number of bots in a team.
        self.lastTickTime = 0 #Time of previous tick (to measure the velocities of enemy bots).
        
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
        
        #Initialise the enemy bot locations at the centre of their spawn area.
        botSpawnArea = commander.game.enemyTeam.botSpawnArea
        self.avgEnemyBotSpawn = botSpawnArea[0] + botSpawnArea[1] / 2
        for bot in commander.game.enemyTeam.members:
            self.lastEnemyPositions[bot] = self.avgEnemyBotSpawn
            self.lastEnemyVelocities[bot] = Vector2(0,0) #Assume they are standing still there.
            self.enemyInView[bot] = False
        
        self.levelCentre = Vector2(self.commander.level.width / 2,self.commander.level.height / 2)
    
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
        self.enemyInView[theirbot] = False
        
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

        # Added these variables: Barend
        self.enemyBase = self.commander.game.enemyTeam.botSpawnArea
        if( not self.ourFlagCaptured):
            self.enemyCarrierPos = self.commander.game.team.flag.carrier
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
    def getMidsection(self,bot):
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
        if(self.commander.level.height - y < distToEdge):
            distToEdge = self.commander.level.height - y
            result = Vector2(x,self.commander.level.height)
        #Right edge
        if(self.commander.level.width - x < distToEdge):
            distToEdge = self.commander.level.width - x
            result = Vector2(self.commander.level.width,y)
        
        return result