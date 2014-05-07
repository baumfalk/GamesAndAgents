#==============================================================================
# This file is part of The AI Sandbox.
# Copyright (c) 2007-2013, AiGameDev.com
#==============================================================================

"""The classes in this module represent all of the bot orders a bot commander can send to the sandbox server.
"""

from api.vector2 import Vector2


class Defend(object):
    """Order a bot to defend its current position.
    """

    def __init__(self):
        super(Defend, self).__init__()
        self.botId = None
        self.facingDirection = None
        self.description = None

    @classmethod
    def create(cls, botId, facingDirection = None, description = ''):
        assert isinstance(botId, str)
        assert (facingDirection == None) or isinstance(facingDirection, Vector2) or (isinstance(facingDirection, list) and len(facingDirection) > 0)

        order = cls()

        order.botId = botId             #: The name of the bot

        if facingDirection:
            # convert the facingDirection into a list of (Vector2, time) pairs
            if isinstance(facingDirection, Vector2):
                facingDirection = [(facingDirection, 0.0)]
            else:
                # if it is already a list check the type
                for i, f in enumerate(facingDirection):
                    if isinstance(f, Vector2):
                        facingDirection[i] = (f, 0)
                    else:
                        # check the type is a type of Vector2, float?
                        pass

        order.facingDirection = facingDirection
        """The desired facing direction(s) of the bot.
        This parameter can be given in three forms:
        If facingDirection is None then the bot will remain facing in its current facing direction.
        If facingDirection is a Vector2 then the bot will turn to face the requested facing direction.
        If facingDirection is a list of (Vector2, float) pairs then the list is a series of directions in which the bot
        will look. For each element of the list the bot will face in that direction for the amount of time specified by
        the second element of the pair (with a minimum time of 1 second). Once the bot has been through all of the elements
        of the list it will continue iterating again from the beginning of the list.
        """
        order.description = description #: A description of the intention of the bot. This is displayed automatically if the commander sets self.verbose = True

        return order

    def __str__(self):
        return "Defend {} facingDirection={} {}".format(self.botId, self.facingDirection, self.description)


class Move(object):
    """Order a bot to run to a specified position without attacking visible enemies.
    """

    def __init__(self):
        super(Move, self).__init__()
        self.botId = None
        self.target = None
        self.description = None

    @classmethod
    def create(cls, botId, target, description = ''):
        if isinstance(target, Vector2):
            target = [target]
        assert isinstance(botId, str)
        assert isinstance(target, list) and len(target) > 0
        for t in target:
            assert isinstance(t, Vector2)

        order = cls()

        order.botId = botId             #: The name of the bot
        order.target = target           #: The target destination (Vector2) or list of destination waypoints ([Vector2])
        order.description = description #: A description of the intention of the bot. This is displayed automatically if the commander sets self.verbose = True

        return order

    def __str__(self):
        return "Move {} target={} {}".format(self.botId, self.target, self.description)


class Attack(object):
    """Order a bot to attack a specified position. If an enemy bot is seen by this bot, it will be attacked.
    """

    def __init__(self):
        super(Attack, self).__init__()
        self.botId = None
        self.target = None
        self.lookAt = None
        self.description = None

    @classmethod
    def create(cls, botId, target, lookAt = None, description = ''):
        if isinstance(target, Vector2):
            target = [target]
        assert isinstance(botId, str)
        assert isinstance(target, list) and len(target) > 0
        for t in target:
            assert isinstance(t, Vector2)
        assert lookAt == None or isinstance(lookAt, Vector2)

        order = cls()

        order.botId = botId             #: The name of the bot
        order.target = target           #: The target destination (Vector2) or list of destination waypoints ([Vector2])
        order.lookAt = lookAt           #: An optional position (Vector2) which the bot should look at while moving
        order.description = description #: A description of the intention of the bot. This is displayed automatically if the commander sets self.verbose = True

        return order

    def __str__(self):
        return "Attack {} target={} lookAt={} {}".format(self.botId, self.target, self.lookAt, self.description)


class Charge(object):
    """Order a bot to attack a specified position at a running pace. 
    This is faster than Attack but incurs an additional firing delay penalty.
    """

    def __init__(self):
        super(Charge, self).__init__()
        self.botId = None
        self.target = None
        self.description = None

    @classmethod
    def create(cls, botId, target, description = ''):
        if isinstance(target, Vector2):
            target = [target]
        assert isinstance(botId, str)
        assert isinstance(target, list) and len(target) > 0
        for t in target:
            assert isinstance(t, Vector2)

        order = cls()

        order.botId = botId             #: The name of the bot
        order.target = target           #: The target destination (Vector2) or list of destination waypoints ([Vector2])
        order.description = description #: A description of the intention of the bot. This is displayed automatically if the commander sets self.verbose = True

        return order

    def __str__(self):
        return "Charge {} target={} {}".format(self.botId, self.target, self.description)


