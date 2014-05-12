"""A set of example Commanders with simple AI.
"""

from api.orders import *
from api.vector2 import Vector2

from ctf import scriptedcommander


class ChallengeCommander(scriptedcommander.ScriptedCommander):

    def __init__(self, *args, **kwargs):
        orders = [
            (0.0, Move.create('Red0', Vector2(26.5, 2.5))),
            (0.0, Move.create('Red1', Vector2(18.5, 2.0))),
            (0.0, Move.create('Red2', Vector2(19.5, 6.5))),
            (0.0, Move.create('Red3', Vector2(22.5, 7.5))),

            (1.5, Defend.create('Red0', Vector2(-0.6, +1.0))),
            (1.5, Defend.create('Red1', Vector2(+0.6, +0.6))),
            (1.0, Defend.create('Red2', Vector2(+1.0, +0.3))),
            (1.0, Defend.create('Red3', Vector2(+1.0, +0.5))),
        ]

        super(ChallengeCommander, self).__init__(orders, *args, **kwargs)

