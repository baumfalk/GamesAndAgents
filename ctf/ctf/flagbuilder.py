#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

from inception.math import Vector3, ColorValue
from inception.rendering import MeshComponent
from inception.simulation import Zone

from ctf.flag import FlagState, FlagController
from ctf.events import FlagEvent

class FlagFactory:
    @staticmethod
    def create(flagName, team, color, initialFlagPos, gameState, gameController, world, worldBuilder):
        pos = Vector3(initialFlagPos.x, 0.0, initialFlagPos.y)

        flag = worldBuilder.createProp(pos, "flag.mesh")
        mesh = flag.getComponent(MeshComponent)
        mesh.setMaterialName("CustomColor")
        mesh.setColor(color)

        zone = Zone(pos, Vector3(2.0, 0.0, 2.0), "Plane/SquareZone")
        zone.color = color
        gameState.addState(zone)

        pos = team.teamConfig.flagScoreLocation
        if initialFlagPos != team.teamConfig.flagScoreLocation:
            zone = Zone(Vector3(pos.x, 0.0, pos.y), Vector3(3.0, 0.0, 3.0), "Plane/SquareZone")
            zone.color = color * 0.25 + ColorValue(0.25, 0.25, 0.25, 1.0) * 0.75
            gameState.addState(zone)

        flagState = FlagState(flagName, team)
        flagState.resetPosition = initialFlagPos
        flag.addState(flagState)

        flagController = FlagController(flagState, gameState, gameController.triggerSystem)
        gameController.addController(flagController)
        flagState.connect(FlagEvent, gameState)

        return flagState

    @staticmethod
    def destroyFlag(flag, world):
        world.model.removeState(flag.getParent())
