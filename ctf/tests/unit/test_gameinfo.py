import random
import unittest

from api.vector2 import Vector2
from api.gameinfo import *
from api import gameinfo
from api import jsonhelpers

from ctf.network import registry
from ctf.gameinfobuilder import _addTeam

from tests.helpers import *


class GameInfoJsonTesting(unittest.TestCase):

    def compareLevelInfo(self, level, copy):
        assert level.width  == copy.width
        assert level.height == copy.height
        assert level.blockHeights == copy.blockHeights
        assert level.teamNames == copy.teamNames
        for teamName in level.teamNames:
            assert teamName in copy.flagSpawnLocations.keys()
            assert isSimilar(level.flagSpawnLocations[teamName], copy.flagSpawnLocations[teamName])
        for teamName in level.teamNames:
            assert teamName in copy.flagScoreLocations.keys()
            assert isSimilar(level.flagScoreLocations[teamName], copy.flagScoreLocations[teamName])
        for teamName in level.teamNames:
            assert teamName in copy.botSpawnAreas.keys()
            assert isSimilar(level.botSpawnAreas[teamName][0], copy.botSpawnAreas[teamName][0])
            assert isSimilar(level.botSpawnAreas[teamName][1], copy.botSpawnAreas[teamName][1])
        assert level.characterRadius == copy.characterRadius
        assert level.fieldOfViewAngles == copy.fieldOfViewAngles
        assert level.firingDistance  == copy.firingDistance
        assert level.walkingSpeed    == copy.walkingSpeed
        assert level.runningSpeed    == copy.runningSpeed
        assert isSimilar(level.gameLength, copy.gameLength)
        assert isSimilar(level.initializationTime, copy.initializationTime)
        assert isSimilar(level.respawnTime, copy.respawnTime)

    def compareMatchInfo(self, match, copy):
        assert match.scores  == copy.scores
        assert isSimilar(match.timeRemaining, copy.timeRemaining)
        assert isSimilar(match.timeToNextRespawn, copy.timeToNextRespawn)
        assert isSimilar(match.timePassed, copy.timePassed)
        assert match.combatEvents == copy.combatEvents

    def compareBotInfo(self, bot, copy):
        self.assertEquals(bot.name, copy.name)
        assert bot.team.name == copy.team.name # should we recurse?
        assert isSimilar(bot.health, copy.health)
        assert bot.state == copy.state
        assert isSimilar(bot.position, copy.position)
        assert isSimilar(bot.facingDirection, copy.facingDirection)
        if bot.seenlast:
            assert isSimilar(bot.seenlast, copy.seenlast)
        else:
            assert bot.seenlast == copy.seenlast
        if bot.flag:
            assert bot.flag.name == copy.flag.name # should we recurse?
        else:
            assert bot.flag == copy.flag
        assert [b.name for b in bot.visibleEnemies] == [b.name for b in copy.visibleEnemies] # should we recurse?
        assert [b.name for b in bot.seenBy] == [b.name for b in copy.seenBy] # should we recurse?

    def compareTeamInfo(self, team, copy):
        self.assertEquals(team.name, copy.name)
        assert [b.name for b in team.members] == [b.name for b in copy.members] # should we recurse?
        assert team.flag.name == copy.flag.name # should we recurse?
        assert isSimilar(team.flagScoreLocation, copy.flagScoreLocation)
        assert isSimilar(team.flagSpawnLocation, copy.flagSpawnLocation)
        assert isSimilar(team.botSpawnArea[0], copy.botSpawnArea[0])
        assert isSimilar(team.botSpawnArea[1], copy.botSpawnArea[1])

    def compareFlagInfo(self, flag, copy):
        self.assertEquals(flag.name, copy.name)
        assert flag.team.name == copy.team.name
        assert isSimilar(flag.position, copy.position)
        if flag.carrier:
            assert flag.carrier.name == copy.carrier.name # should we recurse?
        else:
            assert flag.carrier == copy.carrier
        assert isSimilar(flag.respawnTimer, copy.respawnTimer)

    def compareGameInfo(self, game, copy):
        self.compareMatchInfo(game.match, copy.match)

        assert game.bots.keys() == copy.bots.keys()
        for b in game.bots.keys():
            self.compareBotInfo(game.bots[b], copy.bots[b])

        assert game.flags.keys() == copy.flags.keys()
        for f in game.flags.keys():
            self.compareFlagInfo(game.flags[f], copy.flags[f])

        assert game.teams.keys() == copy.teams.keys()
        for t in game.teams.keys():
            self.compareTeamInfo(game.teams[t], copy.teams[t])

        self.compareTeamInfo(game.team, copy.team)
        self.compareTeamInfo(game.enemyTeam, copy.enemyTeam)
   

    def setUp(self):
        super(GameInfoJsonTesting, self).setUp()

        self.level = LevelInfo()
        self.level.width, self.level.height = 30, 20
        self.level.blockHeights = [[0]*self.level.height for w in range(self.level.width)]
        for w in range(self.level.width):
            for h in range(self.level.height):
                self.level.blockHeights[w][h] = random.choice([0, 1, 2, 4])
        self.level.teamNames = ["red", "blue"]
        self.level.flagSpawnLocations = { "red": 10 * Vector2.random(), "blue": 10 * Vector2.random() }
        self.level.flagScoreLocations = { "red": 10 * Vector2.random(), "blue": 10 * Vector2.random() }
        self.level.botSpawnAreas = { "red": (Vector2.random(), 10 * Vector2.random()), "blue": (Vector2.random(), 10 * Vector2.random()) }
        self.level.characterRadius = 0.3
        self.level.fieldOfViewAngles = [0.6, 1, 2, 4]
        self.level.firingDistance = 15.0
        self.level.walkingSpeed = 4.0
        self.level.runningSpeed = 8.0
        self.level.gameLength = 192.1
        self.level.initializationTime = 3.2
        self.level.respawnTime = 11.2

        self.game = GameInfo()

        self.redTeam = self.createTeam("red", 5)
        _addTeam(self.game, self.redTeam)
        self.game.team = self.redTeam
        
        self.blueTeam = self.createTeam("blue", 4)        
        _addTeam(self.game, self.blueTeam)
        self.game.enemyTeam = self.blueTeam

        self.game.match = MatchInfo()
        self.game.match.scores = {"red": 3, "blue": 2}
        self.game.match.timeRemaining = 81.0
        self.game.match.timeToNextRespawn = 15.0
        self.game.match.timePassed = 19.0
        self.game.match.combatEvents = []

    def createTeam(self, teamName, numBots):
        team = TeamInfo(teamName)

        for i in range(numBots):
            bot = BotInfo("{}{}".format(team.name, i))
            bot.team = team
            bot.health = 10
            bot.state = BotInfo.STATE_DEFENDING
            bot.position = 10 * Vector2.random()
            bot.facingDirection = Vector2.randomUnitVector()
            bot.seenLast = random.random() * 100
            bot.flag = None
            bot.visibleEnemies = []
            bot.seenBy = []
            team.members.append(bot)

        team.flagSpawnLocation = self.level.flagSpawnLocations[team.name]
        team.flagScoreLocation = self.level.flagScoreLocations[team.name]
        team.botSpawnArea = self.level.botSpawnAreas[team.name]

        flag = FlagInfo("{}Flag".format(team.name))
        team.flag = flag
        flag.carrier = None
        flag.position = 10 * Vector2.random()
        flag.respawnTimer = 0
        flag.team = team

        return team

    def test_LevelInfo(self):
        jsonText = registry.serialize(self.level)
        copy = registry.deserialize(jsonText)
        jsonhelpers.fixupReferences(copy, self.game)
        self.compareLevelInfo(self.level, copy)

    def test_MatchInfo(self):
        jsonText = registry.serialize(self.game.match)
        copy = registry.deserialize(jsonText)
        jsonhelpers.fixupReferences(copy, self.game)
        self.compareMatchInfo(self.game.match, copy)

    def test_BotInfo(self):
        jsonText = registry.serialize(next(iter(self.game.bots.values())))
        copy = registry.deserialize(jsonText)
        jsonhelpers.fixupReferences(copy, self.game)
        self.compareBotInfo(next(iter(self.game.bots.values())), copy)

    def test_TeamInfo(self):
        jsonText = registry.serialize(next(iter(self.game.teams.values())))
        copy = registry.deserialize(jsonText)
        jsonhelpers.fixupReferences(copy, self.game)
        self.compareTeamInfo(next(iter(self.game.teams.values())), copy)

    def test_FlagInfo(self):
        jsonText = registry.serialize(next(iter(self.game.flags.values())))
        copy = registry.deserialize(jsonText)
        jsonhelpers.fixupReferences(copy, self.game)
        self.compareFlagInfo(next(iter(self.game.flags.values())), copy)

    def test_GameInfo(self):
        jsonText = registry.serialize(self.game)
        copy = registry.deserialize(jsonText)
        jsonhelpers.fixupReferences(copy, copy)
        self.compareGameInfo(self.game, copy)


if __name__ == '__main__':
    unittest.main(verbosity = 2, failfast = False)
