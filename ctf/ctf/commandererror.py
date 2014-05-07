#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

class CommanderError(Exception):
    def __init__(self, commanderName, message):
        super(CommanderError, self).__init__()
        self.commanderName = commanderName
        self.message = message

    def __str__(self):
        return 'CommanderError for commander {}. {}'.format(self.commanderName, self.message)

