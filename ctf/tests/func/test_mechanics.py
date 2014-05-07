from tests.helpers import *


#------------------------------------------------------------------------------
# Flag Tests
#------------------------------------------------------------------------------
class TestFlagLogic(TestSuite):

    def test_CanPickUpTheFlagAndScoreWhenAttacking(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = {'Red0': (Vector2(10, 15), Vector2(1, 0))}
        self.config.red.commander = Script([(0.0, Attack.create('Red0', self.config.blue.flagSpawnLocation)),
                                     (4.0, Attack.create('Red0', self.config.red.flagScoreLocation))])
        self.config.gameLength = 11.0

        def validate(game, commanders):
            assert game.teams['Red'].score == 1
            assert game.teams['Blue'].score == 0

            for commander in commanders:
                assert hasEvent(commander, CombatEvent.TYPE_FLAG_PICKEDUP, 'Red0', 'BlueFlag', [0, 4])
                assert hasEvent(commander, CombatEvent.TYPE_FLAG_CAPTURED, 'Red0', 'BlueFlag', [4, 11])
                assert scoresAccordingToCommander(commander) == {'Red': 1, 'Blue': 0}
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate

    def test_CanPickUpTheFlagAndScoreWhenCharging(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = {'Red0': (Vector2(10, 15), Vector2(1, 0))}
        self.config.red.commander = Script([(0.0, Move.create('Red0', self.config.blue.flagSpawnLocation)),
                                     (3.0, Move.create('Red0', self.config.red.flagScoreLocation))])
        self.config.gameLength = 9.0

        def validate(game, commanders):
            assert game.teams['Red'].score == 1
            assert game.teams['Blue'].score == 0

            for commander in commanders:
                assert hasEvent(commander, CombatEvent.TYPE_FLAG_PICKEDUP, 'Red0', 'BlueFlag', [0, 4])
                assert hasEvent(commander, CombatEvent.TYPE_FLAG_CAPTURED, 'Red0', 'BlueFlag', [4, 8])
                assert scoresAccordingToCommander(commander) == {'Red': 1, 'Blue': 0}
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


#------------------------------------------------------------------------------
# Spawn Logic
#------------------------------------------------------------------------------
class TestSpawnLogic(TestSuite):

    def test_BotsInSpawnCanNotBeShot(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = {'Red0': (Vector2(6, 2), Vector2(1, 0))}
        self.config.red.commander = Script([(0, Attack.create('Red0', Vector2(17, 2)))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(17, 2), Vector2(0, -1))}
        self.config.blue.commander = Script([(0.5, Attack.create('Blue0', Vector2(6, 2)))])

        self.config.gameLength = 4.0

        def validate(game, commanders):
            assert isDead(game, 'Red0')
            assert not isDead(game, 'Blue0')
            for commander in commanders:
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, 'Blue0', 'Red0', [0, self.config.gameLength])
                assert not hasEvent(commander, CombatEvent.TYPE_KILLED, 'Red0', 'Blue0')
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


#------------------------------------------------------------------------------
# Commander Rules
#------------------------------------------------------------------------------
class TestCommanderRules(TestSuite):

    def test_CommanderCannotGiveOrdersToEnemyBots(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = {'Red0': (Vector2(10, 30), Vector2(1, 0))}
        self.config.red.commander = Script([(0, Defend.create('Red0')), (0, Attack.create('Blue0', Vector2(20, 30)))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(10, 20), Vector2(1, 0))}
        self.config.blue.commander = Script([])

        self.config.gameLength = 3.0

        def validate(game, commanders):
            assert not isDead(game, 'Red0')
            assert not isDead(game, 'Blue0')
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_OrdersIssuedDuringInitializeAreIgnored(self):
        class RedCommander(api.commander.Commander):
            def initialize(self):
                self.issue(Move, self.game.bots['Red0'], Vector2(12, 30), 'move');

            def tick(self):
                pass

        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = {'Red0': (Vector2(10, 30), Vector2(1, 0))}
        self.config.red.commander = RedCommander

        self.config.gameLength = 3
        self.initializationTime = 2

        def validate(game, commanders):
            assert isSimilar(position(game, 'Red0'), Vector2(10, 30))
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate
