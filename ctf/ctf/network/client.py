#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2012-2013, AiGameDev.com KG.
#==============================================================================

import time
import socket

try: # Python 3.x
    import queue
except: # Python 2.x
    import Queue as queue

from threading import Thread

from api import jsonhelpers

from ctf.network import messages
from ctf.network import registry
from ctf.network import serialization

try:
    from aisbx import logger
    logger.configureDefaultLog("CLIENT", level=logger.NOTICE)
    log = logger.getLog("CLIENT")
except ImportError:
    import logging
    log = logging.getLogger("CLIENT")

from aisbx.visualizer.client import Client as VisClient
from aisbx.console import Kernel


class NoConnectionError(Exception):
    pass

class DisconnectError(Exception):
    pass


# returns the next line (\n terminated) from the socket connection, plus any remaining data
# if there is not a complete line available, this function busy waits until one is available
# inputBuffer is the remaining data from the last time we called readLine
# expected usage:   line, inputBuffer = readLine(socket, inputBuffer)
# throws a DisconnectError if there was an error reading from the socket
def readLine(conn, inputBuffer):
    while True:
        data = ''
        try:
            conn.settimeout(0.0)
            while True:
                data = conn.recv(1500)
                if data == '':
                    if inputBuffer == '':
                        raise DisconnectError("Client error reading from socket.")
                    else:
                        break
                inputBuffer += data
        except socket.timeout as e:
            pass
        except socket.error as e:
            if e.errno in [socket.errno.EWOULDBLOCK, socket.errno.EAGAIN]:
                pass  # non-blocking recv timeout
            else:
                raise DisconnectError("Client error reading from socket: {}".format(e))

        line, sep, inputBuffer = inputBuffer.partition('\n')
        if sep == '':
            # if there is no newline character, leave all of the contents in
            # the buffer and return an empty string
            inputBuffer = line
            line = ''

        if line != '':
            return line, inputBuffer
        else:
            time.sleep(0.001)


# This function is designed to be run in a separate thread
# It continually reads from the socket conn and adds complete messages to the messageQueue
# This function terminates after a shutdown message is read
def socketReader(conn, messageQueue, commanderName):
    inputBuffer = ''
    try:
        while True:
            messageJson, inputBuffer = readLine(conn, inputBuffer)
            message = registry.deserialize(messageJson)
            messageQueue.put(message)
    except DisconnectError:
        if log: log.info("CLIENT: Socket was disconnected!")
        messageQueue.put(None)
    except Exception as e:
        if log: log.error("CLIENT: Unknown error while receiving network message in commander {}: {}".format(commanderName, e))
        raise DisconnectError("Unknown error while receiving network message in commander {}: {}".format(commanderName, e))


