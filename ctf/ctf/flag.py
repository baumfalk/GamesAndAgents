#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

from inception import framework
from inception.math import Vector3, Quaternion

from ctf.events import FlagEvent, FlagPickedUpEvent, FlagDroppedEvent, FlagCapturedEvent, FlagRestoredEvent, CombatEvent
from aisbx.actor.trigger import TriggerComponent, InTriggerEvent


class FlagState(framework.State):

    def __init__(self, name, team):
        super(FlagState, self).__init__()
        self.name = name
        self.team = team
        self.holder = None
        self.resetPosition = Vector3(0.0, 0.0, 0.0)
        self.flagResetDelay = 30.0
        self.flagResetCountdown = 0.0
        self.pickupDist = 2.0
        self.captureDist = 2.0

    def reset(self):
        self.setHolder(None)
        self.flagResetCountdown = -1.0
        self.location.setPosition(Vector3(self.resetPosition.x, 0.0, self.resetPosition.y))
        self.location.setOrientation(Quaternion.IDENTITY)

    def setHolder(self, character):
        if self.holder:
            self.holder.flag = None
        self.holder = character
        if character:
            self.holder.flag = self


class FlagController(framework.Controller):

    def __init__(self, component, gameState, triggerSystem):
        super(FlagController, self).__init__(component)

        self.flag = component
        self.location = component.location
        self.gameState = gameState

        pickupTrigger = TriggerComponent(triggerSystem, radius=self.flag.pickupDist)
        self.flag.getParent().addState(pickupTrigger)
        pickupTrigger.subscribe(InTriggerEvent, self.onPickupTriggerEvent)

        self.gameState.subscribe(CombatEvent, self.onCombatEvent)

        self.subscribe(FlagPickedUpEvent, self.cmdFlagPickUp)
        self.subscribe(FlagDroppedEvent, self.cmdFlagDrop)
        self.subscribe(FlagRestoredEvent, self.cmdFlagRestore)
        self.subscribe(FlagCapturedEvent, self.cmdFlagCapture)

        self.connect(FlagEvent, self.flag)


    def tick(self, dt):
        self.tick_droptimer(dt)
        self.tick_capture(dt)

    def tick_droptimer(self, dt):
        if self.flag.holder != None or self.flag.flagResetCountdown < 0.0:
            return
        self.flag.flagResetCountdown -= dt

        if self.flag.flagResetCountdown <= 0.0:
            self.send(FlagRestoredEvent(self.flag))

    def tick_capture(self, dt):
        if not self.flag.holder:
            return

        holder = self.flag.holder
        assert holder.team != self.flag.team
        hTeam = holder.team

        flagScoreLocation = Vector3(hTeam.teamConfig.flagScoreLocation.x, 0, hTeam.teamConfig.flagScoreLocation.y)
        dist = self.location.getPosition().distance(flagScoreLocation)
        if dist < self.flag.captureDist:
            self.send(FlagCapturedEvent(self.flag, self.flag.holder))

    def update(self, dt):
        if self.flag.holder:
            holder = self.flag.holder.location
            loc = self.flag.location
            loc.setPosition(holder.getPosition() + Vector3.UNIT_Y)
            loc.setOrientation(holder.getOrientation())

    def onCombatEvent(self, event):
        if self.flag.holder:
            if event.type == CombatEvent.TYPE_KILLED:
                killed = event.subject
                if killed == self.flag.holder:
                    self.send(FlagDroppedEvent(self.flag, self.flag.holder))

    def onPickupTriggerEvent(self, event):
        if self.flag.holder:
            return

        character = event.actor.character

        if character in self.flag.team.members:
            return

        if character.health.points <= 0:
            return

        self.send(FlagPickedUpEvent(self.flag, character))

    def cmdFlagCapture(self, event):
        event.flag.reset()

    def cmdFlagDrop(self, event):
        event.flag.flagResetCountdown = event.flag.flagResetDelay
        event.flag.setHolder(None)

    def cmdFlagRestore(self, event):
        event.flag.reset()

    def cmdFlagPickUp(self, event):
        assert event.bot.team != event.flag.team
        event.flag.setHolder(event.bot)
