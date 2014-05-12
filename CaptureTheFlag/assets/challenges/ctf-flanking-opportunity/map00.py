"""A set of example Commanders with simple AI.
"""

from api.orders import *
from api.vector2 import Vector2

from ctf import scriptedcommander


class ChallengeCommander(scriptedcommander.ScriptedCommander):

    def __init__(self, **kwargs):
        orders = [
            (0.0, Move.create('Red0', Vector2(7.5, 18.5))),
            (0.0, Move.create('Red1', Vector2(8.0, 17.5))),
            (0.0, Move.create('Red2', Vector2(8.0, 8.5))),
            (0.0, Move.create('Red3', Vector2(7.5, 7.5))),

            (2.0, Defend.create('Red0', Vector2(+0.55, -1.0))),
            (2.0, Defend.create('Red1', Vector2(+0.4, -1.0))),
            (2.0, Defend.create('Red2', Vector2(+0.4, +1.0))),
            (2.0, Defend.create('Red3', Vector2(+0.55, +1.0))),
        ]

        super(ChallengeCommander, self).__init__(orders, **kwargs)

