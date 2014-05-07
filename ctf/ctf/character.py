#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

import re

from inception import overlay
from inception import framework
from inception.math import Vector2, Vector3, ColorValue
from inception.motion import Motion
from inception.rendering import GraphicalRepresentation
from inception.physics import RagdollComponent

from aisbx.actor.navigation import NavigationComponent
from ctf.gameconfig import GameConfig
from ctf import botorders


class ParametersChangedEvent(framework.Event):
    def __init__(self, fieldOfView, shootingDistance, viewDistance):
        super(ParametersChangedEvent, self).__init__()
        self.fieldOfView = fieldOfView
        self.shootingDistance = shootingDistance
        self.viewDistance = viewDistance


class CharacterComponent(framework.State):
    """
    Interface to a character to order him around RTS style
    """
    def __init__(self, actor, name, team, color):
        super(CharacterComponent, self).__init__()

        self.actor = actor
        self.name = name
        self.team = team
        self.color = color
        self.currentAction = None
        self.actionToResume = None
        self.flag = None
        self.firePenalty = 0.0
        self.description = ''
        self.progressToShoot = 0.0
        self.prevTimeToShoot  = 0.0
        self.spawnImmuneTime = 0.0
        self.fieldOfView = GameConfig.MOVING_FOV_ANGLE
        self.shootingDistance = GameConfig.SHOOTING_DISTANCE
        self.viewDistance = GameConfig.VISIBILITY_DISTANCE

        self.setParameters()

    def __repr__(self):
        return 'Character({})'.format(self.name)


    def setParameters(self):
        event = ParametersChangedEvent(self.fieldOfView, \
                                       self.shootingDistance, \
                                       self.viewDistance)

        if isinstance(self.currentAction, botorders.DefendOrder):
            self.fieldOfView = GameConfig.DEFEND_FOV_ANGLE
            self.shootingDistance = GameConfig.SHOOTING_DISTANCE_DEFEND
            self.viewDistance = GameConfig.VISIBILITY_DISTANCE_DEFEND

        elif isinstance(self.currentAction, botorders.MoveOrder) \
          or isinstance(self.currentAction, botorders.ChargeOrder) \
          or isinstance(self.currentAction, botorders.AttackOrder):
            self.fieldOfView = GameConfig.MOVING_FOV_ANGLE
            self.shootingDistance = GameConfig.SHOOTING_DISTANCE
            self.viewDistance = GameConfig.VISIBILITY_DISTANCE

        elif not isinstance(self.currentAction, botorders.TakingOrders) \
         and not isinstance(self.currentAction, botorders.ShootAtCommand):
            self.fieldOfView = GameConfig.IDLE_FOV_ANGLE
            self.shootingDistance = GameConfig.SHOOTING_DISTANCE_IDLE
            self.viewDistance = GameConfig.VISIBILITY_DISTANCE_IDLE

        if event.fieldOfView != self.fieldOfView \
        or event.shootingDistance != self.shootingDistance \
        or event.viewDistance != self.viewDistance:
            event.fieldOfView = self.fieldOfView
            event.shootingDistance = self.shootingDistance
            event.viewDistance = self.viewDistance
            self.send(event)


    def getReloadDelay(self):
        if isinstance(self.currentAction, botorders.DefendOrder):
            return GameConfig.RELOAD_DELAY_DEFEND
        else:
            return GameConfig.RELOAD_DELAY


    def setFirePenalty(self, value, reason):
        self.firePenalty = value
        self.updateProgressToShoot(0.0)


    def onShoot(self, event):
        self.progressToShoot = 0.0


    def updateProgressToShoot(self, dt):
        timeLeft = max(self.firePenalty, self.weapon.nextFireDelay)
        if not self.targetingComponent.target:
            self.progressToShoot = min(self.progressToShoot+dt, min(1.0, 1.0 - min(1.0, timeLeft/GameConfig.MAX_FIRE_DELAY))/2.0)
        elif timeLeft > self.prevTimeToShoot:
            self.progressToShoot = 0.0
        elif timeLeft <= 0:
            self.progressToShoot = 1.0
        else:
            self.progressToShoot = min(1.0, max(0.0, self.progressToShoot+dt/timeLeft))
        self.prevTimeToShoot = timeLeft


    def executeOrderInternal(self, order):
        if self.health.points > 0:
            self.progressToShoot = 0.0
            order.execute(self)
            self.currentAction = order
            self.setParameters()


    def executeOrder(self, order):
        self.previousAction = None
        self.executeOrderInternal(order)


    def checkOrder(self, order):
        return order.check(self)


    def onAcquireTarget(self, target):
        # update the target field of the current action to remember which waypoints are remaining
        remainingWaypoints = self.actor.getComponent(NavigationComponent).getRemainingWaypoints()
        if self.currentAction and len(remainingWaypoints) > 0:
            self.currentAction.target = [Vector2(w.getPosition().x, w.getPosition().z) for w in remainingWaypoints]
        self.actionToResume = self.currentAction
        self.executeOrderInternal(botorders.ShootAtCommand(self.name, target.name))

    def onLoseTarget(self, target):
        if self.currentAction and hasattr(self.currentAction,'onLoseTarget'):
            self.currentAction.onLoseTarget(target)
        self.weapon.clearTarget()


    def reset(self, situation):
        if self.flag:
            self.flag.reset()

        self.health.reset(GameConfig.INITIAL_HEALTH)
        self.body.setColor(self.color)

        self.actionToResume = None
        self.currentAction = None
        self.flag = None
        self.firePenalty = 0.0
        self.progressToShoot = 0.0

        self.navigation.clearWaypoints()
        self.animation.reset()
        self.location.teleport(situation)
        
        self.locomotion.setStyle(Motion.Motion_Idle)
        
        if self.ragdollState:
            self.ragdollState.deactivate()

        self.targeting.target = None
        self.targeting.enabled = False
        self.weapon.clearTarget()
        self.spawnImmuneTime = GameConfig.SPAWN_IMMUNE_TIME

    def die(self):
        # The color of the body becomes black (RGB are zero), and the pedestal becomes invisible (A is zero).
        self.body.setColor(ColorValue(0.0, 0.0, 0.0, 0.0))

        self.health.points = 0
        self.health.alive = False
        self.actor.getComponent(NavigationComponent).clearWaypoints()

        self.locomotionComponent.cancelLockTarget()
        if self.ragdollState:
            self.locomotionComponent.setStyle(Motion.Motion_Ragdoll)
            self.ragdollState.activate(RagdollComponent.MODE_PASSIVE_RAGDOLL)
            self.ragdollState.applyCentralForce(self.health.directionOfLastDamage * -5000 + Vector3(0, 2500, 0))
            self.ragdollState.synchronizationController.reset()
        else:
            self.locomotionComponent.setStyle(Motion.Motion_Dead)

        self.weapon.target = None
        self.targetingComponent.target = None
        self.targetingComponent.enabled = False

    def isInOwnSpawn(self):
        return self.team.inSpawnLocation(self.location.getPosition()) and self.spawnImmuneTime > 0.0



