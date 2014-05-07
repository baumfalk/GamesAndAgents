#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

from ctf.flagbuilder import FlagFactory
from ctf.team import Team
from ctf.teambase import TeamBase
from ctf.botbuilder import BotFactory
from ctf.events import CombatEvent


class TeamFactory:
    @staticmethod
    def create(teamName, teamConfig, gameState, gameController, world, worldBuilder):
        if teamConfig.botSpawnArea is not None:
            teamBase = TeamBase(teamConfig, teamName, gameState)
            gameState.addState(teamBase)

        team = Team(teamConfig, gameState, eventDispatcher=gameController, mapUtilities=worldBuilder)

        flagName = team.name + "Flag"
        flag = FlagFactory.create(flagName, team, teamConfig.getColor(), teamConfig.flagSpawnLocation, gameState, gameController, world, worldBuilder)
        team.flag = flag
        gameState.addFlag(flag)

        gameState.addTeam(team)
        team.connect(CombatEvent, gameState)

        for i in range(teamConfig.numberBots):
            botName = team.name + str(i)
            bot = BotFactory.createBot(botName, team, teamConfig, worldBuilder, gameState, gameController)
            gameState.addBot(bot)

        return team

    @staticmethod
    def destroyTeam(team, world):
        for bot in team.members:
            world.model.removeState(bot.getParent())
        team.members = set()
        FlagFactory.destroyFlag(team.flag, world)

