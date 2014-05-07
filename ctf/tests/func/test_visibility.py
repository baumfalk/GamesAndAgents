from tests.helpers import *


FRAME_DURATION_IN_SECONDS = 0.034


class TestVisibilityInformation(TestSuite):

    def test_TwoOnTwoEveryoneSeesEveryone(self):
        self.config.red.numberBots = 2
        self.config.red.botSpawnLocations = {'Red0': (Vector2(18, 16), Vector2(1, 0)), 'Red1': (Vector2(17, 16), Vector2(1, 0))}
        self.config.red.commander = Script([(0, Defend.create('Red0')), (0, Defend.create('Red1'))])

        self.config.blue.numberBots = 2
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(24, 16), Vector2(-1, 0)), 'Blue1': (Vector2(25, 16), Vector2(-1, 0))}
        self.config.blue.commander = Script([(0, Defend.create('Blue0')), (0, Defend.create('Blue1'))])

        self.config.gameLength = FRAME_DURATION_IN_SECONDS

        def validate(game, commanders):            
            self.assertEquals(canSee  (game, 'Red0' ) , {'Blue0', 'Blue1'})
            self.assertEquals(canSee  (game, 'Red1' ) , {'Blue0', 'Blue1'})
            self.assertEquals(canSee  (game, 'Blue0') , {'Red0' , 'Red1'})
            self.assertEquals(canSee  (game, 'Blue1') , {'Red0' , 'Red1'})
            self.assertEquals(isSeenBy(game, 'Red0' ) , {'Blue0', 'Blue1'})
            self.assertEquals(isSeenBy(game, 'Red1' ) , {'Blue0', 'Blue1'})
            self.assertEquals(isSeenBy(game, 'Blue0') , {'Red0' , 'Red1'})
            self.assertEquals(isSeenBy(game, 'Blue1') , {'Red0' , 'Red1'})

            redCommander = [c for c in commanders if c.game.team.name == 'Red'][0]
            self.assertEquals(canSeeAccordingToCommander  (redCommander, 'Red0' ) , {'Blue0', 'Blue1'})
            self.assertEquals(canSeeAccordingToCommander  (redCommander, 'Red1' ) , {'Blue0', 'Blue1'})
            self.assertEquals(canSeeAccordingToCommander  (redCommander, 'Blue0') , {'Red0' , 'Red1' })
            self.assertEquals(canSeeAccordingToCommander  (redCommander, 'Blue1') , {'Red0' , 'Red1' })
            self.assertEquals(isSeenByAccordingToCommander(redCommander, 'Red0' ) , {'Blue0', 'Blue1'})
            self.assertEquals(isSeenByAccordingToCommander(redCommander, 'Red1' ) , {'Blue0', 'Blue1'})
            self.assertEquals(isSeenByAccordingToCommander(redCommander, 'Blue0') , {'Red0' , 'Red1' })
            self.assertEquals(isSeenByAccordingToCommander(redCommander, 'Blue1') , {'Red0' , 'Red1' })
            self.assertEquals(lastSeenTimeAccordingToCommander(redCommander, 'Red0' ) , 0.0)
            self.assertEquals(lastSeenTimeAccordingToCommander(redCommander, 'Red1' ) , 0.0)
            self.assertEquals(lastSeenTimeAccordingToCommander(redCommander, 'Blue0') , 0.0)
            self.assertEquals(lastSeenTimeAccordingToCommander(redCommander, 'Blue1') , 0.0)
            self.assertEquals(positionAccordingToCommander(redCommander, 'Red0' ) , position(game, 'Red0' ))
            self.assertEquals(positionAccordingToCommander(redCommander, 'Red1' ) , position(game, 'Red1' ))
            self.assertEquals(positionAccordingToCommander(redCommander, 'Blue0') , position(game, 'Blue0'))
            self.assertEquals(positionAccordingToCommander(redCommander, 'Blue1') , position(game, 'Blue1'))
            self.assertEquals(facingDirectionAccordingToCommander(redCommander, 'Red0' ) , facingDirection(game, 'Red0' ))
            self.assertEquals(facingDirectionAccordingToCommander(redCommander, 'Red1' ) , facingDirection(game, 'Red1' ))
            self.assertEquals(facingDirectionAccordingToCommander(redCommander, 'Blue0') , facingDirection(game, 'Blue0'))
            self.assertEquals(facingDirectionAccordingToCommander(redCommander, 'Blue1') , facingDirection(game, 'Blue1'))

            blueCommander = [c for c in commanders if c.game.team.name == 'Blue'][0]
            self.assertEquals(canSeeAccordingToCommander  (blueCommander, 'Red0' ) , {'Blue0', 'Blue1'})
            self.assertEquals(canSeeAccordingToCommander  (blueCommander, 'Red1' ) , {'Blue0', 'Blue1'})
            self.assertEquals(canSeeAccordingToCommander  (blueCommander, 'Blue0') , {'Red0' , 'Red1' })
            self.assertEquals(canSeeAccordingToCommander  (blueCommander, 'Blue1') , {'Red0' , 'Red1' })
            self.assertEquals(isSeenByAccordingToCommander(blueCommander, 'Red0' ) , {'Blue0', 'Blue1'})
            self.assertEquals(isSeenByAccordingToCommander(blueCommander, 'Red1' ) , {'Blue0', 'Blue1'})
            self.assertEquals(isSeenByAccordingToCommander(blueCommander, 'Blue0') , {'Red0' , 'Red1' })
            self.assertEquals(isSeenByAccordingToCommander(blueCommander, 'Blue1') , {'Red0' , 'Red1' })
            self.assertEquals(lastSeenTimeAccordingToCommander(blueCommander, 'Red0' ) , 0.0)
            self.assertEquals(lastSeenTimeAccordingToCommander(blueCommander, 'Red1' ) , 0.0)
            self.assertEquals(lastSeenTimeAccordingToCommander(blueCommander, 'Blue0') , 0.0)
            self.assertEquals(lastSeenTimeAccordingToCommander(blueCommander, 'Blue1') , 0.0)
            self.assertEquals(positionAccordingToCommander(blueCommander, 'Red0' ) , position(game, 'Red0' ))
            self.assertEquals(positionAccordingToCommander(blueCommander, 'Red1' ) , position(game, 'Red1' ))
            self.assertEquals(positionAccordingToCommander(blueCommander, 'Blue0') , position(game, 'Blue0'))
            self.assertEquals(positionAccordingToCommander(blueCommander, 'Blue1') , position(game, 'Blue1'))
            self.assertEquals(facingDirectionAccordingToCommander(blueCommander, 'Red0' ) , facingDirection(game, 'Red0' ))
            self.assertEquals(facingDirectionAccordingToCommander(blueCommander, 'Red1' ) , facingDirection(game, 'Red1' ))
            self.assertEquals(facingDirectionAccordingToCommander(blueCommander, 'Blue0') , facingDirection(game, 'Blue0'))
            self.assertEquals(facingDirectionAccordingToCommander(blueCommander, 'Blue1') , facingDirection(game, 'Blue1'))

            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_TwoBotsTurnedAwayDoNotSeeButAreVisible(self):
        self.config.red.numberBots = 2
        self.config.red.botSpawnLocations = {'Red0': (Vector2(18, 16), Vector2(1, 0)), 'Red1': (Vector2(17, 16), Vector2(1, 0))}
        self.config.red.commander = Script([(0, Defend.create('Red0')), (0, Defend.create('Red1'))])

        self.config.blue.numberBots = 2
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(24, 16), Vector2(1, 0)), 'Blue1': (Vector2(25, 16), Vector2(1, 0))}
        self.config.blue.commander = Script([(0, Defend.create('Blue0')), (0, Defend.create('Blue1'))])

        self.config.gameLength = 0.2

        def validate(game, commanders):
            self.assertEquals(canSee  (game, 'Red0' ) , {'Blue0', 'Blue1'})
            self.assertEquals(canSee  (game, 'Red1' ) , {'Blue0', 'Blue1'})
            self.assertEquals(canSee  (game, 'Blue0') , set())
            self.assertEquals(canSee  (game, 'Blue1') , set())
            self.assertEquals(isSeenBy(game, 'Red0' ) , set())
            self.assertEquals(isSeenBy(game, 'Red1' ) , set())
            self.assertEquals(isSeenBy(game, 'Blue0') , set())
            self.assertEquals(isSeenBy(game, 'Blue1') , set())

            redCommander = [c for c in commanders if c.game.team.name == 'Red'][0]
            self.assertEquals(canSeeAccordingToCommander  (redCommander, 'Red0' ) , {'Blue0', 'Blue1'})
            self.assertEquals(canSeeAccordingToCommander  (redCommander, 'Red1' ) , {'Blue0', 'Blue1'})
            self.assertEquals(canSeeAccordingToCommander  (redCommander, 'Blue0') , set())
            self.assertEquals(canSeeAccordingToCommander  (redCommander, 'Blue1') , set())
            self.assertEquals(isSeenByAccordingToCommander(redCommander, 'Red0' ) , set())
            self.assertEquals(isSeenByAccordingToCommander(redCommander, 'Red1' ) , set())
            self.assertEquals(isSeenByAccordingToCommander(redCommander, 'Blue0') , {'Red0', 'Red1'})
            self.assertEquals(isSeenByAccordingToCommander(redCommander, 'Blue1') , {'Red0', 'Red1'})
            self.assertEquals(lastSeenTimeAccordingToCommander(redCommander, 'Red0' ) , 0.0)
            self.assertEquals(lastSeenTimeAccordingToCommander(redCommander, 'Red1' ) , 0.0)
            self.assertEquals(lastSeenTimeAccordingToCommander(redCommander, 'Blue0') , 0.0)
            self.assertEquals(lastSeenTimeAccordingToCommander(redCommander, 'Blue1') , 0.0)
            self.assertEquals(positionAccordingToCommander(redCommander, 'Red0' ) , position(game, 'Red0' ))
            self.assertEquals(positionAccordingToCommander(redCommander, 'Red1' ) , position(game, 'Red1' ))
            self.assertEquals(positionAccordingToCommander(redCommander, 'Blue0') , position(game, 'Blue0'))
            self.assertEquals(positionAccordingToCommander(redCommander, 'Blue1') , position(game, 'Blue1'))
            self.assertEquals(facingDirectionAccordingToCommander(redCommander, 'Red0' ) , facingDirection(game, 'Red0' ))
            self.assertEquals(facingDirectionAccordingToCommander(redCommander, 'Red1' ) , facingDirection(game, 'Red1' ))
            self.assertEquals(facingDirectionAccordingToCommander(redCommander, 'Blue0') , facingDirection(game, 'Blue0'))
            self.assertEquals(facingDirectionAccordingToCommander(redCommander, 'Blue1') , facingDirection(game, 'Blue1'))

            blueCommander = [c for c in commanders if c.game.team.name == 'Blue'][0]
            self.assertEquals(canSeeAccordingToCommander  (blueCommander, 'Red0' ) , set())
            self.assertEquals(canSeeAccordingToCommander  (blueCommander, 'Red1' ) , set())
            self.assertEquals(canSeeAccordingToCommander  (blueCommander, 'Blue0') , set())
            self.assertEquals(canSeeAccordingToCommander  (blueCommander, 'Blue1') , set())
            self.assertEquals(isSeenByAccordingToCommander(blueCommander, 'Red0' ) , set())
            self.assertEquals(isSeenByAccordingToCommander(blueCommander, 'Red1' ) , set())
            self.assertEquals(isSeenByAccordingToCommander(blueCommander, 'Blue0') , set())
            self.assertEquals(isSeenByAccordingToCommander(blueCommander, 'Blue1') , set())
            assert lastSeenTimeAccordingToCommander(blueCommander, 'Red0' ) >= self.config.gameLength - FRAME_DURATION_IN_SECONDS
            assert lastSeenTimeAccordingToCommander(blueCommander, 'Red1' ) >= self.config.gameLength - FRAME_DURATION_IN_SECONDS
            self.assertEquals(lastSeenTimeAccordingToCommander(blueCommander, 'Blue0') , 0.0)
            self.assertEquals(lastSeenTimeAccordingToCommander(blueCommander, 'Blue1') , 0.0)
            assert isSimilar(positionAccordingToCommander(blueCommander, 'Red0' ), Vector2(18, 16))
            assert isSimilar(positionAccordingToCommander(blueCommander, 'Red1' ), Vector2(17, 16))
            assert isSimilar(positionAccordingToCommander(blueCommander, 'Blue0'), position(game, 'Blue0'))
            assert isSimilar(positionAccordingToCommander(blueCommander, 'Blue1'), position(game, 'Blue1'))
            assert isSimilar(facingDirectionAccordingToCommander(blueCommander, 'Red0' ), Vector2(1, 0))
            assert isSimilar(facingDirectionAccordingToCommander(blueCommander, 'Red1' ), Vector2(1, 0))
            assert isSimilar(facingDirectionAccordingToCommander(blueCommander, 'Blue0'), facingDirection(game, 'Blue0'))
            assert isSimilar(facingDirectionAccordingToCommander(blueCommander, 'Blue1'), facingDirection(game, 'Blue1'))
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_OneBotTurnedAwayDoesNotSeeButSharesVisibility(self):
        self.config.red.numberBots = 2
        self.config.red.botSpawnLocations = {'Red0': (Vector2(10, 14), Vector2(1, 0)), 'Red1': (Vector2(17, 16), Vector2(1, 0))}
        self.config.red.commander = Script([(0.0, Defend.create('Red0')), (0.0, Defend.create('Red1'))])

        self.config.blue.numberBots = 2
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(24, 16), Vector2(1, 0)), 'Blue1': (Vector2(10, 20), Vector2(1, 0))}
        self.config.blue.commander = Script([(0.0, Defend.create('Blue0')), (0.0, Defend.create('Blue1'))])

        self.config.gameLength = 0.5

        def validate(game, commanders):        
            self.assertEquals(canSee  (game, 'Red0' ) , {'Blue0'})
            self.assertEquals(canSee  (game, 'Red1' ) , {'Blue0'})
            self.assertEquals(canSee  (game, 'Blue0') , set())
            self.assertEquals(canSee  (game, 'Blue1') , {'Red1'})
            self.assertEquals(isSeenBy(game, 'Red0' ) , set())
            self.assertEquals(isSeenBy(game, 'Red1' ) , set())
            self.assertEquals(isSeenBy(game, 'Blue0') , set())
            self.assertEquals(isSeenBy(game, 'Blue1') , set())

            redCommander = [c for c in commanders if c.game.team.name == 'Red'][0]
            self.assertEquals(canSeeAccordingToCommander  (redCommander, 'Red0' ) , {'Blue0'})
            self.assertEquals(canSeeAccordingToCommander  (redCommander, 'Red1' ) , {'Blue0'})
            self.assertEquals(canSeeAccordingToCommander  (redCommander, 'Blue0') , set())
            self.assertEquals(canSeeAccordingToCommander  (redCommander, 'Blue1') , set())
            self.assertEquals(isSeenByAccordingToCommander(redCommander, 'Red0' ) , set())
            self.assertEquals(isSeenByAccordingToCommander(redCommander, 'Red1' ) , set())
            self.assertEquals(isSeenByAccordingToCommander(redCommander, 'Blue0') , {'Red0', 'Red1'})
            self.assertEquals(isSeenByAccordingToCommander(redCommander, 'Blue1') , set())
            self.assertEquals(lastSeenTimeAccordingToCommander(redCommander, 'Blue0') , 0.0)
            assert lastSeenTimeAccordingToCommander(redCommander, 'Blue1') >= self.config.gameLength - FRAME_DURATION_IN_SECONDS
            assert isSimilar(positionAccordingToCommander(redCommander, 'Blue0'), position(game, 'Blue0'))
            assert isSimilar(positionAccordingToCommander(redCommander, 'Blue1'), Vector2(10, 20))

            blueCommander = [c for c in commanders if c.game.team.name == 'Blue'][0]
            self.assertEquals(canSeeAccordingToCommander  (blueCommander, 'Red0' ) , set())
            self.assertEquals(canSeeAccordingToCommander  (blueCommander, 'Red1' ) , {'Blue0'})
            self.assertEquals(canSeeAccordingToCommander  (blueCommander, 'Blue0') , set())
            self.assertEquals(canSeeAccordingToCommander  (blueCommander, 'Blue1') , {'Red1' })
            self.assertEquals(isSeenByAccordingToCommander(blueCommander, 'Red0' ) , set())
            self.assertEquals(isSeenByAccordingToCommander(blueCommander, 'Red1' ) , {'Blue1'})
            self.assertEquals(isSeenByAccordingToCommander(blueCommander, 'Blue0') , {'Red1' })
            self.assertEquals(isSeenByAccordingToCommander(blueCommander, 'Blue1') , set())
            assert blueCommander.game.bots['Red0'].seenlast >= self.config.gameLength - FRAME_DURATION_IN_SECONDS
            self.assertEquals(blueCommander.game.bots['Red1'].seenlast , 0.0)
            assert isSimilar(positionAccordingToCommander(blueCommander, 'Red0'), Vector2(10, 14))
            assert isSimilar(positionAccordingToCommander(blueCommander, 'Red1'), position(game, 'Red1'))

            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_UpdatedVisibilityWhenShotFired(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = {'Red0': (Vector2(18, 18), Vector2(1, 0))}
        self.config.red.commander = Script([(0.0, Defend.create('Red0'))])

        self.config.blue.numberBots = 2
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(24, 18), Vector2(1, 0)), 'Blue1': (Vector2(18, 24), Vector2(1, 0))}
        self.config.blue.commander = Script([(0.0, Defend.create('Blue0')), (0.0, Defend.create('Blue1'))])

        self.config.gameLength = 3.2

        def validate(game, commanders):
            assert isDead(game, 'Blue0')
            for commander in commanders:
                assert hasEvent(commander, CombatEvent.TYPE_KILLED, ['Red0'], 'Blue0', [0, self.config.gameLength])
                assert not hasEvent(commander, CombatEvent.TYPE_KILLED, subject = 'Blue1')
                assert not hasEvent(commander, CombatEvent.TYPE_KILLED, subject = 'Red0')

            self.assertEquals(canSee  (game, 'Red0' ) , set())
            self.assertEquals(canSee  (game, 'Blue0') , set())
            self.assertEquals(canSee  (game, 'Blue1') , {'Red0'})
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
            assert lastSeenTimeAccordingToCommander(redCommander, 'Blue1') >= self.config.gameLength - FRAME_DURATION_IN_SECONDS
            assert isSimilar(positionAccordingToCommander(redCommander, 'Blue0'), position(game, 'Blue0'))
            assert isSimilar(positionAccordingToCommander(redCommander, 'Blue1'), Vector2(18, 24))

            blueCommander = [c for c in commanders if c.game.team.name == 'Blue'][0]
            self.assertEquals(canSeeAccordingToCommander  (blueCommander, 'Red0' ) , set())
            self.assertEquals(canSeeAccordingToCommander  (blueCommander, 'Blue0') , set())
            self.assertEquals(canSeeAccordingToCommander  (blueCommander, 'Blue1') , {'Red0'})
            self.assertEquals(isSeenByAccordingToCommander(blueCommander, 'Red0' ) , set())
            self.assertEquals(isSeenByAccordingToCommander(blueCommander, 'Blue0') , set())
            self.assertEquals(isSeenByAccordingToCommander(blueCommander, 'Blue1') , set())
            assert blueCommander.game.bots['Red0'].seenlast > 0.0
            assert isSimilar(positionAccordingToCommander(blueCommander, 'Red0'), position(game, 'Red0'))
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_BotsInSpawnBaseCanBeSeen(self):
        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = {'Red0': (Vector2(6, 2), Vector2(1, 0))}
        self.config.red.commander = Script([(0, Defend.create('Red0'))])

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = { 'Blue0': (Vector2(17, 2), Vector2(-1, 0)) }
        self.config.blue.commander = Script([(0.5, Defend.create('Blue0', Vector2(-1, 0)))])

        self.config.gameLength = 0.1

        def validate(game, commanders):
            assert not isDead(game, 'Red0')
            assert not isDead(game, 'Blue0')

            self.assertEquals(isSeenBy(game, 'Red0' ) , {'Blue0'})
            self.assertEquals(isSeenBy(game, 'Blue0') , {'Red0'})

            redCommander = [c for c in commanders if c.game.team.name == 'Red'][0]
            self.assertEquals(canSeeAccordingToCommander  (redCommander, 'Red0' ) , {'Blue0'})
            self.assertEquals(canSeeAccordingToCommander  (redCommander, 'Blue0') , {'Red0'})
            self.assertEquals(isSeenByAccordingToCommander(redCommander, 'Red0' ) , {'Blue0'})
            self.assertEquals(isSeenByAccordingToCommander(redCommander, 'Blue0') , {'Red0'})

            blueCommander = [c for c in commanders if c.game.team.name == 'Blue'][0]
            self.assertEquals(canSeeAccordingToCommander  (blueCommander, 'Red0' ) , {'Blue0'})
            self.assertEquals(canSeeAccordingToCommander  (blueCommander, 'Blue0') , {'Red0'})
            self.assertEquals(isSeenByAccordingToCommander(blueCommander, 'Red0' ) , {'Blue0'})
            self.assertEquals(isSeenByAccordingToCommander(blueCommander, 'Blue0') , {'Red0'})
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate

