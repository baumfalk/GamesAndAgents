#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

from inception import framework
from inception.math import Vector3
from ctf.gameconfig import GameConfig


class HealthComponent(framework.State):
    def __init__(self):
        super(HealthComponent, self).__init__()
        self.points     = 0.0
        self.health     = None
        self.alive      = False
        self.regenDelay = GameConfig.HEALTH_REGEN_DELAY
        self.regenRate  = GameConfig.HEALTH_REGEN_RATE

        self.regenCountDown = self.regenDelay 
        self.maxHealth  = GameConfig.INITIAL_HEALTH

        self.directionOfLastDamage = Vector3.ZERO

    def reset(self, initialHealth):
        self.points     = initialHealth
        self.alive      = True
        self.directionOfLastDamage = Vector3.ZERO

    def applyDamage(self, amount, locationOfDamageSource):
        self.points = max(self.points - amount, 0)
        self.directionOfLastDamage = (locationOfDamageSource - self.location.getPosition())
        if not self.directionOfLastDamage.isZeroLength():
            self.directionOfLastDamage = self.directionOfLastDamage.normalized()
        self.regenCountDown = self.regenDelay

    def isAlive(self):
        return self.alive


class HealthController(framework.Controller):
    def __init__(self, state):
        super(HealthController, self).__init__(state)
        self.state = state

    def tick(self, dt):
        pass

        # self.tick_regen(dt)

    def tick_regen(self, dt):
        if self.state.points <= 0:
            return

        if self.state.points < self.state.maxHealth and self.state.regenDelay >= 0:
            if self.state.regenCountDown <= 0:
                self.state.points += self.state.regenRate * dt
                if self.state.points > self.state.maxHealth:
                    self.state.points = self.state.maxHealth 
            else:
                self.state.regenCountDown -= dt

