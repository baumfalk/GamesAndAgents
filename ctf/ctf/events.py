#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

from inception import framework


class ScoreChangedEvent(framework.Event):
    def __init__(self, scores):
        super(ScoreChangedEvent, self).__init__()
        self.scores = scores

class BotRespawnEvent(framework.Event):
    def __init__(self, bot, situation):
        super(BotRespawnEvent, self).__init__()
        self.bot = bot
        self.situation = situation

class FlagEvent(framework.Event):
    def __init__(self, flag, bot):
        super(FlagEvent, self).__init__()
        self.flag = flag
        self.bot = bot 

class FlagPickedUpEvent(FlagEvent):
    def __init__(self, flag, bot):
        super(FlagPickedUpEvent, self).__init__(flag, bot)

class FlagDroppedEvent(FlagEvent):
    def __init__(self, flag, bot):
        super(FlagDroppedEvent, self).__init__(flag, bot)

class FlagCapturedEvent(FlagEvent):
    def __init__(self, flag, bot):
        super(FlagCapturedEvent, self).__init__(flag, bot)

class FlagRestoredEvent(FlagEvent):
    def __init__(self, flag):
        super(FlagRestoredEvent, self).__init__(flag, None)

class BotOrderEvent(framework.Event):
    def __init__(self, bot, order):
        super(BotOrderEvent, self).__init__()
        self.bot = bot
        self.order = order


class CombatEvent(framework.Event):
    
    # DON'T REORDER THESE... YOU'LL KILL ANYONE USING THE JSON SDKS
    # they'll haunt your family for generations, randomly adding one to various constants in your code
    TYPE_NONE = 0
    TYPE_KILLED = 1    
    TYPE_FLAG_PICKEDUP = 2
    TYPE_FLAG_DROPPED = 3
    TYPE_FLAG_CAPTURED = 4
    TYPE_FLAG_RESTORED = 5
    TYPE_RESPAWN = 6
    
    TYPE_NAMES = ["TYPE_NONE", "TYPE_KILLED", "TYPE_FLAG_PICKEDUP", "TYPE_FLAG_DROPPED", 
                  "TYPE_FLAG_CAPTURED", "TYPE_FLAG_RESTORED", "TYPE_RESPAWN"]

    def __init__(self, type, subject, instigator, time):
        super(CombatEvent, self).__init__()
        self.type = type
        self.subject = subject
        self.instigator = instigator
        self.time = time
        
    def __repr__(self):
        if self.instigator:
            return "<game.CombatEvent %s on %s by %s @ %4.2f>" % (CombatEvent.TYPE_NAMES[self.type], self.subject.name, self.instigator.name, self.time)
        elif self.subject:
            cp = self.subject
            if cp:
                name = cp.name
            else:
                name = repr(self.subject) 
            return "<game.CombatEvent %s on %s @ %4.2f>" % (CombatEvent.TYPE_NAMES[self.type], name, self.time)
        else:
            return "<game.CombatEvent %s @ %4.2f>" % (CombatEvent.TYPE_NAMES[self.type], self.time)
