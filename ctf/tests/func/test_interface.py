import time
from tests.helpers import *


class TestInterface(TestSuite):

    def test_InitializeIsCalledOnCommanders(self):
        class RedCommander(api.commander.Commander):
            def initialize(self):
                self.initialized = True
                assert set([b.name for b in self.game.team.members]) == set(['Red0'])
            def tick(self):
                pass

        class BlueCommander(api.commander.Commander):
            def initialize(self):
                self.initialized = True
                assert set([b.name for b in self.game.team.members]) == set(['Blue0'])
            def tick(self):
                pass

        self.config.red.numberBots = 1
        self.config.red.botSpawnLocations = {'Red0': (Vector2(65, 45), Vector2(-0, 1))}
        self.config.red.commander = RedCommander

        self.config.blue.numberBots = 1
        self.config.blue.botSpawnLocations = {'Blue0': (Vector2(60, 42.5), Vector2(1, 0))}
        self.config.blue.commander = BlueCommander

    def validate_InitializeIsCalledOnCommanders(self, game, commanders):
        for commander in commanders:
            assert commander.initialized


    def test_StartImmediatelyIfCommandersDoNotOverrideIsReady(self):
        class RedCommander(api.commander.Commander):
            def initialize(self):
                self.initializationStart = time.clock()
            def tick(self):
                self.initializationTime = time.clock() - self.initializationStart

        self.config.red.commander = RedCommander

    def validate_StartImmediatelyIfCommandersDoNotOverrideIsReady(self, game, commanders):
        for commander in commanders:
            assert commander.initializationTime < 0.1


    def test_GameStartsWhenCommandersReady(self):
        class RedCommander(api.commander.Commander):
            def initialize(self):
                self.isReadyCallCount = 0
            # Wait for 10 ticks (approximately 1 second) before reporting isReady.
            def isReady(self):
                self.isReadyCallCount += 1
                return self.isReadyCallCount == 10
            def tick(self):
                pass

        self.config.red.commander = RedCommander
        self.config.initializationTime = 2.0

    def validate_GameStartsWhenCommandersReady(self, game, commanders):
        for commander in commanders:
            assert commander.isReadyCallCount == 10


    def test_InitializationTimeExpiresEvenIfCommandersAreNotReady(self):
        class RedCommander(api.commander.Commander):
            def initialize(self):
                self.isReadyCallCount = 0
            def isReady(self):
                self.isReadyCallCount += 1
                return False
            def tick(self):
                self.firstTickTime = time.clock()

        self.config.red.commander = RedCommander
        self.config.initializationTime = 1.0

    def validate_InitializationTimeExpiresEvenIfCommandersAreNotReady(self, gameState, commanders):
        for commander in commanders:
            assert commander.isReadyCallCount == 31

