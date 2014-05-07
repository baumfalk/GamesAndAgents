#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

import socket
import time

from ctf.gameconfig import GameConfig
from ctf.network import messages
from ctf.network import registry

from api.commander import Commander

from aisbx import settings
from aisbx import logger

log = logger.getLog(logger.LOG_APP)


settings.Section('net',
    synchronous = {'default': False, 'type' : bool,
                   'description': "When connecting with commanders over the network, wait synchronously for them in lock-step.",
                   'parseOpt': ['k', settings.PARSEOPTION.NAMED]
                  }
)


class NoConnectionError(Exception):
    pass

class DisconnectError(Exception):
    pass

class NetworkCommander(Commander):

    def __init__(self, **kwargs):
        super(NetworkCommander, self).__init__(**kwargs)

        hostname = '127.0.0.1'
        port = kwargs.get('port', GameConfig.DEFAULT_NETWORK_PORT)

        # open server socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(15.0)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.bind((hostname, port))
            ip, port = s.getsockname()
            log.info("PROXY: Listening on {}:{}".format(ip, port))
            s.listen(1)

            # wait for the client to connect
            self.conn, addr = s.accept()
            log.info("PROXY: Connection from {}:{}".format(addr[0], addr[1]))

        except socket.error as e:
            log.error("PROXY: Could not create connection, {}.".format(e))
            log.exception(e)
            raise NoConnectionError()

        finally:
            s.close()

        self.inputBuffer = ''
        self.lastEventSent = -1
        self.ticked = False
        self.windowStart = 0.01

        try:
            # send the handshaking message
            connectServerMessage = messages.ConnectServerMessage()
            connectServerJson = registry.serialize(connectServerMessage)
            message = connectServerJson + "\n"
            self.conn.settimeout(1.0)
            self.conn.sendall(message)

            # wait for the client to respond with its handshaking message
            connectClientJson = self.readLine(10.0)
            connectClientMessage = registry.deserialize(connectClientJson)
            if not isinstance(connectClientMessage, messages.ConnectClientMessage):
                log.error("PROXY: Received unexpected message during connection handshake with client: {}".format(connectClientMessage))
                raise DisconnectError("Received unexpected message during connection handshake with client: {}".format(connectClientMessage))
            self.name = connectClientMessage.commanderName

        except socket.error as e:
            log.error("PROXY: Error performing connection handshake with client: {}".format(e))
            try:
                self.conn.shutdown(socket.SHUT_WR)
                self.conn.close()
            finally:
                self.conn = None
                raise DisconnectError("Error performing connection handshake with client: {}".format(e))

        self.ready = False
        self.verbose = True


    def initialize(self):
        # we only send new combat events (since our last update)
        # we do this by modifying game.match directly
        allCombatEvents = self.game.match.combatEvents
        self.game.match.combatEvents = []
        self.sendInitializeInfo()
        # restore game.match
        self.game.match.combatEvents = allCombatEvents
        self.lastEventSent = -1


    def getName(self):
        return self.name


    def isReady(self):
        if not self.ready:
            messageJson = self.readLineNonBlocking()
            if messageJson == '':
                return False

            message = registry.deserialize(messageJson)
            if isinstance(message, messages.ReadyMessage):
                self.ready = True
            else:
                log.warning("PROXY: Received unexpected message while waiting for ready message.")
                log.info("PROXY: Orders issued during initialize will be ignored.")
        return self.ready


    def sendInitializeInfo(self):
        try:
            initializeMessage = messages.InitializeMessage(self.level, self.game)
            initializeJson =  registry.serialize(initializeMessage)
            message = initializeJson + "\n"
            self.conn.settimeout(1.0)
            self.conn.sendall(message)
        except socket.error as e:
            log.error("PROXY: Error sending <initialize> information to client {}: {}".format(self.name, e))
            try:
                self.conn.shutdown(socket.SHUT_WR)
                self.conn.close()
            finally:
                self.conn = None
                raise DisconnectError("Error sending <initialize> information to client {}: {}".format(self.name, e))


    def sendTickInfo(self):
        try:
            tickMessage = messages.TickMessage(self.game)
            tickJson =  registry.serialize(tickMessage)
            message = tickJson + "\n"

            # Attempt to send non-blocking tick information three times only, otherwise return.
            for _ in range(3):
                try:
                    self.conn.sendall(message)
                    self.ticked = True
                    break
                except socket.error as e:
                    if e.errno not in [socket.errno.EWOULDBLOCK, socket.errno.EAGAIN]:
                        raise

        except socket.error as e:
            log.error("Error sending <tick> information to client {}: {}".format(self.name, e))
            try:
                self.conn.shutdown(socket.SHUT_WR)
                self.conn.close()
            finally:
                self.conn = None
                raise DisconnectError("Error sending <tick> information to client {}: {}".format(self.name, e))


    def readLineNonBlocking(self):
        try:
            self.conn.settimeout(0.0)
            while True:
                data = self.conn.recv(1500)
                if data == '':
                    raise DisconnectError("Error reading from socket")
                self.inputBuffer += data
        except socket.timeout as e:
            pass
        except socket.error as e:
            if e.errno in [socket.errno.EWOULDBLOCK, socket.errno.EAGAIN]:
                pass # non-blocking recv timeout
            else:
                log.error("PROXY: Error receiving data from client {}: {}".format(self.name, e))
                try:
                    self.conn.shutdown(socket.SHUT_WR)
                    self.conn.close()
                finally:
                    self.conn = None
                    raise DisconnectError("Error receiving data from client {}: {}".format(self.name, e))

        line, sep, self.inputBuffer = self.inputBuffer.partition('\n')
        if sep == '':
            # if there is no newline character, leave all of the contents in the buffer
            # and return an empty string
            self.inputBuffer = line
            line = ''
        return line


    def readLine(self, timeout = 1.0):
        start = time.clock()
        while True:
            line = self.readLineNonBlocking()
            if line != '':
                return line
            stop = time.clock()
            if timeout > 0.0 and stop - start >= timeout:
                raise DisconnectError("Timeout while receiving data from client {}".format(self.name))
            if timeout < 0.0:
                time.sleep(0.005)


    def tick(self):
        # we only send new combat events (since our last update)
        # we do this by modifying game.match directly
        allCombatEvents = self.game.match.combatEvents
        self.game.match.combatEvents = self.game.match.combatEvents[self.lastEventSent + 1:]
        self.sendTickInfo()
        # restore game.match
        self.game.match.combatEvents = allCombatEvents
        self.lastEventSent = len(self.game.match.combatEvents) - 1

        # we allow a window of time for the commanders to reply with their orders for this frame
        self.windowStart = time.clock()


    def gatherOrders(self):
        config = settings.getSection('net')

        # allow 10ms between sending the last info and getting the orders
        while time.clock() - self.windowStart < 0.0:
            time.sleep(0.001)

        try:
            while True:
                if config.synchronous and self.ticked:
                    messageJson = self.readLine(-1.0)
                    self.ticked = False
                else:
                    messageJson = self.readLineNonBlocking()
                    if messageJson == '':
                        break

                message = registry.deserialize(messageJson)
                if isinstance(message, messages.ReadyMessage):
                    # Ignore any ready messages we received.
                    # This may happen if we started before the commander sent a ready message
                    # eg. because they took too long and the game initializationtime reached 0
                    break
                elif isinstance(message, messages.BotOrderMessage):
                    order = message.order
                    if not self.verbose:
                        order.description = None
                    self.orderQueue.append(order)
                elif isinstance(message, messages.TockMessage):
                    pass
                else:
                    log.warning('PROXY: Unknown message received from network commander.')
        except socket.error as e:
            raise DisconnectError("Error receiving order data from client." + str(e))


    def shutdown(self):
        log.debug("PROXY: Shutting down the network commander, notifying client...")
        try:
            shutdownMessage = messages.ShutdownMessage()
            shutdownJson =  registry.serialize(shutdownMessage)
            message = shutdownJson + "\n"
            self.conn.settimeout(1.0)
            self.conn.sendall(message)
            while True:
                messageJson = self.readLine(-1.0)
                message = registry.deserialize(messageJson)
                if isinstance(message, messages.ReadyMessage):
                    log.info("PROXY: Client acknowledged the shutdown message.")
                    break
            self.conn.close()
        except socket.error as e:
            log.error("PROXY: Error performing shutdown handshake with client: {}".format(e))
            try:
                self.conn.shutdown(socket.SHUT_WR)
                self.conn.close()
            finally:
                self.conn = None
                raise DisconnectError("Error performing shutdown handshake with client: {}".format(e))
