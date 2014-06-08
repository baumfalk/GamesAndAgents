"""
Keeps track of game statistics, such as the number of
kills, current score, and whether events just happened
this tick.
"""

class Statistics:
    """
    Initialises some fields, just to be sure.
    """
    def __init__(self):
        # Internal variables.
        self.commander = None
        self.eventCount = 0
        self.previousTime = 0
        self.time = 0
        self.previousTimeRemaining = 1000000
        self.timeRemaining = 1000000
        
        # Actual statistics.
        self.ourKills = 0
        self.theirKills = 0
        self.ourScore = 0
        self.theirScore = 0
        self.wePickedUp = False
        self.theyPickedUp = False
        self.weDropped = False
        self.theyDropped = False
        self.weCaptured = False
        self.theyCaptured = False
        self.weKilled = False
        self.theyKilled = False
        self.weRespawned = False
        self.theyRespawned = False
    
    def initialize(self,commander):
        self.commander = commander
    
    def tick(self):
        # Reset all event flags.
        self.wePickedUp = False
        self.theyPickedUp = False
        self.weDropped = False
        self.theyDropped = False
        self.weCaptured = False
        self.theyCaptured = False
        self.weKilled = False
        self.theyKilled = False
        self.weRespawned = False
        self.theyRespawned = False
        
        # Handle recent events.
        while len(self.commander.game.match.combatEvents) > self.eventCount:
            event = self.commander.game.match.combatEvents[self.eventCount]
            if event.type == event.TYPE_KILLED:
                if event.subject in self.commander.game.team.members:
                    self.ourKills += 1
                    self.weKilled = True
                else:
                    self.theirKills += 1
                    self.theyKilled = True
            elif event.type == event.TYPE_FLAG_PICKEDUP:
                if event.subject == self.commander.game.team.flag:
                    self.wePickedUp = True
                else:
                    self.theyPickedUp = True
            elif event.type == event.TYPE_FLAG_DROPPED:
                if event.subject == self.commander.game.team.flag:
                    self.weDropped = True
                else:
                    self.theyDropped = True
            elif event.type == event.TYPE_FLAG_CAPTURED:
                if event.subject == self.commander.game.team.flag:
                    self.weCaptured = True
                else:
                    self.theyCaptured = True
            #elif event.type == event.TYPE_FLAG_RESTORED:
                # No statistics to update about this yet.
            elif event.type == event.TYPE_RESPAWN:
                if event.subject in self.commander.game.team.members:
                    self.weRespawned = True
                else:
                    self.theyRespawned = True
            self.eventCount += 1
        
        # Update scores
        scores = self.commander.game.match.scores
        self.ourScore = scores[self.commander.game.team.name]
        self.theirScore = scores[self.commander.game.enemyTeam.name]
        
        # Update time (please execute this last)
        self.previousTime = self.time
        self.time = self.commander.game.match.timePassed
        self.previousTimeRemaining = self.timeRemaining
        self.timeRemaining = self.commander.game.match.timeRemaining
    
    def isCurrentTime(self,time):
        return time <= self.time and time > self.previousTime
    
    def isRemainingTime(self,time):
        return time >= self.timeRemaining and time < self.previousTimeRemaining