class CharacterController(framework.Controller):

    def __init__(self, state):
        super(CharacterController, self).__init__(state)
        self.state = state


    def tick(self, dt):
        pass


    def update(self, dt):
        self.state.updateProgressToShoot(dt)
        if not self.state.health.isAlive():
            return

        if self.state.health.isAlive() and (self.state.health.points <= 0):
            self.state.die()
            return

        self.state.firePenalty = max(self.state.firePenalty - dt, 0.0)
        self.state.spawnImmuneTime = max(self.state.spawnImmuneTime - dt, 0.0)

        if self.state.currentAction:
            self.state.currentAction.tick(dt)

            if self.state.currentAction.isCompleted():
                if self.state.actionToResume:
                    self.state.currentAction = self.state.actionToResume
                    self.state.actionToResume = None
                    self.state.currentAction.execute(self.state)
                else:
                    self.state.currentAction = None



RE_BOT_NAME = re.compile('([A-Za-z]+)([0-9]+)')


class CharacterRepresentation(GraphicalRepresentation):
    
    def __init__(self, entity):
        super(CharacterRepresentation, self).__init__(entity)
        self.character = entity
        self.location = entity.locationComponent
        self.health = entity.healthComponent
        self.weapon = entity.weapon
        self.text = None


    def setup(self, renderer):
        self.renderer = renderer

        color = self.character.team.teamConfig.color * 0.5
        color.a = 1.0

        self.overlay = renderer.findPlugin(overlay.RocketPlugin).findDynamicOverlay()
        self.element = self.overlay.addElement("bot-label")

        self.modify()


    def modify(self):
        character = self.character
        body = character.bodyComponent

        sc = self.renderer.calculateScreenCoordinates(self.location.getPosition())
        self.overlay.setPosition(self.element, sc + Vector2(0.0, 20.0))

        spans = RE_BOT_NAME.match(self.character.name)
        text = "%s <b>%s</b>" % (spans.group(1), spans.group(2))
        desc = character.description

        if character.currentAction is not None:
            desc = desc.replace("[Order]", "[%s]" % repr(character.currentAction))

        if self.health.points > 0:
            color = character.team.teamConfig.color
            flag = character.flag
            scale = 1.0

            if character.isInOwnSpawn():
                color = ColorValue.Black * 0.75 + color * 0.25
                text += '*'
            elif flag is not None:
                text += ' + flag!<br/>' if desc else '!<br/>+flag '
                color = ColorValue.Black * 0.5 + color * 0.5
                scale = 1.5

            body.setScale(scale)

            col = color * 0.5
            if desc:
                text += ': ' + desc if not flag else desc
        else:
            body.setScale(1.0)
            col = ColorValue.Black

        if self.text != text:
            self.overlay.setText(self.element, text)
            self.text = text

        self.overlay.setProperty(self.element, "color", "rgba(%i,%i,%i,255)" % (col.r*255.0, col.g*255.0, col.b*255.0))


    def tick(self, dt):
        self.modify()


    def teardown(self, renderer):
        self.overlay.removeElement(el)
