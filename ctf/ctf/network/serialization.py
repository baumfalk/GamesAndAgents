import types

try:
    from inception import Vector3, Quaternion, Situation
except ImportError:
    Vector3, Quaternion, Situation = None, None, None

from ctf.network import registry
from ctf.network.messages import ConnectClientMessage, ConnectServerMessage, ReadyMessage, InitializeMessage, ShutdownMessage, TickMessage, TockMessage, BotOrderMessage

from api.orders import Attack, Charge, Defend, Move
from api.vector2 import Vector2
from api.gameinfo import BotInfo, FlagInfo, GameInfo, LevelInfo, MatchCombatEvent, MatchInfo, TeamInfo
from api import jsonhelpers


def encodeVector3(v):
    return [v.x, v.y, v.z]

def decodeVector3(cls, v):
    assert type(v) is types.ListType
    assert len(v) == 3
    return Vector3(v[0], v[1], v[2])


def encodeQuaternion(v):
    return [q.x, q.y, q.z, q.w]

def decodeQuaternion(cls, q):
    assert type(q) is types.ListType
    assert len(q) == 4
    return Quaternion(list[3], list[0], list[1], list[2])


def encodeSituation(s):
    return (encodeVector3(python_object.position), encodeQuaternion(python_object.orientation))

def decodeSituation(cls, s):
    return Situation(decodeVector3(list[0]), decodeQuaternion(list[1]))


def encodeOrder(order):
    d = order.__dict__.copy()
    if order.botId is None:
        del d['botId']
    return d


def initialize():
    registry.register('Vector2', Vector2, jsonhelpers.encodeVector2, jsonhelpers.decodeVector2)
    if Vector3:
        registry.register('Vector3', Vector3, encodeVector3, decodeVector3)
    if Quaternion:
        registry.register('Quaternion', Quaternion, encodeQuaternion, decodeQuaternion)
    if Situation:
        registry.register('Situation', Situation, encodeSituation, decodeSituation)
    registry.register('Level', LevelInfo)
    registry.register('Game', GameInfo, jsonhelpers.encodeGameInfo, jsonhelpers.decodeGameInfo)
    registry.register('Team', TeamInfo, jsonhelpers.encodeTeamInfo, jsonhelpers.decodeTeamInfo)
    registry.register('Flag', FlagInfo, jsonhelpers.encodeFlagInfo, jsonhelpers.decodeFlagInfo)
    registry.register('Bot', BotInfo, jsonhelpers.encodeBotInfo, jsonhelpers.decodeBotInfo)
    registry.register('Match', MatchInfo)
    registry.register('CombatEvent', MatchCombatEvent, jsonhelpers.encodeMatchCombatEvent, jsonhelpers.decodeMatchCombatEvent)
    registry.register('Defend', Defend, encodeOrder)
    registry.register('Move', Move, encodeOrder)
    registry.register('Attack', Attack, encodeOrder)
    registry.register('Charge', Charge, encodeOrder)
    registry.register('ConnectClient', ConnectClientMessage)
    registry.register('ConnectServer', ConnectServerMessage)
    registry.register('Ready', ReadyMessage)
    registry.register('Initialize', InitializeMessage)
    registry.register('Shutdown', ShutdownMessage)
    registry.register('Tick', TickMessage)
    registry.register('Tock', TockMessage)
    registry.register('BotOrder', BotOrderMessage)

initialize()
