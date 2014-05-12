#==============================================================================
# This file is part of The AI Sandbox.
# Copyright (c) 2012-2013, AiGameDev.com
#==============================================================================

"""Various classes that provide runtime information on the current match.
"""

import random

from api.vector2 import Vector2


class LevelInfo(object):
    """Provides information about the level the game is played in.
    """

    def __init__(self):
        super(LevelInfo, self).__init__()

        self.width = 0                 #: The width of world grid.
        self.height = 0                #: The height of world grid.

        #: 2d list describing the size of block at each position in world, 0 if there is no block at this position
        self.blockHeights = [[]]
        """:type: list[list[int]]"""

        #: A list of the team names supported by this level, for example 'Red' and 'Blue'.
        self.teamNames = []
        """:type: list[str]"""

        #: Map of team name the spawn location (Vector2) of the team's flag.
        self.flagSpawnLocations = {}
        """:type: dict[str, api.vector2.Vector2]"""

        self.flagScoreLocations = {}   #: Map of team name the location (Vector2) the flag must be taken to score.
        """:type: dict[str, api.vector2.Vector2]"""

        self.botSpawnAreas = {}        #: Map of team name the extents (Vector2, Vector2) of each team's bot spawn area.
        """:type: dict[str, (api.vector2.Vector2, api.vector2.Vector2)]"""

        #: The visibility angles of the bots in each of the different bot states.  The possible values for
        #: the states are integers, with helper enumerations defined in BotInfo.
        self.fieldOfViewAngles = []
        """:type: dict[int, float]"""

        self.characterRadius = 0.0     #: The radius of the character.
        self.firingDistance = 0.0      #: The maximum firing distance of the bots.
        self.walkingSpeed = 0.0        #: The walking speed of the bots.
        self.runningSpeed = 0.0        #: The running speed of the bots.

        self.gameLength = 0.0          #: The length (seconds) of the game.

        self.initializationTime = 0.0  #: The time (seconds) allowed for bot initialization before the start of the game.

        self.respawnTime = 0.0         #: The time (seconds) between bot respawns.


    def clamp(self, x, minValue, maxValue):
        """Clamp the given value between min and max.
        """
        return max(minValue, min(x, maxValue))


    def findRandomFreePositionInBox(self, area):
        """Find a random position for a character to move to in an area.
        None is returned if no position could be found.

        Arguments:
            area: The area in which we want to search for a random free position.

        Returns:
            A randomly chosen free position in the level as a Vector2.

        :type area: (api.vector2.Vector2, api.vector2.Vector2)
        :rtype: api.vector2.Vector2
        """
        minX, minY = self.clamp(area[0].x, 0, self.width-1), self.clamp(area[0].y, 0, self.height-1)
        maxX, maxY = self.clamp(area[1].x, 0, self.width-1), self.clamp(area[1].y, 0, self.height-1)
        rangeX, rangeY = maxX - minX, maxY - minY

        if (rangeX <= 0.0) or (rangeY <= 0.0):
            return None

        # pad the radius a little to ensure that the point is okay even after floating point errors
        # introduced by sending this value across the network to the game server
        radius = self.characterRadius + 0.01

        for i in range(0, 100):
            x, y = random.random() * rangeX + minX, random.random() * rangeY + minY
            ix, iy = int(x), int(y)
            # check if there are any blocks under current position
            if self.blockHeights[ix][iy] > 0:
                continue
            # check if there are any blocks in the four cardinal directions
            if (x - ix) < radius and ix > 0 and self.blockHeights[ix-1][iy] > 0:
                continue
            if (ix + 1 - x) < radius and ix < self.width - 1 and self.blockHeights[ix+1][iy] > 0:
                continue
            if (y - iy) < radius and iy > 0 and self.blockHeights[ix][iy-1] > 0:
                continue
            if (iy + 1 - y) < radius and iy < self.height - 1 and self.blockHeights[ix][iy+1] > 0:
                continue
            # check if there are any blocks in the four diagonals
            if (x - ix) < radius and (y - iy) < radius and ix > 0 and iy > 0 and self.blockHeights[ix-1][iy-1] > 0:
                continue
            if (ix + 1 - x) < radius and (y - iy) < radius and ix < self.width - 1 and iy > 0 and self.blockHeights[ix+1][iy-1] > 0:
                continue
            if (x - ix) < radius and (iy + 1 - y) < radius and ix > 0 and iy < self.height - 1 and self.blockHeights[ix-1][iy+1] > 0:
                continue
            if (ix + 1 - x) < radius and (iy + 1 - y) < radius and ix < self.width - 1 and iy < self.height - 1 and self.blockHeights[ix+1][iy+1] > 0:
                continue
            return Vector2(x, y)
        return None


    def findNearestFreePosition(self, target):
        """Find a free position near 'target' for a character to move to.
        None is returned if no position could be found.

        Arguments:
            target: Try to find a free position as close to this location as possible

        :type target: api.vector2.Vector2
        """
        for r in range(1, 100):
            areaMin = Vector2(target.x - r, target.y - r)
            areaMax = Vector2(target.x + r, target.y + r)
            position = self.findRandomFreePositionInBox((areaMin, areaMax))
            if position:
                return position
        return None

    @property
    def area(self):
        """Return the full area of the world.
        This can be used with findRandomFreePositionInBox to find a random position in the world.
        e.g. `levelInfo.findRandomFreePositionInBox(levelInfo.area)`
        """
        return (Vector2.ZERO, Vector2(self.width, self.height))


class GameInfo(object):
    """All of the filtered read-only information about the current game state.
    This shouldn't be modified. Modifying it will only hurt yourself.
    Updated each frame to show the current known information about the world.
    """
    
    def __init__(self):
        super(GameInfo, self).__init__()

        self.match = None              #: Match information object with current state of high-level game.
        """:type: api.gameinfo.MatchInfo"""

        self.teams = {}                #: The dictionary containing the TeamInfo object for each team indexed by team name.
        """:type: dict[str, api.gameinfo.TeamInfo]"""

        self.team = None               #: The TeamInfo object describing your own team.
        """:type: api.gameinfo.TeamInfo"""

        self.enemyTeam = None          #: The TeamInfo object describing the enemy team.
        """:type: api.gameinfo.TeamInfo"""

        self.bots = {}                 #: The dictionary containing the BotInfo object for each bot indexed by bot name.
        """:type: dict[str, api.gameinfo.BotInfo]"""

        self.flags = {}                #: The dictionary containing the FlagInfo object for each flag indexed by flag name
        """:type: dict[str, api.gameinfo.FlagInfo]"""


    @property
    def bots_alive(self):
        """The list of all bots in this team that are currently alive.
        """
        return [b for b in self.team.members if b.health > 0]

    @property
    def bots_available(self):
        """The list of all bots in this team that are currently alive and not doing an action.
        """
        return [b for b in self.bots_alive if b.state == BotInfo.STATE_IDLE]

    @property
    def bots_holding(self):
        """The list of the attacking bots in this team that are deadlocked by defenders.
        """
        return [b for b in self.bots_alive if b.state == BotInfo.STATE_HOLDING]

    @property
    def enemyFlags(self):
        """Returns a list of FlagInfo objects for all enemy flags. Set up to support more than one enemy team
        """
        return [f for f in self.flags.values() if f.team != self.team]


class TeamInfo(object):
    """Information about the current team including ids of all of the members of the team
    """

    def __init__(self, name):
        super(TeamInfo, self).__init__()

        #: The name of the team, for example Red or Blue.
        self.name = name

        #: A list of the BotInfo objects for each member of the team
        self.members = []
        """:type: list[api.gameinfo.BotInfo]"""

        #: The FlagInfo object for this team's flag.
        self.flag = None
        """:type: api.gameinfo.FlagInfo"""

        #: The position (Vector2) where the team must return an enemy flag to score a point.
        self.flagScoreLocation = None
        """:type: api.vector.Vector2"""

        #: The position (Vector2) where this team's flag is spawned.
        self.flagSpawnLocation = None
        """:type: api.vector.Vector2"""

        #: The min, max) extents (Vector2, Vector2) of each team's bot spawn area
        self.botSpawnArea = (Vector2.ZERO, Vector2.ZERO)
        """:type: (api.vector.Vector2, api.vector.Vector2)"""


    def __repr__(self):
        return "TeamInfo(name='{}')".format(self.name)


class FlagInfo(object):
    """Information about each of the flags.
    The positions of all flags are always known.
    If a flag is being carried the carrier is always known
    """

    def __init__(self, name):
        super(FlagInfo, self).__init__()

        self.name = name               #: The name of the flag
        self.position = Vector2.ZERO   #: The current position of the flag (always known)
        self.respawnTimer = 0          #: Time in seconds until a dropped flag is respawned at its spawn location

        #: The team that owns this flag, represented as a TeamInfo object.
        self.team = None
        """:type: api.gameinfo.TeamInfo | None"""

        #: The BotInfo object for the bot that is currently carrying the flag, None if it is not being carried.
        self.carrier = None
        """:type: api.gameinfo.BotInfo | None"""


    def __repr__(self):
        return "FlagInfo(name='{}')".format(self.name)


