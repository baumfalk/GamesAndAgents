import sys
import unittest
import random
import inspect

from inception import demo as platform

import api
from api.vector2 import Vector2
from api.gameinfo import *
from api.orders import *

from ctf.events import *
from ctf.health import HealthComponent
from ctf.character import CharacterComponent
from ctf.perception import PerceptionComponent
from ctf.scriptedcommander import ScriptedCommander

from tests.application import CaptureTheFlagTests
from tests.configs import TestConfig


class ValidateAndCallMethod(object):
    def __init__(self, method):
        self.method = method
    def __call__(self, game, commanders):
        self.method(game, commanders)
        validateCommanders(commanders)


class TestSuite(unittest.TestCase):

    def setUp(self):
        """Initialization function run for each of the `test_*` functions below.
        """
        self.config = TestConfig()
        self.config.endOfGameCallback = None

    def runGame(self, config):
        if sys.gettrace() and not 'trace' in sys.modules:
            runner = platform.WindowRunner()
            runner.forceSingleThreaded()
        else:
            runner = platform.ConsoleRunner()
            runner.forceAcceleration()
        
        
        #runner = platform.WindowRunner()
        #runner.forceSingleThreaded()

        self.app = CaptureTheFlagTests(config)
        runner.main(self.app)
        del self.app
        del runner

    def tearDown(self):
        """Shutdown function run for each of the `test_*` functions below.
        """
        method = self.id().split('.')[-1].replace('test_', 'validate_')
        if hasattr(self, method):
            assert self.config.endOfGameCallback is None
            m = getattr(self, method)
            self.config.endOfGameCallback = ValidateAndCallMethod(m)
        assert self.config.endOfGameCallback is not None
        self.runGame(self.config)
        del self.config


def isSimilar(a, b, e = 0.01):
    if isinstance(a, list) and isinstance(b, list):
        for x,y in zip(a,b): 
            if not isSimilar(x, y, e):
                return False
        return True
    if isinstance(a, Vector2):
        distance = a.distance(b)
        return distance < e
    else:
        distance = abs(a - b)
        return distance < e
    return False

# return True if botId is dead
def isDead(gameState, botId):
    return gameState.bots[botId].health.points <= 0.0

def isDeadAccordingToCommander(commander, botId):
    return commander.game.bots[botId].health <= 0.0

# return the number of dead bots in the botIds list
def numberDeadBots(gameState, botIds):
    return len([b for b in botIds if isDead(gameState, b)])

# return the number of alive bots in the botIds list
def numberAliveBots(gameState, botIds):
    return len([b for b in botIds if not isDead(gameState, b)])

def canSee(gameState, botId):
     return {a.characterComponent.name for a in gameState.bots[botId].perceptionComponent.getPerceivable()}

def canSeeAccordingToCommander(commander, botId):
    return {b.name for b in commander.game.bots[botId].visibleEnemies}

def isSeenBy(gameState, botId):
    return {a.characterComponent.name for a in gameState.bots[botId].perceptionComponent.getPerceivableByPerceivable()}

def isSeenByAccordingToCommander(commander, botId):
    return {b.name for b in commander.game.bots[botId].seenBy}

def position(gameState, botId):
    pos = gameState.bots[botId].location.getPosition()
    return Vector2(pos.x, pos.z)

def positionAccordingToCommander(commander, botId):
    return commander.game.bots[botId].position

def facingDirection(gameState, botId):
    from inception.math import Vector3
    dir = gameState.bots[botId].location.getOrientation() * Vector3.UNIT_Z
    return Vector2(dir.x, dir.z)

def facingDirectionAccordingToCommander(commander, botId):
    return commander.game.bots[botId].facingDirection

def lastSeenTimeAccordingToCommander(commander, botId):
    return commander.game.bots[botId].seenlast

def hasEvent(commander, type, instigator = None, subject = None, timeRange = (0, 99999)):
    for event in commander.game.match.combatEvents:
        if event.type != type:
            continue
        if instigator and (event.instigator.name != instigator) and not (isinstance(instigator, list) and event.instigator.name in instigator):
            continue
        if subject and (event.subject.name != subject) and not (isinstance(subject, list) and event.subject.name in subject):
            continue
        if (event.time < timeRange[0]) or (event.time > timeRange[1]):
            continue
        return True
    return False

def scoresAccordingToCommander(commander):
    return commander.game.match.scores

def validateGameInfo(gameInfo):
    assert gameInfo.team == gameInfo.teams[gameInfo.team.name]
    assert gameInfo.enemyTeam == gameInfo.teams[gameInfo.enemyTeam.name]
    assert set(gameInfo.team.members) | set(gameInfo.enemyTeam.members) == set(gameInfo.bots.values())
    assert set(gameInfo.team.members) & set(gameInfo.enemyTeam.members) == set()
    for t in gameInfo.teams.values():
        assert t.flag == gameInfo.flags[t.flag.name]
    for b in gameInfo.bots.values():
        assert b.team in gameInfo.teams.values()
        assert b.flag == None or b.flag in gameInfo.flags.values()
    for f in gameInfo.flags.values():
        assert f.team in gameInfo.teams.values()
        assert f.carrier == None or f.carrier in gameInfo.bots.values()
    for e in gameInfo.match.combatEvents:
        assert e.instigator == None or e.instigator in gameInfo.bots.values()
        assert e.subject == None or e.subject in gameInfo.bots.values() or e.subject in gameInfo.flags.values()

def validateCommanders(commanders):
    for commander in commanders:
        validateGameInfo(commander.game)

def Script(orders):
    return lambda nick, **kwargs: ScriptedCommander(orders, nick, **kwargs)
