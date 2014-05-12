"""A set of example Commanders with simple AI.
"""

from api.orders import *
from api.vector2 import Vector2

from ctf import scriptedcommander


class ChallengeCommander(scriptedcommander.ScriptedCommander):

    def __init__(self, *args, **kwargs):
        orders = [
            (0.0, Move.create('Red0', Vector2(26.5, 17.5))),
            (0.0, Move.create('Red1', Vector2(31.5, 25.0))),
            (0.0, Move.create('Red2', Vector2(13.5, 17.5))),
            (0.0, Move.create('Red3', Vector2(16.5, 25.0))),

            (1.5, Defend.create('Red0', Vector2(-1.0, -0.2))),
            (2.0, Defend.create('Red1', Vector2(-0.5, -0.4))),
            (2.0, Defend.create('Red2', Vector2(+1.0, -0.2))),
            (1.5, Defend.create('Red3', Vector2(+0.5, -1.0))),
        ]

        super(ChallengeCommander, self).__init__(orders, *args, **kwargs)

