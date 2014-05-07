from tests.helpers import *


#------------------------------------------------------------------------------
# Shooting Tests
#------------------------------------------------------------------------------
class TestShooting(TestSuite):

    def test_BotCannotShootThroughWalls(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = {'Red0': (Vector2(78.75, 8.25), Vector2(0, 1))}
        self.config.red.commander = Script([(0.0, Defend.create('Red0', Vector2(-1, 1)))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(68.75, 18.25), Vector2(0, -1))}
        self.config.blue.commander = Script([(0.0, Defend.create('Blue0', Vector2(1, -1)))])

        self.config.gameLength = 10.0

        def validate(game, commanders):
            assert not isDead(game, 'Red0')
            assert not isDead(game, 'Blue0')
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_LineOfSightLostNoShotFired(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = {'Red0': (Vector2(66, 45), Vector2(0, 1))}
        self.config.red.commander = Script([(0, Move.create('Red0', Vector2(68, 25)))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(60, 42.5), Vector2(1, 0))}
        self.config.blue.commander = Script([(0, Charge.create('Blue0', Vector2(80, 42.5)))])

        self.config.gameLength = 2.0

        def validate(game, commanders):            
            assert not isDead(game, 'Red0')
            assert not isDead(game, 'Blue0')
            for commander in commanders:
                assert not hasEvent(commander, type, 'Red0', 'Blue0')
                assert not hasEvent(commander, type, 'Blue0', 'Red0')
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate
