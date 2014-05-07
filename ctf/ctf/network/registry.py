try:
    import simplejson as json
except ImportError:
    import json

EncodeRegistry = {}
DecodeRegistry = {}

def asciiEncodeDict(data):
    """ Helps to decode unicode strings in cascaded dicts/lists read from a replay file via JSON
    """

    def asciiEncode(x):
        if type(x) == dict:
            return asciiEncodeDict(x)
        if type(x) == list:
            return [asciiEncode(y) for y in x]
        if type(x) == unicode:
            return x.encode('ascii')
        return x
    return dict(map(asciiEncode, pair) for pair in data.items())

def defaultEncode(o):
    return o.__dict__

def defaultDecode(cls, x):
    o = cls()
    o.__dict__.update(x)
    return o

def toJSON(o):
    clsName = o.__class__.__name__
    if clsName in EncodeRegistry.keys():
        encodingData = EncodeRegistry[clsName]
        name = encodingData['name']
        encodeFn = encodingData['encode']
        key = '%s' % name
        return { key: encodeFn(o) }
    raise TypeError(repr(o) + ' is not JSON serializable')

def fromJSON(dct):
    dct = asciiEncodeDict(dct)

    if len(dct.keys()) == 1:
        name = next(iter(dct.keys()))
        if name in DecodeRegistry.keys():
            decodingData = DecodeRegistry[name]
            cls = decodingData['cls']
            decodeFn = decodingData['decode']
            return decodeFn(cls, dct[name])

    return dct


def register(name, cls, encodeFn=defaultEncode, decodeFn=defaultDecode):
    EncodeRegistry[cls.__name__] = {'name': name, 'encode': encodeFn }
    DecodeRegistry[name] = {'cls': cls, 'decode': decodeFn }


def serialize(message):
    return json.dumps(message, default = toJSON)


def deserialize(messageJson):
    try:
        return json.loads(messageJson, object_hook = fromJSON)
    except:
        import traceback
        traceback.print_exc()
