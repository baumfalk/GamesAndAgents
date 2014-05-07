from tests.helpers import *

class TestShooting(TestSuite):

    def test_BotShootsNearbyEnemyThatShotHisTeamMate(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = {'Red0': (Vector2(18, 18), Vector2(1, 0))}
        self.config.red.commander = Script([(0.0, Defend.create('Red0'))])

        self.config.blue.numberBots = 2
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(24, 18), Vector2(1, 0)), 'Blue1': (Vector2(18, 24), Vector2(1, 0))}
        self.config.blue.commander = Script([(0.0, Defend.create('Blue0')), (0.0, Defend.create('Blue1'))])

        self.config.gameLength = 6.0

        def validate(game, commanders):
            assert isDead(game, 'Red0')
            assert isDead(game, 'Blue0')
            for commander in commanders:
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, ['Red0'], 'Blue0', [0, self.config.gameLength])
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, ['Blue1'], 'Red0', [0, self.config.gameLength])
                assert not hasEvent(commander, CombatEvent.TYPE_KILLED, subject = 'Blue1')

            self.assertEquals(canSee  (game, 'Red0' ) , set())
            self.assertEquals(canSee  (game, 'Blue0') , set())
            self.assertEquals(canSee  (game, 'Blue1') , set())
            self.assertEquals(isSeenBy(game, 'Red0' ) , set())
            self.assertEquals(isSeenBy(game, 'Blue0') , set())
            self.assertEquals(isSeenBy(game, 'Blue1') , set())

            redCommander = [c for c in commanders if c.game.team.name == 'Red'][0]
            self.assertEquals(canSeeAccordingToCommander  (redCommander, 'Red0' ) , set())
            self.assertEquals(canSeeAccordingToCommander  (redCommander, 'Blue0') , set())
            self.assertEquals(canSeeAccordingToCommander  (redCommander, 'Blue1') , set())
            self.assertEquals(isSeenByAccordingToCommander(redCommander, 'Red0' ) , set())
            self.assertEquals(isSeenByAccordingToCommander(redCommander, 'Blue0') , set())
            self.assertEquals(isSeenByAccordingToCommander(redCommander, 'Blue1') , set())
            self.assertEquals(lastSeenTimeAccordingToCommander(redCommander, 'Blue0') , 0.0)
            assert lastSeenTimeAccordingToCommander(redCommander, 'Blue1') > 0.0
            assert isSimilar(positionAccordingToCommander(redCommander, 'Blue0'), position(game, 'Blue0'))
            assert isSimilar(positionAccordingToCommander(redCommander, 'Blue1'), position(game, 'Blue1'))

            blueCommander = [c for c in commanders if c.game.team.name == 'Blue'][0]
            self.assertEquals(canSeeAccordingToCommander  (blueCommander, 'Red0' ) , set())
            self.assertEquals(canSeeAccordingToCommander  (blueCommander, 'Blue0') , set())
            self.assertEquals(canSeeAccordingToCommander  (blueCommander, 'Blue1') , set())
            self.assertEquals(isSeenByAccordingToCommander(blueCommander, 'Red0' ) , set())
            self.assertEquals(isSeenByAccordingToCommander(blueCommander, 'Blue0') , set())
            self.assertEquals(isSeenByAccordingToCommander(blueCommander, 'Blue1') , set())
            self.assertEquals(blueCommander.game.bots['Red0'].seenlast , 0.0)
            assert isSimilar(positionAccordingToCommander(blueCommander, 'Red0'), position(game, 'Red0'))
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_OneAttackerResumesMovingAfterPausingIfBlockingBotLooksAway(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = {'Red0': (Vector2(10, 16), Vector2(-1, 0))}
        self.config.red.commander = Script([(0.0, Attack.create('Red0', Vector2(30, 16)))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(32, 16), Vector2(-1, 0))}
        self.config.blue.commander = Script([(0.0, Defend.create('Blue0', Vector2(-1, 0))), (4.0, Defend.create('Blue0', Vector2(1, 0)))])

        self.config.gameLength = 8.0

        def validate(game, commanders):
            assert not isDead(game, 'Red0')
            assert isDead(game, 'Blue0')
            for commander in commanders:
                assert not hasEvent(commander, CombatEvent.TYPE_KILLED, subject = 'Red0')
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, 'Red0', 'Blue0', [4, self.config.gameLength])

            redCommander = [c for c in commanders if c.game.team.name == 'Red'][0]
            self.assertEquals(redCommander.game.bots['Red0'].state , BotInfo.STATE_ATTACKING)
            self.assertEquals(redCommander.game.bots['Blue0'].state , BotInfo.STATE_DEAD)

            blueCommander = [c for c in commanders if c.game.team.name == 'Blue'][0]
            self.assertEquals(blueCommander.game.bots['Red0'].state , BotInfo.STATE_HOLDING)
            self.assertEquals(blueCommander.game.bots['Blue0'].state , BotInfo.STATE_DEAD)
            
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_OneAttackerResumesMovingAfterPausingIfBlockingBotIsKilled(self):
        self.config.red.numberBots = 2
        self.config.red.botSpawnLocations = {'Red0': (Vector2(10, 16), Vector2(-1, 0)), 'Red1': (Vector2(32, 40), Vector2(0, -1))}
        self.config.red.commander = Script([(0.0, Attack.create('Red0', Vector2(32, 16))), (0.0, Attack.create('Red1', Vector2(32, 16)))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(32, 16), Vector2(-1, 0))}
        self.config.blue.commander = Script([(0.0, Defend.create('Blue0', Vector2(-1, 0)))])

        self.config.gameLength = 6.0

        def validate(game, commanders):
            assert not isDead(game, 'Red0')
            assert not isDead(game, 'Red1')
            assert isDead(game, 'Blue0')
            for commander in commanders:
                assert not hasEvent(commander, CombatEvent.TYPE_KILLED, subject = 'Red0')
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, 'Red1', 'Blue0', [0, self.config.gameLength])

            redCommander = [c for c in commanders if c.game.team.name == 'Red'][0]
            self.assertEquals(redCommander.game.bots['Red0'].state , BotInfo.STATE_ATTACKING)
            self.assertEquals(redCommander.game.bots['Red1'].state , BotInfo.STATE_ATTACKING)
            self.assertEquals(redCommander.game.bots['Blue0'].state , BotInfo.STATE_DEAD)

            blueCommander = [c for c in commanders if c.game.team.name == 'Blue'][0]
            self.assertEquals(blueCommander.game.bots['Red0'].state , BotInfo.STATE_HOLDING)
            self.assertEquals(blueCommander.game.bots['Red1'].state , BotInfo.STATE_IDLE)
            self.assertEquals(blueCommander.game.bots['Blue0'].state , BotInfo.STATE_DEAD)

            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_AutoTargettingSwapsTargetAfterKillingGuy(self):
        self.config.red.numberBots = 2
        self.config.red.botSpawnLocations = {'Red0': (Vector2(18, 16), Vector2(1, 0)), 'Red1': (Vector2(17, 16), Vector2(1, 0))}
        self.config.red.commander = Script([(0.0, Defend.create('Red0')), (0.0, Defend.create('Red1'))])

        self.config.blue.numberBots = 2
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(24, 16), Vector2(-1, 0)), 'Blue1': (Vector2(25, 16), Vector2(-1, 0))}
        self.config.blue.commander = Script([(0.0, Defend.create('Blue0')), (0.0, Defend.create('Blue1'))])

        self.config.gameLength = 4

        def validate(game, commanders):
            assert isDead(game, 'Red0')
            assert isDead(game, 'Red1')
            assert isDead(game, 'Blue0')
            assert isDead(game, 'Blue1')
            for commander in commanders:
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, ['Red0', 'Red1'], 'Blue0', [0, self.config.gameLength])
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, ['Red0', 'Red1'], 'Blue1', [0, self.config.gameLength])
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, ['Blue0', 'Blue1'], 'Red0', [0, self.config.gameLength])
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, ['Blue0', 'Blue1'], 'Red1', [0, self.config.gameLength])
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_BotResumesChargeOrderAfterShooting(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = {'Red0': (Vector2(10, 20), Vector2(1, 0))}
        self.config.red.commander = Script([(0, Charge.create('Red0', [Vector2(10, 20), Vector2(30, 20), Vector2(30, 20)]))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(30, 20), Vector2(1, 0))}
        self.config.blue.commander = Script([])

        # Red0 should skip the first waypoint when it resumes the Charge order.
        # This time needs to be short enough that the bot doesn't have time to
        # return back to the first waypoint.
        self.config.gameLength = 6.0

        def validate(game, commanders):
            assert not isDead(game, 'Red0')
            assert isDead(game, 'Blue0')
            assert isSimilar(position(game, 'Red0'), Vector2(30, 20), 0.5)
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_BotResumesDefendOrderAfterShooting(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = {'Red0': (Vector2(10, 20), Vector2(1, 0))}
        self.config.red.commander = Script([(0, Defend.create('Red0'))])

        self.config.blue.numberBots = 2
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(25, 20), Vector2(-1, 0)), 'Blue1': (Vector2(30, 20), Vector2(-1, 0))}
        self.config.blue.commander = Script([(0, Move.create('Blue0', Vector2(10, 20))), (0, Move.create('Blue1', Vector2(10, 20)))])

        self.config.gameLength = 10.0

        def validate(game, commanders):
            assert not isDead(game, 'Red0')
            assert isDead(game, 'Blue0')
            assert isDead(game, 'Blue1')
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_BotDoesNotResumePreviousCommandAfterNewCommand(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = {'Red0': (Vector2(10, 20), Vector2(1, 0))}

        # Before the bot gets to (30, 20) we send it to (15, 15).
        self.config.red.commander = Script([(0, Move.create('Red0', Vector2(30, 20))), (2, Move.create('Red0', Vector2(15, 15)))])

        self.config.gameLength = 7.0

        def validate(game, commanders):            
            assert isSimilar(position(game, 'Red0'), Vector2(15, 15), 0.5)
            # if this test isn't working the bot will go to (15, 15) then resume the order to got to (30, 20)
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


class TestHoldingState(TestSuite):

    def test_OneAttackerStopsBeforeEnteringDefenderRange(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = {'Red0': (Vector2(10, 16), Vector2(-1, 0))}
        self.config.red.commander = Script([(0.0, Attack.create('Red0', Vector2(32, 16)))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(32, 16), Vector2(-1, 0))}
        self.config.blue.commander = Script([(0.0, Defend.create('Blue0'))])

        self.config.gameLength = 10

        def validate(game, commanders):
            assert not isDead(game, 'Red0')
            assert not isDead(game, 'Blue0')
            for commander in commanders:
                self.assertEquals(commander.game.bots['Red0'].state , BotInfo.STATE_HOLDING)
                self.assertEquals(commander.game.bots['Blue0'].state , BotInfo.STATE_DEFENDING)
                assert not hasEvent(commander, CombatEvent.TYPE_KILLED, 'Blue0', 'Red0', [0, self.config.gameLength])
                assert not hasEvent(commander, CombatEvent.TYPE_KILLED, subject = 'Blue0')
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_HoldingAttackerCanAttackInDifferentDirection(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = {'Red0': (Vector2(10, 16), Vector2(-1, 0))}
        self.config.red.commander = Script([(0.0, Attack.create('Red0', Vector2(20, 16))),
                                            (4.0, Attack.create('Red0', Vector2(10, 16)))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(32, 16), Vector2(-1, 0))}
        self.config.blue.commander = Script([(0.0, Defend.create('Blue0'))])

        self.config.gameLength = 8.0

        def validate(game, commanders):
            assert not isDead(game, 'Red0')
            assert not isDead(game, 'Blue0')
            assert isSimilar(position(game, 'Red0'), Vector2(10, 16), 0.3)
            for commander in commanders:
                self.assertEquals(commander.game.bots['Red0'].state, BotInfo.STATE_IDLE)
                self.assertEquals(commander.game.bots['Blue0'].state, BotInfo.STATE_DEFENDING)
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate
