#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

from inception import framework
from inception.math import Situation, Vector3, Quaternion, Situation, ColorValue
from inception.motion import LocomotionComponent, Motion

from aisbx import game, logger
log = logger.getLog(logger.LOG_GAME)

from aisbx.actor.sensory import SensorySystem, SensoryComponent
from aisbx.actor.perception import PerceptionSystem, PerceivedEvent
from aisbx.actor.trigger import TriggerSystem
from aisbx.actor.navigation import NavigationComponent

from ctf.character import CharacterComponent, CharacterController

import sensory
import perception


from ctf.events import *
from ctf.commands import *
from ctf.commandererror import CommanderError
from ctf.gameinfobuilder import GameInfoBuilder
from ctf.levelbuilder import LevelBuilder
from ctf.teambuilder import TeamFactory
from ctf.botorders import TakingOrders
from ctf.gameconfig import GameConfig
import ctf.network.commander

from character import CharacterComponent, CharacterController

import health
import targeting
import weapon


class CaptureTheFlagGameController(game.GameController):
    """The GameController for the Capture The Flag demo.
    """

    def __init__(self, gameState, worldBuilder, levelConfig, commanderOptions):
        super(CaptureTheFlagGameController, self).__init__(gameState, worldBuilder)

        self.levelConfig = levelConfig
        self.commanderOptions = commanderOptions
        self.commanders = {} # map of commanders with the team they are commanding
        self.lastCommanderTickTime = -1.0 # the time since the commanders were last ticked, initialized to negative value so commanders are ticked in the first frame
        self.gameInfoBuilders = {} # objects responsible for updating the game info objects of each commander
        self.readyCountdown = 0.0

        ## general game events
        self.gameState.subscribe(FlagPickedUpEvent, self.onFlagPickedUp)
        self.gameState.subscribe(FlagDroppedEvent, self.onFlagDropped)
        self.gameState.subscribe(FlagRestoredEvent, self.onFlagRestored)
        self.gameState.subscribe(FlagCapturedEvent, self.onFlagCapture)

        ## internal game events
        self.subscribe(BotOrderEvent, self.cmdBotOrder)
        self.subscribe(BotRespawnEvent, self.cmdBotRespawn)
        self.gameState.subscribe(WeaponKillTargetCommand, self.cmdKill)


    def initialize(self):

        super(CaptureTheFlagGameController, self).initialize()

        self.sensorySystem = SensorySystem(self.gameState)
        self.sensorySystem.addCanSenseFilter(sensory.CTFCanSenseFilter())
        self.sensorySystem.addSkipPairingFilter(sensory.CTFSkipDeadFilter())
        self.sensorySystem.addSkipPairingFilter(sensory.CTFSkipSameTeamFilter())
        self.addController(self.sensorySystem)

        self.perceptionSystem = PerceptionSystem()
        self.perceptionSystem.addCanPerceiveFilter(perception.CTFCanPerceiveFilter())
        self.perceptionSystem.connect(PerceivedEvent, self.gameState)
        self.addController(self.perceptionSystem)

        self.triggerSystem = TriggerSystem(self.gameState)
        self.addController(self.triggerSystem)

        LevelBuilder.build(self, self.gameState, self.levelConfig, self.commanderOptions)

        for commander, commanderTeam in self.commanders.items():
            gameInfoBuilder = GameInfoBuilder(commanderTeam, self.gameState.world, self.worldBuilder, self.levelConfig, self.gameState.teams, self.gameState)
            commander.level = gameInfoBuilder.levelInfo
            commander.game = gameInfoBuilder.gameInfo
            self.gameInfoBuilders[commander] = gameInfoBuilder


    def tickCommanders(self, dt, readable = False):
        self.updateCommanderInfos(dt)

        # let the commanders do their thing
        if self.gameState.timePassed - self.lastCommanderTickTime >= 0.12: # tick commanders at ~8Hz (every 4 30Hz frames)
            for c in self.commanders.keys():
                try:
                    c.tick()
                except ctf.network.commander.DisconnectError as e:
                    raise CommanderError(c.nick, 'Commander disconnected or timed out: {}'.format(e))

            self.lastCommanderTickTime = self.gameState.timePassed

        if not readable:
            # execute orders by commanders
            for commander, team in self.commanders.items():
                try:
                    commander.gatherOrders()
                except AttributeError:
                    # Only NetworkCommander defines gatherOrders, to avoid cluttering
                    # the base class with implementation details and improve readability.
                    pass
                except ctf.network.commander.DisconnectError as e:
                    raise CommanderError(commander.nick, 'Commander disconnected or timed out: {}'.format(e))

                for order in commander.orderQueue:
                    bot = self.gameState.bots[order.botId]
                    # a commander can only execute orders for bots in its team
                    if bot.team == team:
                        self.send(BotOrderEvent(bot, order))

                commander.orderQueue = []


    def isReady(self):
        # wait until the read countdown has ticked down to 0
        # or until all of the commanders have reported ready
        if self.readyCountdown <= 0.0:
            return True

        readyCount = 0
        for c in self.commanders:
            try:
                readyCount += 1 if c.isReady() else 0
            except AttributeError:
                # Only NetworkCommander implements isReady to keep the base
                # class as tidy as possible.  Assume local commanders always
                # ready to go!
                readyCount += 1
            except ctf.network.commander.DisconnectError as e:
                raise CommanderError(c.nick, 'Commander disconnected or timed out: {}'.format(e))

        if readyCount != len(self.commanders):
            # not all of the commanders are ready
            return False
        else:
            log.debug("Commanders are ready; starting the game.")
            self.readyCountdown = 0.0
            return True


    def tick(self, dt):
        if self.isPaused():
            # TODO: Just tick commanders, no orders.
            self.tickCommanders(dt, True)

        self.readyCountdown -= dt
        if not self.isReady():
            return

        self.gameState.timePassed += dt
        self.gameState.gameTimer -= dt
        if self.gameState.gameTimer <= 0 and self.gameState.gameMode == game.GameState.MODE_PLAYING:
            self.gameState.gameMode = game.GameState.MODE_FINISHING

        self.gameState.respawnTimer -= dt
        if self.gameState.respawnTimer <= 0:
            self.gameState.respawnTimer = self.levelConfig.respawnTime
            self.respawnDeadBots()

        self._tickAndUpdateControllers(dt, lambda cls: 'FlagController' in repr(cls))

        if hasattr(self, 'ticker'):
            self._tickAndUpdateControllers(dt, lambda _: True, [self])
        else:
            self.tickCommanders(dt)

        self._tickAndUpdateControllers(dt, lambda cls: 'FlagController' not in repr(cls))


    def sendCombatEvent(self, type, subject, instigator=None):
        event = CombatEvent(type, subject, instigator, self.gameState.timePassed)
        self.gameState.send(event)


    def cmdBotOrder(self, cmd):
        description = " ('" + cmd.order.description + "')" if cmd.order.description else ''
        log.debug("Received order `%s`%s for %s." % (cmd.order.__class__.__name__, description, cmd.bot.name))

        cmd.bot.description = cmd.order.description
        cmd.bot.executeOrder(TakingOrders(cmd.bot.name, cmd.order))


    def cmdKill(self, event):
        target = event.target
        position = target.location.getPosition()
        color = target.body.getColor()
        self.worldBuilder.createExplosion(Situation(position, Quaternion.IDENTITY), color)
        self.sendCombatEvent(CombatEvent.TYPE_KILLED, event.target, event.weapon.character)
        log.debug(event.target.name + " was taken down by " + event.weapon.character.name + ".")


    def cmdBotRespawn(self, cmd):
        cmd.bot.reset(cmd.situation)
        self.sendCombatEvent(CombatEvent.TYPE_RESPAWN, cmd.bot)
        log.debug(cmd.bot.name + " spawned.")


    def onFlagCapture(self, event):
        self.sendCombatEvent(CombatEvent.TYPE_FLAG_CAPTURED, event.flag, event.bot)
        team = event.bot.team
        team.score += 1
        scores = {team.name: team.score for team in self.gameState.teams.values()}
        self.gameState.send(ScoreChangedEvent(scores))
        log.info(event.bot.name + " captured the flag; " + team.name + " team now has " + str(team.score) + " point(s).")


    def onFlagPickedUp(self, event):
        self.sendCombatEvent(CombatEvent.TYPE_FLAG_PICKEDUP, event.flag, event.bot)
        log.info(event.bot.name + " picked up flag.")


    def onFlagDropped(self, event):
        self.sendCombatEvent(CombatEvent.TYPE_FLAG_DROPPED, event.flag, event.bot)
        log.info(event.bot.name + " dropped flag.")


    def onFlagRestored(self, event):
        self.sendCombatEvent(CombatEvent.TYPE_FLAG_RESTORED, event.flag)


    def updateCommanderInfos(self, dt):
        # aggregate the perceivable enemies for the bots on each team
        visibleByTeam = {}
        for team in self.gameState.teams.values():
            perceptionComponents = [b.perceptionComponent for b in team.members]
            visible = {entity.characterComponent for p in perceptionComponents for entity in p.perceivableEntities.get('visual', set())}
            visibleByTeam[team] = visible

        # now sync all infos with the commanders
        for commander in self.commanders.keys():
            self.gameInfoBuilders[commander].updateGameInfo(self.gameState, visibleByTeam, dt, commander.cheat)


    def respawnDeadBots(self):
        for team in self.gameState.teams.values():
            for bot in team.members:
                if bot.health.points <= 0.0:
                    situation = team.findSpawnLocation(bot)
                    self.send(BotRespawnEvent(bot, situation))


    def startGame(self):
        super(CaptureTheFlagGameController, self).startGame()

        scores = { team.name: team.score for team in self.gameState.teams.values() }
        self.gameState.send(ScoreChangedEvent(scores))

        # start the game timer
        self.gameState.gameTimer = self.levelConfig.gameLength
        self.gameState.respawnTimer = 0.0
        self.gameState.gameMode = game.GameState.MODE_PLAYING

        # now sync all infos with the commanders
        for commander in self.commanders.keys():
            self.gameInfoBuilders[commander].updateGameInfo(self.gameState)

        for c in self.commanders:
            try:
                if c.initialize() == False:
                    self.gameState.gameMode = game.GameState.MODE_FINISHING

                if len(c.orderQueue) > 0:
                    logger.getLog(logger.LOG_BOTCMD).warning(
                            "Commanders should not issue orders during initialize(). Orders issued during initialize() will be ignored.")
                    c.orderQueue = []

            except ctf.network.commander.DisconnectError as e:
                raise CommanderError(c.nick, 'Commander disconnected or timed out: {}'.format(e))

        # add a little bit of time to allow for floating point arithmatic errors during countdown
        self.readyCountdown = self.levelConfig.initializationTime + 1e-2


    def stopGame(self):
        super(CaptureTheFlagGameController, self).stopGame()

        for c in self.commanders:
            try:
                c.shutdown()
            except Exception as e:
                import sys
                log.error('Caught exception from commander(' + c.name + ') during shutdown: ' + str(e))
                log.exception(e)

        for team in self.gameState.teams.values():
            TeamFactory.destroyTeam(team, self.gameState.world)
