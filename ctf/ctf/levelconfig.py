#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

import os
import random

try:     # Python 3.x
    import configparser
except:  # Python 2.x
    import ConfigParser as configparser

from api.vector2 import Vector2
from inception.framework import ApplicationFramework
from inception.math import ColorValue


class LevelConfig(object):
    class TeamConfig(object):
        def __init__(self):
            super(LevelConfig.TeamConfig, self).__init__()
            self.name = ''
            self.color = ColorValue.White
            self.flagSpawnLocation = Vector2.ZERO
            self.flagScoreLocation = Vector2.ZERO
            self.botSpawnArea = (Vector2.ZERO, Vector2.ZERO)
            self.numberBots = 0
            self.botSpawnLocations = {}
            self.commander = None

        def getColor(self):
            return (self.color + ColorValue.Black) * 0.5

    def __init__(self):
        super(LevelConfig, self).__init__()
        self.map = None
        self.teams = []
        self.teamConfigs = {}
        self.initializationTime = 0
        self.gameLength = 180
        self.respawnTime = 45
        self.repeat = False

    def endOfGameCallback(self, gameState, commanders):
        pass


class RedVersusBlue(LevelConfig):
    def __init__(self):
        super(RedVersusBlue, self).__init__()

        self.map = 'map00.png'
        self.initializationTime = 10          # allow time for the commanders to perform their initialization

        red = self.TeamConfig()
        red.name = "Red"
        red.color = ColorValue(201, 0, 0, 255.0) / 255.0
        red.flagSpawnLocation = Vector2(6.0, 30.0)
        red.flagScoreLocation = Vector2(6.0, 30.0)
        red.botSpawnArea = (Vector2(3, 41), Vector2(9, 48))
        red.numberBots = 5
        red.botSpawnLocations = {}
        red.commander = None
        self.red = red
        self.teamConfigs[red.name] = red
        self.teams.append(red)

        blue = self.TeamConfig()
        blue.name = "Blue"
        blue.color = ColorValue(50.0, 22.0, 176.0, 255.0) / 255.0
        blue.flagSpawnLocation = Vector2(82.0, 20.0)
        blue.flagScoreLocation = Vector2(82.0, 20.0)
        blue.botSpawnArea = (Vector2(79, 2), Vector2(85, 9))
        blue.numberBots = 5
        blue.botSpawnLocations = {}
        blue.commander = None
        self.blue = blue
        self.teamConfigs[blue.name] = blue
        self.teams.append(blue)


    def makeVector2(self, data):
        return Vector2(*[float(x) for x in data.split()])

    def configure(self, name):
        self.map = name+'.png'

        config = configparser.RawConfigParser()
        config.read('applications/demos/CaptureTheFlag/assets/'+name+'.ini')
        config.read('assets/'+name+'.ini')
        config.read(ApplicationFramework.getInitialDirectory()+'assets/'+name+'.ini')

        if not config.has_section('game'):
            return

        self.initializationTime = config.getfloat('game', 'initialization')
        self.gameLength = config.getfloat('game', 'duration')
        self.respawnTime = config.getfloat('game', 'respawn')

        self.loadTeams(config)


    def loadTeams(self, config):
        for n, team in self.teamConfigs.items():
            section = n.lower()
            team.numberBots = config.getint(section, 'bots')
            team.flagSpawnLocation = self.makeVector2(config.get(section, 'flag'))
            team.flagScoreLocation = self.makeVector2(config.get(section, 'score'))
            try:
                team.botSpawnArea = tuple([self.makeVector2(data) for data in config.get(section, 'base').split(',')])
            except configparser.NoOptionError:
                team.botSpawnArea = None
                for i, l in enumerate(config.get(section, 'spawn').split('\n')):
                    situation = tuple([self.makeVector2(v) for v in l.split(',')])
                    team.botSpawnLocations[n+str(i)] = situation


class Competition(RedVersusBlue):
    def __init__(self):
        super(Competition, self).__init__()

        self.commanders = []

    def getCommanders(self):
        assert len(self.commanders) >= 2, "Need at least two commanders to be specified in order to run this competition."
        if len(self.commanders) == 2:
            return self.commanders
        else:
            return random.sample(self.commanders, 2)


class Challenge(Competition):
    def __init__(self, challengeName):
        super(Competition, self).__init__()
        self.challengeName = challengeName
        self.map = None
        self.initializationTime = 0.0
        self.gameLength = 0.0
        self.respawnTime = 0.0


    def configure(self, levelName):
        challengeDir = os.path.join(ApplicationFramework.getInitialDirectory(), 'assets', 'challenges', self.challengeName)
        challengeIni = os.path.join(challengeDir, levelName + '.ini')
        self.map = os.path.join('challenges', self.challengeName, levelName + '.png')

        config = configparser.RawConfigParser()
        config.read(challengeIni)

        if not config.has_section('game'):
            return

        self.initializationTime = config.getfloat('game', 'initialization')
        self.gameLength = config.getfloat('game', 'duration')
        self.respawnTime = config.getfloat('game', 'respawn')

        self.loadTeams(config)


    def getCommanders(self):
        assert len(self.commanders) == 2, "Need only two commanders in order to run this competition."
        return self.commanders


def getLevelConfig(challengeID):
    return Challenge(challengeID)
