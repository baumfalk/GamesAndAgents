from tests.helpers import *


#------------------------------------------------------------------------------
# Helper Class / Functions
#------------------------------------------------------------------------------
class TestOrders(TestSuite):

    def setUp(self):
        """Initialization function run for each of the `test_*` functions below.
        """
        super(TestOrders, self).setUp()

        self.config.red.numberBots = 4
        self.config.red.botSpawnLocations = {
                'Red0': (Vector2(10, 30), Vector2(1.0, 0.0)),
                'Red1': (Vector2(20, 30), Vector2(-1.0, 0.0)),
                'Red2': (Vector2(20, 20), Vector2(0.0, 1.0)),
                'Red3': (Vector2(10, 20), Vector2(0.0, -1.0))
        }
        self.config.gameLength = 4.0
        self.orders = None

    def tearDown(self):
        """Shutdown function run for each of the `test_*` functions below.
        """
        assert self.orders is not None
        self.config.red.commander = Script(self.orders)

        super(TestOrders, self).tearDown()


#--------------------------------------------------------------------------
# Defending Tests
#--------------------------------------------------------------------------
class TestDefend(TestOrders):

    def test_NullFacingDirection(self):
        self.orders = [(0, Defend.create(bot, description = 'defend')) for bot in ['Red0', 'Red1', 'Red2', 'Red3']]

    def validate_NullFacingDirection(self, game, commanders):
        for bot, situation in self.config.red.botSpawnLocations.items():
            assert isSimilar(position(game, bot), situation[0], 0.01)
            assert isSimilar(facingDirection(game, bot), situation[1], 0.01)


    def test_FacingInCurrentLookDirection(self):
        locations = self.config.red.botSpawnLocations
        self.orders = [(0, Defend.create(bot, locations[bot][1], description = 'defend')) for bot in ['Red0', 'Red1', 'Red2', 'Red3']]

    def validate_FacingInCurrentLookDirection(self, game, commanders):
        for bot, situation in self.config.red.botSpawnLocations.items():
            assert isSimilar(position(game, bot), situation[0], 0.01)
            assert isSimilar(facingDirection(game, bot), situation[1], 0.01)


    def setup_SingleFacingDirectionRotationTest(self, i):
        locations = list(self.config.red.botSpawnLocations.values())
        count = self.config.red.numberBots
        self.orders = [(0, Defend.create(bot, locations[(index+i)%count][1], description = 'defend')) for index, bot in enumerate(['Red0', 'Red1', 'Red2', 'Red3'])]

        def validate(game, commanders):
            for bot, order in [(o.botId, o) for _, o in self.orders]:
                situation = self.config.red.botSpawnLocations[bot]
                assert isSimilar(position(game, bot), situation[0], 0.01)
                assert isSimilar(facingDirection(game, bot), order.facingDirection[0][0], 0.01)
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate


    def test_SingleFacingDirectionRotate90(self):
        self.setup_SingleFacingDirectionRotationTest(1)

    def test_SingleFacingDirectionRotate180(self):
        self.setup_SingleFacingDirectionRotationTest(2)

    def test_SingleFacingDirectionRotate270(self):
        self.setup_SingleFacingDirectionRotationTest(3)


    def test_MultipleFacingDirectionsSamePosition(self):
        locations = self.config.red.botSpawnLocations
        self.orders = [(0, Defend.create(bot, [locations[bot][1], -locations[bot][1]], description = 'defend')) for bot in ['Red0', 'Red1', 'Red2', 'Red3']]

        def validate(game, commanders):
            for bot, situation in self.config.red.botSpawnLocations.items():
                assert isSimilar(position(game, bot), situation[0], 0.01)
            validateCommanders(commanders)

        self.config.endOfGameCallback = validate
        self.config.gameLength = 12.0


#--------------------------------------------------------------------------
# Moving Order Tests
#--------------------------------------------------------------------------
class TestMovingOrders(TestOrders):

    def setup_OrderReachesLocation(self, Order, precision):
        locations = list(self.config.red.botSpawnLocations.values())
        count = self.config.red.numberBots
        self.orders = [(0, Order.create(bot, locations[(index+2)%count][0])) for index, bot in enumerate(['Red0', 'Red1', 'Red2', 'Red3'])]
        
        def validate(game, commanders):
            for bot, order in [(o.botId, o) for _, o in self.orders]:
                assert isSimilar(position(game, bot), order.target[0], precision)

        self.config.endOfGameCallback = validate
        

    def test_AttackOrderReachesLocation(self):
        self.setup_OrderReachesLocation(Attack, 0.5)
        self.config.gameLength = 10.0

    def test_MoveOrderReachesLocation(self):
        self.setup_OrderReachesLocation(Move, 0.5)
        self.config.gameLength = 7.0

    def test_ChargeOrderReachesLocation(self):
        self.setup_OrderReachesLocation(Charge, 0.5)
        self.config.gameLength = 7.0


    def setup_OrderUsesMultipleWaypoints(self, Order, precision):
        locations = list(self.config.red.botSpawnLocations.values())
        count = self.config.red.numberBots
        self.orders = [(0, Order.create(bot, [locations[(index+i)%count][0] for i in range(0,2)])) for index, bot in enumerate(['Red0', 'Red1', 'Red2', 'Red3'])]

        def validate(game, commanders):
            for bot, order in [(o.botId, o) for _, o in self.orders]:
                assert isSimilar(position(game, bot), order.target[-1], precision)

        self.config.endOfGameCallback = validate


    def test_AttackOrderUsesMultipleWaypoints(self):
        self.setup_OrderUsesMultipleWaypoints(Attack, 1.0)
        self.config.gameLength = 15.0

    def test_MoveOrderUsesMultipleWaypoints(self):
        self.setup_OrderUsesMultipleWaypoints(Move, 1.0)
        self.config.gameLength = 10.0

    def test_ChargeOrderUsesMultipleWaypoints(self):
        self.setup_OrderUsesMultipleWaypoints(Charge, 1.0)
        self.config.gameLength = 10.0
