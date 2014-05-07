#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

from aisbx import game



class CaptureTheFlagGameState(game.GameState):
    """The model (data) for the Capture The Flag game.

    This data-structure stores variables about the current game (i.e. a 
    blackboard), and is a container for the state of individual entities too, 
    for example the bots or flags.  The game state also serves as a central
    event dispatcher for important notifications.
    """

    def __init__(self, world):
        super(CaptureTheFlagGameState, self).__init__()
        self.world = world


    def reset(self):
        super(CaptureTheFlagGameState, self).reset()

        self.teams = {}                #: Map of team names to team.Team
        self.bots = {}                 #: Map of bot names to character.CharacterComponent
        self.allBots = set()           #: Set of all the bots
        self.flags = {}                #: Map of flag names to flag.FlagState
        self.weapons = {}              #: Map of weapon names to weapon.Weapon
        self.timePassed = 0.0          #: Time since the start of the game
        self.gameTimer = 0.0           #: Time remaining in this game
        self.respawnTimer = 0.0        #: Time until the next respawn wave


    def addTeam(self, team):
        self.teams[team.name] = team


    def addBot(self, bot):
        self.bots[bot.name] = bot
        self.allBots.add(bot)


    def addFlag(self, flag):
        self.flags[flag.name] = flag


    def addWeapon(self, weapon):
        self.weapons[weapon.name] = weapon


    def getEnemyBots(self, ofTeam):
        return self.allBots - ofTeam.members
