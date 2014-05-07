# -*- coding: utf-8 -*-
#==============================================================================
# This file is part of Capture The Flag
# Copyright (c) 2014, AiGameDev.com KG.
#==============================================================================

from __future__ import (absolute_import, division, print_function)

import gevent
import threading

from thrift import transport, protocol, server

from api import commander, orders
from api.vector2 import Vector2

from ctf.gameconfig import GameConfig

from ._thrift import _Commander as _thrift
from ._thrift.ttypes import *

from aisbx import logger
log = logger.getLog(logger.LOG_APP)


class NoConnectionError(Exception):
    pass

class DisconnectError(Exception):
    pass


def T(v):
    if type(v) in [float, int, bool, str, unicode]:
        return v
    if isinstance(v, dict):
        return {a: T(b) for a, b in v.items()}
    if isinstance(v, list):
        return [T(a) for a in v]
    if isinstance(v, tuple):
        return tuple([T(a) for a in v])
    if v.__class__ is TArea2:
        return TArea2(T(v.start), T(v.finish))
    if isinstance(v, Vector2):
        return TVector2(v.x, v.y)
    assert "Unknown object type %s." % type(v)


class Handler(object):

    def __init__(self, commander):
        self.cmdr = commander

    def connect(self, name, language, version):
        print("THRIFT: Commander named `%s' connected from %s version %s." % (name, language, version))
        self.cmdr.name = name
        self.cmdr.isConnected.set()

        self.cmdr.isInitialized.wait()
        print("THRIFT: Initialization of commander finished and data is now available.")

    def disconnect(self):
        print("THRIFT: Commander is done and the client is about to disconnect.")
        self.cmdr.isConnected.set()

    def ready(self):
        print("THRIFT: Commander signals it's ready to proceed into the game!")
        self.cmdr.ready = True

    def step(self):
        return not self.cmdr.done

    def getLevel(self):
        lvl = self.cmdr.level
        return TLevel(
            lvl.width,
            lvl.height,
            lvl.blockHeights,
            lvl.teamNames,
            T({k: [v] for k, v in lvl.flagSpawnLocations.items()}),
            T({k: [TArea2(v,v)] for k, v in lvl.flagScoreLocations.items()}),
            T({k: [TArea2(v[0],v[1])] for k, v in lvl.botSpawnAreas.items()}),
        )

    def getSettings(self):
        lvl = self.cmdr.level
        return TSettings(
            lvl.fieldOfViewAngles,

            lvl.characterRadius,
            lvl.firingDistance,
            lvl.walkingSpeed,
            lvl.runningSpeed,

            gameDuration=lvl.gameLength,
            initializationTime=lvl.initializationTime,
            respawnDelay=lvl.respawnTime
        )

    def getBot(self, name):
        b = self.cmdr.game.bots[name]
        return TBot(
            b.name,
            b.team.name,
            b.flag.name if b.flag else "",
            b.seenlast,
            b.health,
            b.state,
            T(b.position),
            T(b.facingDirection),

            [e.name for e in b.visibleEnemies],
            [e.name for e in b.seenBy],
        )

    def getFlag(self, name):
        f = self.cmdr.game.flags[name]
        return TFlag(
            f.name,
            f.team.name,
            T(f.position),
            f.respawnTimer,
            f.carrier.name if f.carrier else ""
        )

    def getTeam(self, name):
        t = self.cmdr.game.teams[name]
        return TTeam(
            t.name,
            0 if (t is self.cmdr.game.team) else 1,
            [b.name for b in t.members],
            [t.flag.name],
            T([t.flagSpawnLocation]),
            T([TArea2(t.flagScoreLocation, t.flagScoreLocation)]),
            T([TArea2(t.botSpawnArea[0], t.botSpawnArea[1])]),
        )

    def getState(self):
        stt = self.cmdr.game
        return TState(
            self.getMatch(),
            {k: self.getTeam(k) for k in stt.teams},
            {k: self.getBot(k) for k in stt.bots},
            {k: self.getFlag(k) for k in stt.flags},
        )

    def getMatch(self):
        mtch = self.cmdr.game.match
        return TMatch(
            T(mtch.scores),
            mtch.timeRemaining,
            mtch.timeToNextRespawn,
            mtch.timePassed,
        )

    def sendDefendOrder(self, botId, f):
        self.cmdr.orderQueue.append(orders.Defend.create(botId, Vector2(f.x, f.y)))

    def sendAttackOrder(self, botId, positions, l=None):
        if l is not None:
            l = Vector2(l.x, l.y)
        self.cmdr.orderQueue.append(orders.Attack.create(botId, [Vector2(p.x, p.y) for p in positions], l))

    def sendChargeOrder(self, botId, positions):
        self.cmdr.orderQueue.append(orders.Charge.create(botId, [Vector2(p.x, p.y) for p in positions]))

    def sendSprintOrder(self, botId, positions):
        self.cmdr.orderQueue.append(orders.Move.create(botId, [Vector2(p.x, p.y) for p in positions]))


class TSingleServer(server.TServer.TSimpleServer):

  def serve(self):
    self.serverTransport.listen()
    client = self.serverTransport.accept()

    itrans = self.inputTransportFactory.getTransport(client)
    otrans = self.outputTransportFactory.getTransport(client)
    iprot = self.inputProtocolFactory.getProtocol(itrans)
    oprot = self.outputProtocolFactory.getProtocol(otrans)
    try:
        while True:
            self.processor.process(iprot, oprot)
    except TTransport.TTransportException:
        pass
    except Exception:
        import traceback
        traceback.print_exc()

    itrans.close()
    otrans.close()


class Service(threading.Thread):

    def __init__(self, commander, **kwargs):
        super(Service, self).__init__()

        address = '127.0.0.1'
        port = kwargs.get('port', GameConfig.DEFAULT_NETWORK_PORT)
        print("THRIFT: Starting server for address %s and on port %s." % (address, port))

        self.commander = commander
        self.handler = Handler(commander)
        processor = _thrift.Processor(self.handler)
        socket = transport.TSocket.TServerSocket(port=port, host=address)
        tfactory = transport.TTransport.TBufferedTransportFactory()
        pfactory = protocol.TBinaryProtocol.TBinaryProtocolFactory() # TODO: Accelerated
        self.server = TSingleServer(processor, socket, tfactory, pfactory)


    def run(self):
        print("THRIFT: Waiting for a single client, then processing requests...")
        self.server.serve()
        print("THRIFT: Remote commander disconnected, no longer serving requests.")
        self.commander.isConnected.set()


class ThriftCommander(commander.Commander):

    def __init__(self, **kwargs):
        super(ThriftCommander, self).__init__(**kwargs)

        self.name = b'Thrift'
        self.ready = False
        self.done = False
        self.verbose = True

        self.isConnected = threading.Event()
        self.isInitialized = threading.Event()

        self.thread = Service(self, **kwargs) # gevent.get_hub().threadpool.spawn(self._run)
        self.thread.start()

        self.isConnected.wait()
        self.isConnected.clear()


    def initialize(self):
        self.isInitialized.set()


    def getName(self):
        return self.name


    def isReady(self):
        return self.ready


    def tick(self):
        pass


    def gatherOrders(self):
        # self.orderQueue.append(order)
        pass


    def shutdown(self):
        self.done = True
        self.isConnected.wait()
