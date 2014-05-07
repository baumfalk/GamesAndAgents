#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

import math

from aisbx import interface, actor
from aisbx.actor.perception import PerceptionComponent as _PerceptionComponent
from aisbx.actor.perception import PerceptionConeRepresentation, PerceptionCanPerceiveFilter
from aisbx.actor.perception import PerceptionConeDevice

from inception import framework
from inception.math import Quaternion, Radian, Vector3, ColorValue
from inception.rendering import GraphicalRepresentation

from ctf.events import CombatEvent
from ctf.character import CharacterComponent, ParametersChangedEvent
from ctf.gameconfig import GameConfig


class CTFCanPerceiveFilter(PerceptionCanPerceiveFilter):

    def shouldDiscard(self, entity):
        healthCmp = entity.healthComponent
        return not healthCmp.isAlive()


class PerceptionComponent(_PerceptionComponent):
    def __init__(self, actor, perceptionSystem):
        super(PerceptionComponent, self).__init__(actor, perceptionSystem)

        self.character = actor.getComponent(CharacterComponent)
        self.character.subscribe(ParametersChangedEvent, self.onCharacterParametersChanged)

        self.primaryPerceptionCone = \
            self.addPerceptionDevice(PerceptionConeDevice('visual', self, 'primary', 0, GameConfig.VISIBILITY_DISTANCE_IDLE, \
                                                            GameConfig.IDLE_FOV_ANGLE, color = self.character.color))
        inverseFoVAngle = (math.pi * 2.0) - GameConfig.IDLE_FOV_ANGLE
        intuitionRange = 1.0
        self.secondaryPerceptionCone = \
            self.addPerceptionDevice(PerceptionConeDevice('visual', self, 'secondary', 0, intuitionRange, \
                                                            inverseFoVAngle, color = self.character.color, \
                                                            offsetOrientation = Quaternion(Radian(math.pi), Vector3.UNIT_Y)))


    def __del__(self):
        self.character.unsubscribe(ParametersChangedEvent, self.onCharacterParametersChanged)
        super(PerceptionComponent, self).__del__()


    def onCharacterParametersChanged(self, event):
        self.primaryPerceptionCone.fieldOfPerception = event.fieldOfView
        self.secondaryPerceptionCone.fieldOfPerception = (math.pi * 2.0) - event.fieldOfView
        self.primaryPerceptionCone.maxDistance = event.viewDistance


@interface.implementer(actor.interface.perception.PerceptionDeviceInterface)
class PerceptionFromCombatEventDevice(object):

    def __init__(self, type, perceptionCmp, identifier, gameState):
        super(PerceptionFromCombatEventDevice, self).__init__()

        self.type = type
        self.component = perceptionCmp
        self.identifier = identifier
        self.gameState = gameState
        self.recentEvents = []
        self.perceivableEntities = []

        self.gameState.subscribe(CombatEvent, self.onCombatEvent)


    def __del__(self):
        self.gameState.unsubscribe(CombatEvent, self.onCombatEvent)
        super(PerceptionFromCombatEventDevice, self).__del__()


    def update(self):
        """ Called per tick to give the source a chance to update.
        """
        self.perceivableEntities = []

        character = self.component.character
        # filter out old events
        self.recentEvents = [e for e in self.recentEvents if self.gameState.timePassed <= e.time + GameConfig.PERCEPTION_IGNORE_EVENTS_AFTER]

        detectableEntities = self.component.sensoryComponent.detectableEntities

        # add instigators of events to our perceivableBots set
        for e in self.recentEvents:

            # model a reaction time. this is a delay before we notice events
            if self.gameState.timePassed < e.time + GameConfig.PERCEPTION_EVENT_REACTION_TIME:
                continue

            # for events which have an instigator, add the instigator to the perceivableBots if we have line of sight
            if e.instigator:
                instigatorIsNotTeamMember = e.instigator not in character.team.members
                instigatorIsAlive = e.instigator.health.points > 0
                instigatorIsDetectable = True#e.instigator.actor in detectableEntities
                if (instigatorIsNotTeamMember) and (instigatorIsAlive) and (instigatorIsDetectable):
                    self.perceivableEntities.append(e.instigator.actor)


    def contains(self, entity):
        """ Lookup if a certain entity was perceived (should only be valid after update())

        Arguments:
            entity:           Nonspecific game entity

        Returns:
            Boolean on whether the given entity can be perceived or not
        """
        return entity in self.perceivableEntities


    def getPerceived(self):
        """ Called per Tick to retrieve entites perceived by this device

        Returns:
            A list of entities which are perceived by this device
        """
        return self.perceivableEntities


    def onCombatEvent(self, event):
        self.recentEvents.append(event)



class CTFPerceptionConeRepresentation(PerceptionConeRepresentation):
    def __init__(self, perceptionComponent):
        super(CTFPerceptionConeRepresentation, self).__init__(perceptionComponent)
        color = self.component.character.color
        self.raycolor = ColorValue(color.r, color.g, color.b, 0.1)
        g = (color.r + color.g + color.b) / 3.0
        self.raygray = ColorValue(g, g, g, 0.034)
        self.visibilityRayShapes = {}

    def setup(self, renderer):
        super(CTFPerceptionConeRepresentation, self).setup(renderer)

    def updateVisibilityRays(self, position):
        perceptor = self.component

        perceivableBots = [a.character for a in perceptor.getPerceivable()]
        visibleBots = [a.character for a in perceptor.perceivableEntities.get('visual', set())]

        # Hide unseen arrrows.
        for enemy, ray in self.visibilityRayShapes.items():
            if enemy not in perceivableBots: #this referred to (visibleBots | perceivableBots) before... not quite sure if this is the right replacement
                ray.color = ColorValue(0.0, 0.0, 0.0, 0.0)
                self.visualizer.update(ray)

        # Show arrows for guys, create new ones if we don't have them.
        for enemy in visibleBots:
            self.updateVisibilityRay(enemy, position, 0.1, self.raycolor)

        for enemy in perceivableBots:
            self.updateVisibilityRay(enemy, position, 0.2, self.raycolor * 0.5)


    def updateVisibilityRay(self, bot, position, thickness, color):
        up = Vector3(0.0, 0.1, 0.0)

        if bot not in self.visibilityRayShapes:
            rayShape = self.visualizer.createLineShape()
            rayShape.source = position + up
            rayShape.target = bot.location.getPosition() + up
            rayShape.thickness = thickness
            rayShape.color = color

            self.visibilityRayShapes[bot] = rayShape
        else:
            shape = self.visibilityRayShapes[bot]
            shape.source = position + up
            shape.target = bot.location.getPosition() + up
            shape.thickness = thickness
            shape.color = color
            self.visualizer.update(shape)


    def modify(self):
        super(CTFPerceptionConeRepresentation, self).modify()

        if self.component.health.points <= 0.0:
            for cone, coneShape in self.coneArcShapes.items():
                coneShape.color = ColorValue(0.0, 0.0, 0.0, 0.0)

        # Disabling visibility rays for CTF as they're very noisy visually and not
        # worth the cost.  Could be enabled when there's a mouse over event.
        # self.updateVisibilityRays(self.location.getPosition())


    def tick(self, dt):
        self.modify()


    def teardown(self, renderer):
        super(CTFPerceptionConeRepresentation, self).teardown(renderer)
        for shape in self.visibilityRayShapes.values():
            self.visualizer.remove(shape)
