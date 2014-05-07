import os
import collections
try:
    import simplejson as json
except ImportError:
    import json

from inception import framework
from inception.math import Vector3, Quaternion, Situation
from aisbx import logger, game
from api.vector2 import Vector2
import api.jsonhelpers
import api.commander

from ctf.events import *
from ctf.commands import *

from ctf.network import registry


DEFAULT_REPLAY_FILENAME = os.path.join('output', 'ctf.replay')

log = logger.getLog(logger.LOG_APP)


def ascii_encode_dict(data):
    """ Helps to decode unicode strings in cascaded dicts/lists read from a replay file via JSON
    """

    def ascii_encode(x):
        if type(x) == dict:
            return ascii_encode_dict(x)
        if type(x) == list:
            return [ascii_encode(y) for y in x]
        if type(x) == unicode:
            return x.encode('ascii')
        return x
    return dict(map(ascii_encode, pair) for pair in data.items())


class EventSaver(object):
    """ Proxyobject used by the Replayservice
    """

    def __init__(self, controller, index, replayService):
        self.index = index
        self.controller = controller
        self.replayService = replayService

    def __call__(self, event):
        self.replayService.saveEvent(self.controller, self.index, event)


class ReplayService(object):
    """ ReplayService inherits from BridgeService and implements ReplayFunctionality via the BridgeInterface
    """

    def __init__(self, enable):
        super(ReplayService, self).__init__()
        self.enabled = enable
        self.frame = 0
        self.level = ''
        self.commanders = []
        self.controllers = []
        self.dictionary = None
        self.validate = None

        #: dictionary of frame number to dictionaries of controller name to a list of events
        if self.enabled:
            self.data = None
        else:
            self.data = collections.defaultdict(lambda: collections.defaultdict(list))



    def initialize(self):
        """ Implementation of virtual method called when a BridgeService Object is enabled
        """
        pass

    
    def subscribeToControllers(self, controller, depth=0):
        """ Implementation of virtual method called when a BridgeService Object is supposed to chose the controllers it is interested in
        """

        if not self.enabled:
            controller.subscribe(framework.Event, EventSaver(controller, len(self.controllers), self))
        self.controllers.append(controller)

        if isinstance(controller, framework.CompositeController):
            for child in controller.getControllers():
                self.subscribeToControllers(child, depth+1)

        if depth == 0 and self.validate is not None:
            if self.validate != [self._getKey(c, i) for i, c in enumerate(self.controllers)]:
                log.warning("Replay data is not an exact match for this version of the simulation.")
            else:
                log.info("Replay loaded is fully compatible with this version of the simulation.")


    def resetFrameCounter(self):
        self.frame = -1


    def incrementFrameCounter(self):
        self.frame += 1


    def _getKey(self, ctrl, idx):
        return "%s_%d" % (ctrl.__class__.__name__, idx)


    def saveEvent(self, controller, index, event):
        entry = toDict(event)
        if entry is None:
            return

        key = self._getKey(controller, index)
        self.data[str(self.frame)][key].append(entry)
        log.debug("Saved {} {}".format(self.frame, event))


    def requestEvents(self, controller, index):
        """ Implementation of virtual method called when the BridgeService Object is expected to inject events
        """

        key = self._getKey(controller, index)
        idx = str(self.frame)
        if idx not in self.data:
            return

        data = self.data[idx].get(key, [])
        for d in data:
            # log.debug("Replay {} {}".format(self.frame, json.dumps(d, default=toJSON)))
            self.applyPositionCorrection(d)
            event = self.createEvent(d)
            if event is not None:
                controller.send(event)

        if len(data) == 0 and key in self.data[idx]:
                log.warn("Empty replay data found for `%s' at frame %i. %r" % (key, self.frame, self.data[str(self.frame)][key]))


    def saveToFile(self, filename):
        f = open(filename, 'w')
        keys = [self._getKey(c, i) for i, c in enumerate(self.controllers)]
        data = {'level': self.level, 'commanders': self.commanders, 'events': self.data, 'validate': keys, 'format': '0'}
        serialized_data = json.dumps(data, default=toJSON, sort_keys=True, indent=2, separators=(',', ': '))
        f.write(serialized_data)
        f.close()


    def loadFromFile(self, filename):
        f = open(filename, 'r')
        serialized_data = f.read()
        f.close()
        data = json.loads(serialized_data, object_hook=ascii_encode_dict)

        self.validate = data.get('validate', None)
        self.level = data['level']
        self.commanders = data['commanders']
        self.data = data['events']


    def createEvent(self, dct):
        assert '__class__' in dct
        cls =  dct['__class__']
        value = dct['__value__']
        
        if value is None:
            return None

        if cls == 'BotOrderEvent':
            order = registry.deserialize(value['order'])
            order.botId = value['bot']
            return BotOrderEvent(self.dictionary.bots[value['bot']], order)

        if cls == 'BotRespawnEvent':
            return BotRespawnEvent(self.dictionary.bots[value['bot']], toSituation(value['situation']))

        if cls == 'FlagPickedUpEvent':
            return FlagPickedUpEvent(self.dictionary.flags[value['flag']], self.dictionary.bots[value['bot']])

        if cls == 'FlagDroppedEvent':
            return FlagDroppedEvent(self.dictionary.flags[value['flag']], self.dictionary.bots[value['bot']])

        if cls == 'FlagCapturedEvent':
            return FlagCapturedEvent(self.dictionary.flags[value['flag']], self.dictionary.bots[value['bot']])

        if cls == 'FlagRestoredEvent':
            return FlagRestoredEvent(self.dictionary.flags[value['flag']])

        if cls == 'ChangeTargetCommand':
            return ChangeTargetCommand(self.dictionary.bots[value['bot']], self.dictionary.bots[value['target']] if value['target'] else None)

        if cls == 'WeaponClearTargetCommand':
            return WeaponClearTargetCommand(self.dictionary.weapons[value['weapon']])

        if cls == 'WeaponFireShotCommand':
            return WeaponFireShotCommand(self.dictionary.weapons[value['weapon']], self.dictionary.bots[value['target']])

        if cls == 'WeaponKillTargetCommand':
            return WeaponKillTargetCommand(self.dictionary.weapons[value['weapon']], self.dictionary.bots[value['target']])

        assert False, 'Unknown event class type {}'.format(cls)
        return None


    def applyPositionCorrection(self, dct):
        for name, situation in dct.get('__positions__', {}).items():
            sit = toSituation(situation)
            loc = self.dictionary.bots[name].location
            dist = loc.getPosition().distance(sit.position)
            if dist > 0.001:
                log.debug("%4.3fm deviation for %s in %s." % (dist, name, dct["__class__"]))
                loc.setSituation(sit)


