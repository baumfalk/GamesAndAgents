#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

from aisbx.actor.sensory import SensorySkipPairingFilter, SensoryCanSenseFilter
from ctf.team import Team


class CTFCanSenseFilter(SensoryCanSenseFilter):

    def shouldDiscard(self, entity):
        healthCmp = entity.healthComponent
        return not healthCmp.isAlive()


class CTFSkipSameTeamFilter(SensorySkipPairingFilter):

    def shouldDiscard(self, entity, otherEntity):
        team = entity.characterComponent.team
        otherTeam = otherEntity.characterComponent.team
        return (team is otherTeam)


class CTFSkipDeadFilter(SensorySkipPairingFilter):

    def shouldDiscard(self, entity, otherEntity):
        return not otherEntity.health.isAlive()

