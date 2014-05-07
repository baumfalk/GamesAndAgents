from tests.helpers import *


class TestAmbushBalance(TestSuite):

    def test_OneAttackerDiesAgainstTwoWaitingDefenders(self):
        self.config.red.numberBots = 2
        self.config.red.botSpawnLocations = {
                'Red0': (Vector2(20, 15), Vector2(1, 0)),
                'Red1': (Vector2(20, 15), Vector2(1, 0)),
        }
        self.config.red.commander = Script([(0.0, Defend.create('Red0')), (0.0, Defend.create('Red1'))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = {
                'Blue0': (Vector2(20, 37), Vector2(0, -1))
        }
        self.config.blue.commander = Script([(0.0, Attack.create('Blue0', Vector2(20, 10)))])

        self.config.gameLength = 6.0

        def validate(game, commanders):
            assert isDead(game, 'Blue0')
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_ThreeAttackersTwoDieAgainstOneDefender(self):
        self.config.red.numberBots = 3
        self.config.red.botSpawnLocations = {
                'Red0': (Vector2(53, 36), Vector2(1, 0)),
                'Red1': (Vector2(52, 36), Vector2(1, 0)),
                'Red2': (Vector2(51, 36), Vector2(1, 0))
        }
        self.config.red.commander = Script([(2.0, Attack.create('Red0', Vector2(75, 36))),
                                            (2.0, Attack.create('Red1', Vector2(75, 36))),
                                            (2.0, Attack.create('Red2', Vector2(75, 36)))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(66, 40), Vector2(0, -1))}
        self.config.blue.commander = Script([(0.0, Defend.create('Blue0'))])

        self.config.gameLength = 10.0

        def validate(game, commanders):
            assert isDead(game, 'Red0')
            assert isDead(game, 'Red1')
            assert not isDead(game, 'Red2')
            assert isDead(game, 'Blue0')
            for commander in commanders:
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, 'Blue0', 'Red0', [0, self.config.gameLength])
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, 'Blue0', 'Red1', [0, self.config.gameLength])
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, 'Red2', 'Blue0', [0, self.config.gameLength])

            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_ThreeChargersTwoDieAgainstOneDefender(self):
        self.config.red.numberBots = 3
        self.config.red.botSpawnLocations = {
                'Red0': (Vector2(53, 36), Vector2(1, 0)),
                'Red1': (Vector2(52, 36), Vector2(1, 0)),
                'Red2': (Vector2(51, 36), Vector2(1, 0))
        }
        self.config.red.commander = Script([(2.0, Charge.create('Red0', Vector2(75, 36))),
                                            (2.0, Charge.create('Red1', Vector2(75, 36))),
                                            (2.0, Charge.create('Red2', Vector2(75, 36)))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = { 'Blue0': (Vector2(66, 40), Vector2(0, -1)) }
        self.config.blue.commander = Script([(0.0, Defend.create('Blue0'))])

        self.config.gameLength = 10.0

        def validate(game, commanders):
            # TODO!
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_OneMoverDecoyOneAttackerAgainstDefender(self):
        self.config.red.numberBots = 2
        self.config.red.botSpawnLocations = {
                'Red0': (Vector2(47, 30), Vector2(1, 0)),
                'Red1': (Vector2(54, 30), Vector2(1, 0))
        }
        self.config.red.commander = Script([(2.0, Move.create('Red0', Vector2(75, 30))),
                                            (2.0, Attack.create('Red1', Vector2(75, 30)))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(66, 40), Vector2(0, -1))}
        self.config.blue.commander = Script([(0.0, Defend.create('Blue0'))])

        self.config.gameLength = 10.0

        def validate(game, commanders):
            # TODO!
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


class TestOneVersusOne(TestSuite):

    def test_TwoDefendersBothDie(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = {'Red0': (Vector2(2, 16), Vector2(1, 0))}
        self.config.red.commander = Script([(0.0, Defend.create('Red0'))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(6, 16), Vector2(-1, 0))}
        self.config.blue.commander = Script([(0.0, Defend.create('Blue0'))])

        self.config.gameLength = 4.0

        def validate(game, commanders):
            assert isDead(game, 'Red0')
            assert isDead(game, 'Blue0')
            for commander in commanders:
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, 'Red0', 'Blue0', [0, self.config.gameLength])
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, 'Blue0', 'Red0', [0, self.config.gameLength])
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_TwoAttackersBothDieIfSpawnedInRange(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = {'Red0': (Vector2(12, 16), Vector2(1, 0))}
        self.config.red.commander = Script([(0.0, Attack.create('Red0', Vector2(20, 16)))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(20, 16), Vector2(-1, 0))}
        self.config.blue.commander = Script([(0.0, Attack.create('Blue0', Vector2(20, 16)))])

        self.config.gameLength = 2.0

        def validate(game, commanders):
            assert isDead(game, 'Red0')
            assert isDead(game, 'Blue0')
            for commander in commanders:
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, 'Red0', 'Blue0', [0, self.config.gameLength])
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, 'Blue0', 'Red0', [0, self.config.gameLength])
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_TwoAttackersBothStopOutOfRange(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = { 'Red0': (Vector2(12, 16), Vector2(1, 0)) }
        self.config.red.commander = Script([(0.0, Attack.create('Red0', Vector2(20, 16)))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = { 'Blue0': (Vector2(28, 16), Vector2(-1, 0)) }
        self.config.blue.commander = Script([(0.0, Attack.create('Blue0', Vector2(20, 16)))])

        self.config.gameLength = 2.0

        def validate(game, commanders):
            assert not isDead(game, 'Red0')
            assert not isDead(game, 'Blue0')
            for commander in commanders:
                assert not hasEvent(commander, CombatEvent.TYPE_KILLED, 'Red0', 'Blue0', [0, self.config.gameLength])
                assert not hasEvent(commander, CombatEvent.TYPE_KILLED, 'Blue0', 'Red0', [0, self.config.gameLength])
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_TwoChargersFaceEachOtherBothDie(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = { 'Red0': (Vector2(10, 16), Vector2(1, 0)) }
        self.config.red.commander = Script([(0.0, Charge.create('Red0', Vector2(20, 16)))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = { 'Blue0': (Vector2(30, 16), Vector2(-1, 0)) }
        self.config.blue.commander = Script([(0.0, Charge.create('Blue0', Vector2(20, 16)))])

        self.config.gameLength = 3.0

        def validate(game, commanders):
            assert isDead(game, 'Red0')
            assert isDead(game, 'Blue0')
            for commander in commanders:
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, 'Red0', 'Blue0', [0, self.config.gameLength])
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, 'Blue0', 'Red0', [0, self.config.gameLength])
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


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


    def test_OneAttackerWinsAgainstOneCharger(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = { 'Red0': (Vector2(12, 16), Vector2(1, 0)) }
        self.config.red.commander = Script([(0.0, Charge.create('Red0', Vector2(20, 16)))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = { 'Blue0': (Vector2(32, 16), Vector2(-1, 0)) }
        self.config.blue.commander = Script([(0.0, Attack.create('Blue0', Vector2(20, 16)))])

        self.config.gameLength = 4.0

        def validate(game, commanders):
            assert isDead(game, 'Red0')
            assert not isDead(game, 'Blue0')
            for commander in commanders:
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, 'Blue0', 'Red0', [0, self.config.gameLength])
                assert not hasEvent(commander, CombatEvent.TYPE_KILLED, subject = 'Blue0')
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_OneDefenderWinsAganstOneCharger(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = {'Red0': (Vector2(10, 16), Vector2(1, 0))}
        self.config.red.commander = Script([(0.0, Charge.create('Red0', Vector2(20, 16)))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(30, 16), Vector2(-1, 0))}
        self.config.blue.commander = Script([(0.0, Defend.create('Blue0'))])

        self.config.gameLength = 4.0

        def validate(game, commanders):
            assert isDead(game, 'Red0')
            assert not isDead(game, 'Blue0')
            for commander in commanders:
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, 'Blue0', 'Red0', [0, self.config.gameLength])
                assert not hasEvent(commander, CombatEvent.TYPE_KILLED, subject = 'Blue0')
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


class TestGroupBattles(TestSuite):

    def test_FiveAttackersWinEasilyAgainstFiveChargers(self):
        self.config.red.numberBots = 5
        self.config.red.botSpawnLocations = {
                'Red0': (Vector2(10, 16), Vector2(1, 0)),
                'Red1': (Vector2(10, 16), Vector2(1, 0)),
                'Red2': (Vector2(10, 16), Vector2(1, 0)),
                'Red3': (Vector2(10, 16), Vector2(1, 0)),
                'Red4': (Vector2(10, 16), Vector2(1, 0))
        }
        self.config.red.commander = Script([(0.0, Charge.create('Red0', Vector2(30, 16))),
                                            (0.0, Charge.create('Red1', Vector2(30, 16))),
                                            (0.0, Charge.create('Red2', Vector2(30, 16))),
                                            (0.0, Charge.create('Red3', Vector2(30, 16))),
                                            (0.0, Charge.create('Red4', Vector2(30, 16)))])

        self.config.blue.numberBots = 5
        self.config.blue.botSpawnLocations = {
                'Blue0': (Vector2(30, 16), Vector2(-1, 0)),
                'Blue1': (Vector2(30, 16), Vector2(-1, 0)),
                'Blue2': (Vector2(30, 16), Vector2(-1, 0)),
                'Blue3': (Vector2(30, 16), Vector2(-1, 0)),
                'Blue4': (Vector2(30, 16), Vector2(-1, 0))
        }
        self.config.blue.commander = Script([(0.0, Attack.create('Blue0', Vector2(10, 16))),
                                             (0.0, Attack.create('Blue1', Vector2(10, 16))),
                                             (0.0, Attack.create('Blue2', Vector2(10, 16))),
                                             (0.0, Attack.create('Blue3', Vector2(10, 16))),
                                             (0.0, Attack.create('Blue4', Vector2(10, 16)))])

        self.config.gameLength = 5.0

        def validate(game, commanders):
            self.assertEquals(numberAliveBots(game, ['Red0', 'Red1', 'Red2', 'Red3', 'Red4']) , 0)
            assert numberAliveBots(game, ['Blue0', 'Blue1', 'Blue2', 'Blue3', 'Blue4']) > 2
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


class TestAimingMechanics(TestSuite):

    def test_TheBotThatStartsShootingFirstWins(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = {'Red0': (Vector2(2, 16), Vector2(1, 0))}
        self.config.red.commander = Script([(0.0, Defend.create('Red0'))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(6, 16), Vector2(-1, 0))}
        # ideally we want this to be one frame later
        # but the best we can hope for is one commander tick later (4 frames)
        self.config.blue.commander = Script([(0.2, Defend.create('Blue0'))])

        self.config.gameLength = 4.0

        def validate(game, commanders):
            assert not isDead(game, 'Red0')
            assert isDead(game, 'Blue0')
            for commander in commanders:
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, 'Red0', 'Blue0', [0, self.config.gameLength])
                assert not hasEvent(commander, CombatEvent.TYPE_KILLED, subject = 'Red0')
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_TheBotThatHasToTurnFurtherDies(self):
        #TODO: Fix testcase or gamecode for the first pair of bots and

        #self.config.red.numberBots = 3
        #self.config.red.botSpawnLocations = {
        #        'Red0': (Vector2(9, 16), Vector2(1, 1)),
        #        'Red1': (Vector2(19, 36), Vector2(1, -1)),
        #        'Red2': (Vector2(40, 16), Vector2(-1, 0))
        #}
        #self.config.red.commander = Script([(0.0, Attack.create('Red0', Vector2(10, 17))),
        #                                    (0.0, Attack.create('Red1', Vector2(20, 35))),
        #                                    (0.5, Attack.create('Red2', Vector2(41, 16)))])

        #self.config.blue.numberBots = 3
        #self.config.blue.botSpawnLocations = {
        #        'Blue0': (Vector2(16, 16), Vector2(-1, 0.5)),
        #        'Blue1': (Vector2(26, 36), Vector2(-1, -0.5)),
        #        'Blue2': (Vector2(47, 16), Vector2(-0, 1))
        #}
        #self.config.blue.commander = Script([(0.0, Attack.create('Blue0', Vector2(15, 16.5))),
        #                                     (0.0, Attack.create('Blue1', Vector2(25, 35.5))),
        #                                     (0.5, Attack.create('Blue2', Vector2(46, 16)))])
        self.config.red.numberBots = 2
        self.config.red.botSpawnLocations = {
                'Red0': (Vector2(19, 36), Vector2(1, -1)),
                'Red1': (Vector2(40, 16), Vector2(-1, 0))
        }
        self.config.red.commander = Script([(0.0, Attack.create('Red0', Vector2(20, 35))),
                                            (0.5, Attack.create('Red1', Vector2(41, 16)))])

        self.config.blue.numberBots = 2
        self.config.blue.botSpawnLocations = {
                'Blue0': (Vector2(26, 36), Vector2(-1, -0.5)),
                'Blue1': (Vector2(47, 16), Vector2(-0, 1))
        }
        self.config.blue.commander = Script([(0.0, Attack.create('Blue0', Vector2(25, 35.5))),
                                             (0.5, Attack.create('Blue1', Vector2(46, 16)))])


        self.config.gameLength = 4.0

        #def validate(game, commanders):
        #    assert isDead(game, 'Red0')
        #    assert isDead(game, 'Red1')
        #    assert isDead(game, 'Red2')
        #    assert not isDead(game, 'Blue0')
        #    assert not isDead(game, 'Blue1')
        #    assert not isDead(game, 'Blue2')
        #    for commander in commanders:
        #        assert hasEvent(commander, CombatEvent.TYPE_KILLED, ['Blue0', 'Blue1', 'Blue2'], 'Red0', [0, self.config.gameLength])
        #        assert hasEvent(commander, CombatEvent.TYPE_KILLED, ['Blue0', 'Blue1', 'Blue2'], 'Red1', [0, self.config.gameLength])
        #        assert hasEvent(commander, CombatEvent.TYPE_KILLED, ['Blue0', 'Blue1', 'Blue2'], 'Red2', [0, self.config.gameLength])
        #        assert not hasEvent(commander, CombatEvent.TYPE_KILLED, subject = 'Blue0')
        #        assert not hasEvent(commander, CombatEvent.TYPE_KILLED, subject = 'Blue1')
        #        assert not hasEvent(commander, CombatEvent.TYPE_KILLED, subject = 'Blue2')
        #    validateCommanders(commanders)
        def validate(game, commanders):
            assert isDead(game, 'Red0')
            assert isDead(game, 'Red1')
            assert not isDead(game, 'Blue0')
            assert not isDead(game, 'Blue1')
            for commander in commanders:
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, ['Blue0', 'Blue1'], 'Red0', [0, self.config.gameLength])
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, ['Blue0', 'Blue1'], 'Red1', [0, self.config.gameLength])
                assert not hasEvent(commander, CombatEvent.TYPE_KILLED, subject = 'Blue0')
                assert not hasEvent(commander, CombatEvent.TYPE_KILLED, subject = 'Blue1')
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_TwoBotsTurnSameAngleBothDie(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = {'Red0': (Vector2(19, 16), Vector2(2, 1))}
        self.config.red.commander = Script([(0.0, Attack.create('Red0', Vector2(21, 17)))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(26, 16), Vector2(-2, 1))}
        self.config.blue.commander = Script([(0.0, Attack.create('Blue0', Vector2(24, 17)))])

        self.config.gameLength = 4.0

        def validate(game, commanders):
            assert isDead(game, 'Red0')
            assert isDead(game, 'Blue0')
            for commander in commanders:
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, 'Blue0', 'Red0', [0, self.config.gameLength])
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, 'Red0', 'Blue0', [0, self.config.gameLength])
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


class TestTwoVersusOne(TestSuite):

    def test_TwoDefendersWinsAgainstOneDefender(self):
        self.config.red.numberBots = 2
        self.config.red.botSpawnLocations = {
                'Red0': (Vector2(19, 15), Vector2(1, 0)),
                'Red1': (Vector2(19, 17), Vector2(1, 0))
        }
        self.config.red.commander = Script([(0.0, Defend.create('Red0')), (0.0, Defend.create('Red1'))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(26, 16), Vector2(-1, 0))}
        self.config.blue.commander = Script([(0.0, Defend.create('Blue0'))])

        self.config.gameLength = 4.0

        def validate(game, commanders):
            self.assertEquals(numberAliveBots(game, ['Red0', 'Red1']) , 1)
            assert isDead(game, 'Blue0')
            for commander in commanders:
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, 'Blue0', ['Red0', 'Red1'], [0, self.config.gameLength])
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, ['Red0', 'Red1'], 'Blue0', [0, self.config.gameLength])
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_TwoChargersTwoMetersApartWinAgainstOneDefender(self):
        self.config.red.numberBots = 2
        self.config.red.botSpawnLocations = {
                'Red0': (Vector2(11, 16), Vector2(1, 0)),
                'Red1': (Vector2(9, 16), Vector2(1, 0))
        }
        self.config.red.commander = Script([(0.0, Charge.create('Red0', Vector2(35, 16))), (0.0, Charge.create('Red1', Vector2(35, 16)))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(35, 16), Vector2(-1, 0))}
        self.config.blue.commander = Script([(0.0, Defend.create('Blue0'))])

        self.config.gameLength = 7.0

        def validate(game, commanders):
            assert isDead(game, 'Red0')
            assert not isDead(game, 'Red1')
            assert isDead(game, 'Blue0')
            for commander in commanders:
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, 'Blue0', 'Red0', [0, self.config.gameLength])
                assert not hasEvent(commander, CombatEvent.TYPE_KILLED, subject = 'Red1')
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, ['Red0', 'Red1'], 'Blue0', [0, self.config.gameLength])
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_TwoChargersSameDistanceWinAgainstOneDefender(self):
        self.config.red.numberBots = 2
        self.config.red.botSpawnLocations = {
                'Red0': (Vector2(10, 15), Vector2(1, 0)),
                'Red1': (Vector2(10, 17), Vector2(1, 0))
        }
        self.config.red.commander = Script([(0.0, Charge.create('Red0', Vector2(35, 16))), (0.0, Charge.create('Red1', Vector2(35, 16)))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = { 'Blue0': (Vector2(35, 16), Vector2(-1, 0)) }
        self.config.blue.commander = Script([(0.0, Defend.create('Blue0'))])

        self.config.gameLength = 4.0

        def validate(game, commanders):
            self.assertEquals(numberAliveBots(game, ['Red0', 'Red1']) , 1)
            assert isDead(game, 'Blue0')
            for commander in commanders:
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, ['Red0', 'Red1'], 'Blue0', [0, self.config.gameLength])
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate
