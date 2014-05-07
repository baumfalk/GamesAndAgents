#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

from inception.math import Vector3

from api.vector2 import Vector2
import api.gameinfo

from ctf import gameconfig
from ctf.events import CombatEvent


def toVector2(vec):
    return Vector2(vec.x, vec.z)


def _createFromWorldBuilder(world, worldBuilder, levelConfig):
    levelInfo = api.gameinfo.LevelInfo()

    worldBounds = world.getBounds()
    extents = worldBounds.getMaximum()
    levelInfo.width, levelInfo.height = int(extents.x), int(extents.z)
    levelInfo.blockHeights = [ [worldBuilder.getAltitude(x, y) for y in range(levelInfo.height)] for x in range(levelInfo.width)]

    levelInfo.teamNames = levelConfig.teamConfigs.keys()
    levelInfo.flagSpawnLocations = {}
    levelInfo.flagScoreLocations = {}
    levelInfo.botSpawnAreas = {}
    for (teamName, teamConfig) in levelConfig.teamConfigs.items():
        levelInfo.flagSpawnLocations[teamName] = teamConfig.flagSpawnLocation
        levelInfo.flagScoreLocations[teamName] = teamConfig.flagScoreLocation
        levelInfo.botSpawnAreas[teamName] = teamConfig.botSpawnArea

    return levelInfo


def createLevelInfo(world, worldBuilder, levelConfig):
    levelInfo = _createFromWorldBuilder(world, worldBuilder, levelConfig)
    levelInfo.characterRadius = gameconfig.GameConfig.CHARACTER_RADIUS
    levelInfo.fieldOfViewAngles = [0.0,                                       # STATE_UNKNOWN
                                   gameconfig.GameConfig.MOVING_FOV_ANGLE,    # STATE_IDLE
                                   gameconfig.GameConfig.DEFEND_FOV_ANGLE,    # STATE_DEFENDING
                                   gameconfig.GameConfig.MOVING_FOV_ANGLE,    # STATE_MOVING
                                   gameconfig.GameConfig.MOVING_FOV_ANGLE,    # STATE_ATTACKING
                                   gameconfig.GameConfig.MOVING_FOV_ANGLE,    # STATE_CHARGING
                                   gameconfig.GameConfig.MOVING_FOV_ANGLE,    # STATE_SHOOTING
                                   0.0,                                       # STATE_TAKINGORDERS
                                   gameconfig.GameConfig.MOVING_FOV_ANGLE,    # STATE_HOLDING
                                   0.0]                                       # STATE_DEAD
    levelInfo.firingDistance = gameconfig.GameConfig.SHOOTING_DISTANCE
    levelInfo.walkingSpeed = gameconfig.GameConfig.WALKING_SPEED
    levelInfo.runningSpeed = gameconfig.GameConfig.RUNNING_SPEED
    levelInfo.gameLength = levelConfig.gameLength
    levelInfo.initializationTime = levelConfig.initializationTime
    levelInfo.respawnTime = levelConfig.respawnTime
    return levelInfo


def createMatchInfo(teams):
    matchInfo = api.gameinfo.MatchInfo()
    for name in teams.keys():
        matchInfo.scores[name] = 0
    return matchInfo


def _addTeam(gameinfo, team):
    gameinfo.teams[team.name] = team
    for bot in team.members:
        gameinfo.bots[bot.name] = bot
    gameinfo.flags[team.flag.name] = team.flag


def createGameInfo(teams, commanderTeam):
    gameInfo = api.gameinfo.GameInfo()

    gameInfo.match = createMatchInfo(teams)

    for teamName, team in teams.items():
        teamInfo = api.gameinfo.TeamInfo(teamName)

        # populate the team information
        teamInfo.flagScoreLocation = team.teamConfig.flagScoreLocation
        teamInfo.flagSpawnLocation = team.teamConfig.flagSpawnLocation
        try:
            teamInfo.botSpawnArea  = team.teamConfig.botSpawnArea[:]
        except TypeError:
            teamInfo.botSpawnArea  = None

        # populate the bot information
        for m in team.members:
            botInfo = api.gameinfo.BotInfo(m.name)
            botInfo.team = teamInfo
            teamInfo.members.append(botInfo)

        # populate the flag information
        flagInfo = api.gameinfo.FlagInfo(team.flag.name)
        flagInfo.team = teamInfo
        teamInfo.flag = flagInfo

        _addTeam(gameInfo, teamInfo)
        if team == commanderTeam:
            gameInfo.team = teamInfo
        else:
            gameInfo.enemyTeam = teamInfo

    return gameInfo


def updateFriendlyBots(gameInfo, commanderTeam, visibleBotsForEachTeam):
    for bot in commanderTeam.members:
        botInfo = gameInfo.bots[bot.name]
        botInfo.seenlast = 0.0
        locationComponent = bot.locationComponent
        botInfo.position = toVector2(locationComponent.getPosition())
        botInfo.facingDirection = toVector2(locationComponent.getOrientation() * Vector3.UNIT_Z)
        botInfo.health = bot.health.points
        if bot.health.points <= 0:
            botInfo.state = api.gameinfo.BotInfo.STATE_DEAD
        else:
            botInfo.state = bot.currentAction.botState if bot.currentAction else api.gameinfo.BotInfo.STATE_IDLE
        botInfo.flag = gameInfo.flags[bot.flag.name] if bot.flag else None
        botInfo.visibleEnemies = { gameInfo.bots[a.characterComponent.name] for a in bot.perceptionComponent.getPerceivable() }
        if visibleBotsForEachTeam:
            botInfo.seenBy = { gameInfo.bots[b.name] for b in visibleBotsForEachTeam[commanderTeam] if bot.actor in b.perceptionComponent.perceivableEntities['visual'] }
        else:
            botInfo.seenBy = set()