def toVector2(list):
    if not list: return None
    assert len(list) == 2
    return Vector2(list[0], list[1])


def fromVector2(v):
    return [v.x, v.y]


def toVector3(list):
    if not list: return None
    assert len(list) == 3
    return Vector3(list[0], list[1], list[2])


def fromVector3(v):
    return [v.x, v.y, v.z]


def fromQuaternion(q):
    return [q.x, q.y, q.z, q.w]


def toQuaternion(list):
    if not list: return None
    assert len(list) == 4
    return Quaternion(list[3], list[0], list[1], list[2])


def toSituation(list):
    return Situation(toVector3(list[0]), toQuaternion(list[1]))


def toJSON(python_object):
    if isinstance(python_object, Vector2):
        return fromVector2(python_object)

    if isinstance(python_object, Vector3):
        return fromVector3(python_object)

    if isinstance(python_object, Quaternion):
        return fromQuaternion(python_object)

    if isinstance(python_object, Situation):
        return (python_object.position, python_object.orientation)

    raise TypeError(repr(python_object) + ' is not serializable') 


def toDict(event):
    if isinstance(event, BotOrderEvent):
        # No need to save the bot name in the order as well, it's duplicate data that takes up
        # more space in the database when the replays are saved.
        botId = event.order.botId
        event.order.botId = None
        order = registry.serialize(event.order)
        event.order.botId = botId

        return {'__class__': 'BotOrderEvent',
                '__value__': {'bot': event.bot.name, 'order': order},
                '__positions__': {event.bot.name: event.bot.location.getSituation()}}

    if isinstance(event, BotRespawnEvent):
        return {'__class__': 'BotRespawnEvent',
                '__value__': {'bot': event.bot.name, 'situation': event.situation}}

    if isinstance(event, FlagPickedUpEvent):
        return {'__class__': 'FlagPickedUpEvent',
                '__value__': {'flag': event.flag.name, 'bot': event.bot.name},
                '__positions__': {event.bot.name: event.bot.location.getSituation()}}

    if isinstance(event, FlagDroppedEvent):
        return {'__class__': 'FlagDroppedEvent',
                '__value__': {'flag': event.flag.name, 'bot': event.bot.name},
                '__positions__': {event.bot.name: event.bot.location.getSituation()}}

    if isinstance(event, FlagCapturedEvent):
        return {'__class__': 'FlagCapturedEvent',
                '__value__': {'flag': event.flag.name, 'bot': event.bot.name},
                '__positions__': {event.bot.name: event.bot.location.getSituation()}}

    if isinstance(event, FlagRestoredEvent):
        return {'__class__': 'FlagRestoredEvent',
                '__value__': {'flag': event.flag.name}}

    if isinstance(event, ChangeTargetCommand):
        return {'__class__': 'ChangeTargetCommand',
                '__value__': {'bot': event.bot.name, 'target': event.target.name if event.target else None}}
    
    if isinstance(event, WeaponClearTargetCommand):
        return {'__class__': 'WeaponClearTargetCommand',
                '__value__': {'weapon': event.weapon.name}}

    if isinstance(event, WeaponFireShotCommand):
        return {'__class__': 'WeaponFireShotCommand',
                '__value__': {'weapon': event.weapon.name, 'target': event.target.name},
                '__positions__': {event.weapon.character.name: event.weapon.location.getSituation(),
                                  event.target.name: event.target.location.getSituation()}}

    if isinstance(event, WeaponKillTargetCommand):
        return {'__class__': 'WeaponKillTargetCommand',
                '__value__': {'weapon': event.weapon.name, 'target': event.target.name},
                '__positions__': {event.weapon.character.name: event.weapon.location.getSituation(),
                                  event.target.name: event.target.location.getSituation()}}

    # if event.__class__.__name__ == 'PerceivedEvent':
    #     return {'__class__': 'PerceivedEvent', '__value__': None,
    #             '__positions': {event.who.character.name: event.who.location.getSituation(),
    #                             event.whom.character.name: event.whom.location.getSituation()}}

    # raise NotImplementedError("Not expecting `%s' in the replay serialization." % event.__class__)


class ReplayCommander(api.commander.Commander):
    """
    This commander doesn't do anything. It is a placeholder for the real commanders when we are doing replays
    """

    def __init__(self, nick, **kwargs):
        super(ReplayCommander, self).__init__(nick, **kwargs)
        self.name = kwargs.get('name', nick).split('.')[-1]

    def tick(self):
        pass