class NetworkClient(object):

    def __init__(self, networkAddr, commanderCls, commanderNick, enableVisualizer=False, enableInterpreter=False):
        super(NetworkClient, self).__init__()
        commanderArgs = {'nick': commanderNick}
        self.commander = commanderCls(**commanderArgs)

        start = time.clock()
        while True:
            try:
                self.conn = socket.create_connection(networkAddr)
                self.conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                if log: log.info("CLIENT: Connected from {}!".format(self.conn.getsockname()))
                break
            except socket.error:
                time.sleep(0.1) # failed to connect, try again
            if time.clock() - start > 30.0:
                if log: log.error("CLIENT: Error connecting to {}:{}".format(networkAddr[0], networkAddr[1]))
                raise NoConnectionError()

        self.messageQueue = queue.Queue()
        self.socketReaderThread = Thread(target=socketReader, args=(self.conn, self.messageQueue, self.commander.name))
        self.socketReaderThread.name = "SocketReaderThread"
        self.socketReaderThread.daemon = True
        self.socketReaderThread.start()

        if enableVisualizer:
            self.visualizer = VisClient(host='127.0.0.1', port=3232, log=log)
            self.visualizer.start()
        else:
            self.visualizer = None

        if enableInterpreter:
            self.ipkernel = Kernel(self.commander)
            self.ipkernel.start()
        else:
            self.ipkernel = None


    def performHandshaking(self):
        # wait for the server to send its handshaking message
        try:
            if log: log.info("CLIENT: Waiting for ConnectServer message...")
            message = self.messageQueue.get(True, 5)
            assert isinstance(message, messages.ConnectServerMessage), 'Received unexpected message from the server. Expected connect message.'
        except queue.Empty:
            if log: log.error("CLIENT: No ConnectServer message received from the server.")
            raise DisconnectError('No ConnectServer message received from the server.')

        if log: log.info("CLIENT: Received ConnectServer message.")
        connectServerMessage = message
        if not connectServerMessage.validate():
            if log: log.error("CLIENT: Validation failed during hand-shaking.")
            raise DisconnectError('Validation failed during hand-shaking.')

        self.messageQueue.task_done()

        # send the handshaking message
        if log: log.info("CLIENT: Sending ConnectClient message to server.")
        connectClientMessage = messages.ConnectClientMessage(self.commander.name, "python")
        connectClientJson =  registry.serialize(connectClientMessage)
        message = connectClientJson + "\n"
        self.conn.sendall(message)

    def sendReady(self):
        if log: log.info("CLIENT: Sending Ready message to server.")
        readyMessage = messages.ReadyMessage()
        readyJson =  registry.serialize(readyMessage)
        message = readyJson + "\n"
        self.conn.sendall(message)

    def sendOrders(self):
        for order in self.commander.orderQueue:
            orderMessage = messages.BotOrderMessage(order)
            orderJson =  registry.serialize(orderMessage)
            message = orderJson + "\n"
            self.conn.sendall(message)
        else:
            tockMessage = messages.TockMessage()
            tockJson =  registry.serialize(tockMessage)
            self.conn.sendall(tockJson + "\n")
        self.commander.orderQueue = []

    def initializeCommanderGameData(self, levelInfo, gameInfo):
        jsonhelpers.fixupGameInfoReferences(gameInfo)
        self.commander.level = levelInfo
        self.commander.game = gameInfo
        self.commander.visualizer = self.visualizer

    def updateCommanderGameData(self, gameInfo):
        jsonhelpers.mergeGameInfo(self.commander.game, gameInfo)

    def run(self):
        try:
            if log: log.info("CLIENT: Performing hand-shaking.")
            self.performHandshaking()

            initialized = False
            shutdown = False
            tickRequired = False

            if log: log.debug("CLIENT: Entering main loop...")
            while True:
                while True:
                    try:
                        message = self.messageQueue.get_nowait()
                    except queue.Empty:
                        break

                    if message is None:
                        assert shutdown, 'Server disconnected before sending shutdown.'
                        break

                    if isinstance(message, messages.InitializeMessage):
                        assert not initialized, 'Unexpected initialize message {}'.format(message[0])
                        self.initializeCommanderGameData(message.level, message.game)
                        if log: log.debug("CLIENT: Initializing...")
                        self.commander.initialize()
                        self.sendReady()
                        if log: log.debug("CLIENT: Done with initialization.")
                        initialized = True

                    elif isinstance(message, messages.TickMessage):
                        assert initialized, 'Unexpected message {} while waiting for initialize'.format(message[0])
                        self.updateCommanderGameData(message.game)
                        tickRequired = True

                    elif isinstance(message, messages.ShutdownMessage):
                        assert initialized, 'Unexpected message {} while waiting for initialize'.format(message[0])
                        if log: log.debug("CLIENT: Shutting down...")
                        self.commander.shutdown()
                        self.sendReady()
                        shutdown = True
                        if log: log.debug("CLIENT: Done with shutdown.")
                        break

                    else:
                        assert False, 'Unknown message received: "{}"'.format(message)

                    self.messageQueue.task_done()

                if shutdown:
                    break

                if self.ipkernel is not None:
                    self.ipkernel.step(duration=0.02)

                if tickRequired:
                    self.commander.tick()

                    if self.visualizer is not None:
                        self.visualizer.flush()

                    self.sendOrders()
                    tickRequired = False
                else:
                    time.sleep(0.0001)

                # gc.collect()
            if log: log.debug("CLIENT: Exit from main loop!")

        except:
            try:
                self.conn.close()
            except:
                pass
            raise
