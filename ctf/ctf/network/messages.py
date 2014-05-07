#==============================================================================
# This file is part of The AI Sandbox.
# Copyright (c) 2007-2013, AiGameDev.com
#==============================================================================

"""
Network messages sent between the client and the server.
"""

from __future__ import print_function

from __future__ import print_function


class ConnectServerMessage(object):
    ExpectedProtocolVersion = "1.4"

    def __init__(self, protocolVersion = ExpectedProtocolVersion):
        super(ConnectServerMessage, self).__init__()
        self.protocolVersion = protocolVersion

    def validate(self):
        if self.protocolVersion != self.ExpectedProtocolVersion:
            print("This client version does not match network protocol version. Expected version {} received {}.".format(self.ExpectedProtocolVersion, self.protocolVersion), file=sys.stderr)
            return False
        return True

    def __str__(self):
        return "ConnectServer"

    def __eq__(self, other):
        return self.protocolVersion == other.protocolVersion


class ConnectClientMessage(object):
    def __init__(self, commanderName = None, language = None):
        super(ConnectClientMessage, self).__init__()
        self.commanderName = commanderName
        self.language = language

    def __str__(self):
        return "ConnectClient commanderName = {}, language = {}".format(self.commanderName, self.language)

    def __eq__(self, other):
        return (self.commanderName == other.commanderName) and (self.language == other.language)


class ReadyMessage(object):
    def __init__(self):
        super(ReadyMessage, self).__init__()

    def __str__(self):
        return "Ready"

    def __eq__(self, other):
        return type(self) == type(other)


class InitializeMessage(object):
    def __init__(self, level = None, game = None):
        super(InitializeMessage, self).__init__()
        self.level = level
        self.game = game

    def __str__(self):
        return "Initialize"

    def __eq__(self, other):
        # TODO: Complete this comparison
        return type(self) == type(other)


class ShutdownMessage(object):
    def __init__(self):
        super(ShutdownMessage, self).__init__()

    def __str__(self):
        return "Shutdown"

    def __eq__(self, other):
        return type(self) == type(other)


class TickMessage(object):
    def __init__(self, game = None):
        super(TickMessage, self).__init__()
        self.game = game

    def __str__(self):
        return "Tick"

    def __eq__(self, other):
        # TODO: Complete this comparison
        return type(self) == type(other)


class TockMessage(object):
    def __init__(self, game = None):
        super(TockMessage, self).__init__()

    def __str__(self):
        return "Tock"

    def __eq__(self, other):
        return type(self) == type(other)


class BotOrderMessage(object):
    def __init__(self, order = None):
        super(BotOrderMessage, self).__init__()
        self.order = order

    def __str__(self):
        return "BotOrder"

    def __eq__(self, other):
        # TODO: Complete this comparison
        return type(self) == type(other)


