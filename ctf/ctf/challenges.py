#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

import os
import glob

try:     # Python 3.x
    import configparser
except:  # Python 2.x
    import ConfigParser as configparser

from inception.framework import ApplicationFramework, State

from aisbx.game.gamestate import GameState

from ctf.events import CombatEvent
from ctf.levelconfig import Challenge


class EventDispatcher(State):
    def __init__(self):
        super(EventDispatcher, self).__init__()
        self.callback = None
        self.app = None

    def onEvent(self, event):
        self.send(event)
        if self.callback:
            self.callback(event)


class ChallengeRules(object):
    AUTHOR = "AiGameDev.com"
    CHALLENGE_ID = None
    CHALLENGE_FILE = None

    def __init__(self, commanderName, eventDispatcher):
        self.commanderName = commanderName
        self.eventDispatcher = eventDispatcher
        if hasattr(self.eventDispatcher, 'callback'):
            self.eventDispatcher.callback = self._onGameEvent

        ## some default game runtime attributes
        self.candidateTeamName = None
        self.candidateTeamSize = -1
        self.gameController = None
        self.gameState = None
        self.elapsed = None
        self.losses = 0
        self.hits = 0


    def initialize(self):
        pass


    def setGameState(self, gameState, gameController):
        assert gameState and gameController, "Both game state and game controller objects must not be None!"
        self.gameState = gameState
        self.gameController = gameController
        for commander in gameController.commanders:
            if commander.nick == "Candidate":
                self.candidateTeamName = commander.game.team.name
                self.candidateTeamSize = len(commander.game.team.members)


    def _onGameEvent(self, event):
        ## fallback, if gameState or gameController have not been set yet (then to this once)
        if self.gameState is None or self.gameController is None:
            app = self.eventDispatcher.app
            self.setGameState(app.gameState, app.gameController)

        ## collect default game statistics
        if event.__class__.__name__ == 'CombatEvent' and event.type == CombatEvent.TYPE_KILLED:
            self._onCombatKilledEvent(event)

        ## call event handler, if available in this (child) class
        toCall = 'on' + event.__class__.__name__
        try:
            getattr(self, toCall)(event)
        except:
            pass


    def _onCombatKilledEvent(self, event):
        if self.candidateTeamName in event.subject.name:
            self.losses += 1
        else:
            self.hits += 1


    def _terminate(self):
        if self.gameState is not None:
            self.gameState.gameMode = GameState.MODE_FINISHING


    def getStatistics(self):
        return {'elapsed': self.elapsed or 'N/A',
                'losses': self.losses, 'hits': self.hits}


    @classmethod
    def calculateFinalScore(cls, stats):
        try:
            total = 0.0
            for s in stats:
                total += cls.calculateIndividualScore(s)
            return total / len(stats)
        except:
            import traceback
            traceback.print_exc()
            return 0.0


    # TODO: Legacy. Remove.
    @classmethod
    def getFinalScore(cls, stats):
        return cls.calculateFinalScore(stats)


    @staticmethod
    def calculateIndividualScore(stat):
        raise NotImplementedError


    @staticmethod
    def createEventDispatcher():
        return EventDispatcher()


    @classmethod
    def getLevelNames(cls):
        if not cls.CHALLENGE_ID:
            raise AttributeError("You have to set CHALLENGE_ID in your Rules child class implementation.")

        challengeDir = os.path.dirname(cls.CHALLENGE_FILE)
        levelNames = [os.path.basename(os.path.splitext(p)[0]) for p in glob.glob(os.path.join(challengeDir, '*.png'))]
        return levelNames


    @classmethod
    def createChallengeConfig(cls):
        if not cls.CHALLENGE_ID:
            raise AttributeError("You have to set CHALLENGE_ID in your Rules child class implementation.")
        return Challenge(cls.CHALLENGE_ID)