def updateEnemyBots(gameInfo, commanderTeam, enemyBots, visibleBotsForEachTeam, dt, cheat = False):
    for bot in enemyBots:
        botInfo = gameInfo.bots[bot.name]

        # In some cases in Python3 with simplejson, these values are not set.
        if botInfo.health is None:
            botInfo.health = 0.0
        if bot.health.points is None:
            bot.health.points = 0.0

        respawned = (botInfo.health <= 0.0) and (bot.health.points > 0.0)
        visible = visibleBotsForEachTeam and (bot in visibleBotsForEachTeam[commanderTeam])

        if bot.health.points <= 0.0:
            botInfo.seenlast = 0.0
            # don't update position, facingDirection
            botInfo.health = 0.0
            botInfo.state = api.gameinfo.BotInfo.STATE_DEAD
            botInfo.flag = None
            botInfo.visibleEnemies = set()
            botInfo.seenBy = set()

        elif respawned or visible or cheat:
            botInfo.seenlast = 0.0
            locationComponent = bot.locationComponent
            botInfo.position = toVector2(locationComponent.getPosition())
            botInfo.facingDirection = toVector2(locationComponent.getOrientation() * Vector3.UNIT_Z)
            botInfo.health = bot.health.points
            botInfo.state = bot.currentAction.botState if bot.currentAction else api.gameinfo.BotInfo.STATE_IDLE
            botInfo.flag = gameInfo.flags[bot.flag.name] if bot.flag else None
            botInfo.visibleEnemies = { gameInfo.bots[a.characterComponent.name] for a in bot.perceptionComponent.getPerceivable() }
            botInfo.seenBy = { gameInfo.bots[b.name] for b in commanderTeam.members if bot.actor in b.perceptionComponent.perceivableEntities.get('visual', set()) }

        else:
            # not seen
            # don't update position, facingDirection, health, state
            botInfo.seenlast += dt
            botInfo.flag = gameInfo.flags[bot.flag.name] if bot.flag else None
            botInfo.visibleEnemies = set()
            botInfo.seenBy = set()


def updateFlagInfo(gameInfo, gameState):
    for team in gameState.teams.values():
        flag = team.flag
        flagInfo = gameInfo.flags[flag.name]
        position = flag.location.getPosition()
        flagInfo.position = toVector2(position)
        flagInfo.respawnTimer = flag.flagResetCountdown
        flagInfo.carrier = gameInfo.bots[flag.holder.name] if flag.holder else None


def updateMatchInfo(gameInfo, gameState):
    matchInfo = gameInfo.match

    matchInfo.timeRemaining = gameState.gameTimer
    matchInfo.timeToNextRespawn = gameState.respawnTimer
    matchInfo.timePassed = gameState.timePassed

    for teamname, team in gameState.teams.items():
        matchInfo.scores[teamname] = team.score


def updateCommanderGameInfo(gameInfo, gameState, commanderTeam, visibleBotsForEachTeam, dt, cheat = False):
    updateFriendlyBots(gameInfo, commanderTeam, visibleBotsForEachTeam)
    updateEnemyBots(gameInfo, commanderTeam, gameState.getEnemyBots(commanderTeam), visibleBotsForEachTeam, dt, cheat)
    updateFlagInfo(gameInfo, gameState)
    updateMatchInfo(gameInfo, gameState)



class GameInfoBuilder:
    def __init__(self, team, world, worldBuilder, levelConfig, teams, eventDispatcher):
        self.team = team
        self.gameInfo = createGameInfo(teams, team)
        self.levelInfo = createLevelInfo(world, worldBuilder, levelConfig)
        # Put the current team's name at the front by convention so the client AI knows
        # easily which team it's in control of.
        t = self.levelInfo.teamNames
        t.insert(0, t.pop(t.index(team.name)))

        eventDispatcher.subscribe(CombatEvent, self.onCombatEvent)

    def updateGameInfo(self, gameState, visibleByTeam = None, dt = 0.0, cheat = False):
        updateCommanderGameInfo(self.gameInfo, gameState, self.team, visibleByTeam, dt, cheat)

    def onCombatEvent(self, event):
        # the commander knows information about enemy bots that have just shot one of its bots
        if event.type == CombatEvent.TYPE_KILLED:
            killed = event.subject
            if killed.team == self.team:
                killer = event.instigator
                enemyLocationComponent = killer.locationComponent
                enemyPosition = enemyLocationComponent.getPosition()
                killerInfo = self.gameInfo.bots[killer.name]
                killerInfo.position = Vector2(enemyPosition.x, enemyPosition.z)
                facingDirection = enemyLocationComponent.getOrientation() * Vector3.UNIT_Z
                killerInfo.facingDirection = Vector2(facingDirection.x, facingDirection.z)
                killerInfo.seenlast = 0.0

        # store all combat events in the MatchInfo for the comamnders to access
        botInfos = self.gameInfo.bots
        flagInfos = self.gameInfo.flags

        subject = None
        instigator = None

        if event.instigator:
            characterInstigator = event.instigator
            if characterInstigator:
                instigator = botInfos[characterInstigator.name]

        if event.subject:
            if event.subject.name in botInfos:
                subject = botInfos[event.subject.name]
            elif event.subject.name in flagInfos:
                subject = flagInfos[event.subject.name]

        assert instigator or not event.instigator
        assert subject or not event.subject

        mce = api.gameinfo.MatchCombatEvent(event.type, subject, instigator, event.time)
        self.gameInfo.match.combatEvents.append(mce)