class BotInfo(object):
    """Information that you know about each of the bots.
    Enemy bots will contain information about the last time they were seen.
    Friendly bots will contain full information.
    """

    STATE_UNKNOWN      = 0             #: The current state of the bot is unknown. This state should never be seen by commanders.
    STATE_IDLE         = 1             #: The bot is not currently doing any actions. Auto-targeting is disabled.
    STATE_DEFENDING    = 2             #: The bot is defending. Auto-targeting is enabled.
    STATE_MOVING       = 3             #: The bot is moving. Auto-targeting is disabled.
    STATE_ATTACKING    = 4             #: The bot is attacking. Auto-targeting is enabled.
    STATE_CHARGING     = 5             #: The bot is charging. Auto-targeting is enabled.
    STATE_SHOOTING     = 6             #: The bot is shooting.
    STATE_TAKINGORDERS = 7             #: The bot is in a cooldown period after receiving an order. Auto-targeting is disabled.
    STATE_HOLDING      = 8             #: The bot was in an attacking state but its movement is blocked by the firing arc of an enemy. Auto-targeting is enabled.
    STATE_DEAD         = 9             #: The bot is dead.

    def __init__(self, name):
        super(BotInfo, self).__init__()

        self.name = name               #: The name of this bot
        self.team = None               #: The TeamInfo for the team that owns this bot
        """:type: api.gameinfo.TeamInfo"""

        self.seenlast = None           #: The time (seconds) since this bot was last seen. For friendly bots this is always 0.
        self.flag = None               #: The flag being carried by the bot, None if no flag is carried. This is always known for both friendly and enemy bots.
        """:type: api.gameinfo.FlagInfo | None"""

        self.health = None
        """The health of the bot. This is always known for friendly bots.
        For enemy bots this is the current state if the bot is dead or is visible by this commander. Otherwise, this is the last known health value.
        """

        #: The state/action of the bot. The possible states are:
        #: `STATE_UNKNOWN`, `STATE_IDLE`, `STATE_DEFENDING`, `STATE_MOVING`, `STATE_ATTACKING`,
        #: `STATE_CHARGING`, `STATE_SHOOTING`, `STATE_TAKINGORDERS`, `STATE_HOLDING`, `STATE_DEAD`.
        #: This is always known for friendly bots. For enemy bots this is the current state if
        #: the bot is dead or is visible by this commander. Otherwise, this is the last known state.
        self.state = BotInfo.STATE_UNKNOWN
        """:type: STATE_UNKNOWN | STATE_IDLE | STATE_DEFENDING | STATE_MOVING | STATE_ATTACKING | STATE_CHARGING | STATE_SHOOTING | STATE_TAKINGORDERS | STATE_HOLDING | STATE_DEAD"""

        #: The last known position (Vector2) of the bot.
        #: This is always known for friendly bots.
        #: For enemy bots this is the current state if the bot is dead or is visible by this commander.
        #: Otherwise, this is the last known position.
        self.position = None
        """:type: api.vector2.Vector2 | None"""

        #: The last known facing direction (Vector2) of the bot.
        #: This is always known for friendly bots.
        #: For enemy bots this is the current state if the bot is dead or is visible by this commander.
        #: Otherwise, this is the last known facing direction.
        self.facingDirection = None
        """:type: api.vector2.Vector2 | None"""

        #: List of BotInfo objects for enemies which are visible to this bot.
        #: For friendly bots the list will only include enemy bots which are visible by this commander.
        #: For enemy bots which are not visible by this commander, this will be an empty list.
        self.visibleEnemies = []
        """:type: list[api.gameinfo.BotInfo]"""

        #: List of BotInfo objects for enemies which are visible by the team and can see this bot
        #: For friendly bots the list will only include enemy bots which are visible by this commander.
        #: For enemy bots which are not visible by this commander, this will be an empty list.
        self.seenBy = []
        """:type: list[api.gameinfo.BotInfo]"""


    def __repr__(self):
        return "BotInfo(name='{}')".format(self.name)


class MatchInfo(object):
    """Information about the current match.
    """

    def __init__(self):
        super(MatchInfo, self).__init__()

        self.scores = {}               #: A dictionary of team name to score.
        """:type: dict[str, float]"""

        self.timeRemaining = 0.0       #: Time in seconds until this match ends.
        self.timeToNextRespawn = 0.0   #: Time in seconds until the next bot respawn cycle
        self.timePassed = 0.0          #: Time in seconds since the beginning of this match

        self.combatEvents = []         #: List of combat events that have occurred during this match.
        """:type: list[api.gameinfo.MatchCombatEvent]"""


class MatchCombatEvent(object):
    """Information about a particular game event.
    """

    TYPE_NONE = 0
    TYPE_KILLED = 1
    TYPE_FLAG_PICKEDUP = 2
    TYPE_FLAG_DROPPED = 3
    TYPE_FLAG_CAPTURED = 4
    TYPE_FLAG_RESTORED = 5
    TYPE_RESPAWN = 6

    def __init__(self, type, subject, instigator, time):
        super(MatchCombatEvent, self).__init__()

        self.type = type               #: The type of event (`TYPE_NONE`, `TYPE_KILLED`, `TYPE_FLAG_PICKEDUP`, `TYPE_FLAG_DROPPED`, `TYPE_FLAG_CAPTURED`, `TYPE_FLAG_RESTORED`, `TYPE_RESPAWN`)
        self.subject = subject         #: The FlagInfo/BotInfo object of the flag/bot that this event is about
        self.instigator = instigator   #: The BotInfo object of the bot which instigated this event
        self.time = time               #: Time in seconds since the beginning of this match that this event occurred.
