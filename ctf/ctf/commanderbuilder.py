#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

from ctf.commandererror import CommanderError
from ctf.network.commander import NoConnectionError


class CommanderFactory:
    @staticmethod
    def create(teamConfig, commanderArgs):
        cmdr = None
        teamName = ""

        if teamConfig.commander:
            try:
                nick = commanderArgs.get('nick', teamConfig.name)
                commanderArgs['nick'] = nick
                cmdr = teamConfig.commander(**commanderArgs)
                teamName = cmdr.name.replace('Commander', '').upper()

            except NoConnectionError:
                raise CommanderError(nick, 'Timed out waiting for network connection from commander.')

        return cmdr, teamName
