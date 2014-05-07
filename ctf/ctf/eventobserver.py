#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

"""Monitor each event that happened in the game.

You should not use this class directly, but rather derive from it. In 
your child class create a method called "on<EventClassName>(self, event)"
which will be called if such an event is generated.
"""

from aisbx import framework


##-------------------------------------------------
class GameEventObserver(object):
    
    def onEvent(self, event):
        try:
            getattr(self, "on%s" % event.__class__.__name__)(event)
        except:
            pass  ## event handler function not found, which is not bad in our case here
        
        
##-------------------------------------------------
class EmptySampleObserver(GameEventObserver):
    def onFlagPickedUpEvent(self, event):
        pass

    def onFlagDroppedEvent(self, event):
        pass

    def onFlagCapturedEvent(self, event):
        pass

    def onFlagRestoredEvent(self, event):
        pass

    def onScoreChangedEvent(self, event):
        pass

    def onBotRespawnEvent(self, event):
        pass

    def onBotOrderEvent(self, event):
        pass

    def onCombatEvent(self, event):
        pass



