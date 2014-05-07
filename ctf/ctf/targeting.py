#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

from inception import framework

from ctf.commands import ChangeTargetCommand
from ctf.gameconfig import GameConfig


class TargetingComponent(framework.State):
    """Component storing which enemy a bot is targeting."""

    def __init__(self):
        super(TargetingComponent, self).__init__()
        self.target = None
        self.enabled = False

    def setTarget(self, target):
        """Update the currently targeted enemy bot."""
        if target == self.target:
            return

        ch = self.character
        if self.target:
            ch.onLoseTarget(self.target)
        self.target = target
        if target:
            ch.onAcquireTarget(self.target)


class TargetingController(framework.Controller):

    def __init__(self, targeting):
        super(TargetingController, self).__init__(targeting)
        self.targeting = targeting
        self.subscribe(ChangeTargetCommand, self.cmdTargetChanged)


    def tick(self, dt):
        healthComponent = self.targeting.healthComponent
        if healthComponent.points <= 0 or not self.targeting.enabled:
            self.targeting.target = None
            return

        # enemy bots have to be both perceivable (either in fov or instigator of recent event) and visible (line of sight, but not necessarily in fov)
        detectableBots = { entity.characterComponent for entity in self.targeting.sensoryComponent.detectableEntities }
        perceivableBots = { entity.characterComponent for entity in self.targeting.perceptionComponent.getPerceivable() }

        targetable =  detectableBots & perceivableBots

        # filter out dead bots
        targetable = {b for b in targetable if b.health.points > 0}
        # filter out invulnerable characters
        targetable = {b for b in targetable if not b.isInOwnSpawn()}

        position = self.targeting.location.getPosition()
        previousTarget = self.targeting.target

        # Don't change targets if the target has not died but is still visible.
        if previousTarget and (previousTarget in targetable):
            # Make sure we can really shoot him (lose line of sight)
            dist = position.distance(previousTarget.location.getPosition())
            if dist < self.targeting.characterComponent.shootingDistance + GameConfig.SHOOTING_TARGETTING_BONUS:
                return

        # find the closest enemy
        closestDist = float("inf")
        target = None
        for enemy in targetable:
            dist = position.distance(enemy.location.getPosition())
            if dist < closestDist and dist < self.targeting.characterComponent.shootingDistance:
                target = enemy
                closestDist = dist

        if target != previousTarget:
            self.send(ChangeTargetCommand(self.targeting.character, target))

    def cmdTargetChanged(self, event):
        event.bot.targeting.setTarget(event.target)

