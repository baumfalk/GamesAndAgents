#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

from ctf.commanderbuilder import CommanderFactory
from ctf.teambuilder import TeamFactory


class LevelBuilder(object):
    @staticmethod
    def build(gameController, gameState, levelConfig, commanderOptions):
        if hasattr(levelConfig, 'getCommanders'):
            for config, commanderName in zip(levelConfig.teams, levelConfig.getCommanders()):
                config.commander = commanderName

        for i, teamConfig in enumerate(levelConfig.teams):
            commander, teamName = CommanderFactory.create(teamConfig, commanderOptions[i])
            team = TeamFactory.create(teamName, teamConfig, gameState, gameController, gameState.world, gameController.worldBuilder)

            if commander:
                gameController.commanders[commander] = team
