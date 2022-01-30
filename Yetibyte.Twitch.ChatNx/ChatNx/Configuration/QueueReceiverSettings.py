import json
from json import JSONEncoder, JSONDecoder
from json.decoder import WHITESPACE

class QueueReceiverSettings(object):
    """Encapsulates configuration settings for a ChatNx queue receiver connection."""
    def __init__(self, address: str, port = 4769):
        self.address = address
        self.port = port


class QueueReceiverSettingsJsonEncoder(JSONEncoder):
    
    def default(self, object):
        if not isinstance(object, QueueReceiverSettings):
            return json.JSONEncoder.default(self, object)
        
        return { "__type__": type(object).__name__, "address": object.address, "port": object.port }

class QueueReceiverSettingsJsonDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        
        typename = dct.get('__type__')

        if typename != 'QueueReceiverSettings':
            return dct

        address = dct['address'] if 'address' in dct else ''
        port = dct['port'] if 'port' in dct else 4769

        return QueueReceiverSettings(address, port)

