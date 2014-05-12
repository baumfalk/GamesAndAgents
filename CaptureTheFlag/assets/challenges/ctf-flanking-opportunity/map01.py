"""A set of example Commanders with simple AI.
"""

from api.orders import *
from api.vector2 import Vector2

from ctf import scriptedcommander


class ChallengeCommander(scriptedcommander.ScriptedCommander):

    def __init__(self, *args, **kwargs):
        orders = [
            (0.0, Move.create('Red1', Vector2(37.0, 17.5))),
            (0.0, Move.create('Red0', Vector2(36.5, 16.5))),
            (0.0, Move.create('Red2', Vector2(35.5, 7.5))),
            (0.0, Move.create('Red3', Vector2(36.0, 6.5))),

            (2.0, Defend.create('Red0', Vector2(-0.6, -1.0))),
            (2.0, Defend.create('Red1', Vector2(-0.5, -1.0))),
            (2.0, Defend.create('Red2', Vector2(-0.30, +1.0))),
            (2.0, Defend.create('Red3', Vector2(-0.40, +1.0))),
        ]

        super(ChallengeCommander, self).__init__(orders, *args, **kwargs)

