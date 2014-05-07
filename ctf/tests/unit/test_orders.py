import random
import unittest

from api.vector2 import Vector2
from api.orders import *

from ctf.network import serialization
from ctf.network import registry


def randomVector2():
    return Vector2(random.random(), random.random())

def isSimilar(a, b):
    if isinstance(a, list) and isinstance(b, list):
        for x,y in zip(a,b): 
            if not isSimilar(x,y):
                return False
        return True
    if isinstance(a, Vector2):
        distance = a.distance(b)
        return distance < 0.01
    else:
        distance = abs(a - b)
        return distance < 0.001
    return False

def compareDefend(defend, copy):
    assert defend.botId  == copy.botId
    if defend.facingDirection:
        # facingDirection is list of direction and time pairs
        for directionAndTime, directionAndTimeCopy in zip(defend.facingDirection, copy.facingDirection):
            assert isSimilar(directionAndTime[0], directionAndTimeCopy[0])
            assert isSimilar(directionAndTime[1], directionAndTimeCopy[1])
    else:
        assert not copy.facingDirection
    assert defend.description == copy.description

def compareMove(move, copy):
    assert move.botId  == copy.botId
    assert isSimilar(move.target, copy.target)
    assert move.description == copy.description

def compareAttack(attack, copy):
    assert attack.botId  == copy.botId
    assert isSimilar(attack.target, copy.target)
    if attack.lookAt:
        assert isSimilar(attack.lookAt, copy.lookAt)
    else:
        assert not copy.lookAt
    assert attack.description == copy.description

def compareCharge(charge, copy):
    assert charge.botId  == copy.botId
    assert isSimilar(charge.target, copy.target)
    assert charge.description == copy.description

def compareOrder(order, copy):
    assert type(order) == type(copy)
    if isinstance(order, Defend):
        compareDefend(order, copy)
    elif isinstance(order, Move):
        compareMove(order, copy)
    elif isinstance(order, Attack):
        compareAttack(order, copy)
    elif isinstance(order, Charge):
        compareCharge(order, copy)
    else:
        assert False, "unknown order type."

class BotOrdersJsonTesting(unittest.TestCase):

    def setUp(self):
        super(BotOrdersJsonTesting, self).setUp()

        self.orders = [Defend.create("bot1", None, "Defend"),
                       Defend.create("bot1", randomVector2(), "Defend"),
                       Defend.create("bot1", [randomVector2(), randomVector2()], "Defend"),
                       Defend.create("bot1", [(randomVector2(), 1), (randomVector2(), 3), randomVector2()], "Defend"),
                       Move  .create("bot2", randomVector2(), "Move"),
                       Move  .create("bot2", [randomVector2(), randomVector2()], "Move"),
                       Attack.create("bot3", randomVector2(), None, "Attack"),
                       Attack.create("bot3", randomVector2(), randomVector2(), "Attack"),
                       Attack.create("bot3", [randomVector2(), randomVector2()], randomVector2(), "Attack"),
                       Charge.create("bot4", randomVector2(), "Charge"),
                       Charge.create("bot4", [randomVector2(), randomVector2()], "Charge")]

    def test_Orders(self):
        for order in self.orders:
            jsonText =  registry.serialize(order)
            copy = registry.deserialize(jsonText)
            compareOrder(order, copy)

if __name__ == '__main__':
    unittest.main(verbosity = 2, failfast = False)
