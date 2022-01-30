import json
from json import JSONEncoder, JSONDecoder
from json.decoder import WHITESPACE

class ChatNxDebugSettings(object):
    """Describes a set of configuration settings that control debugging behavior."""

    def __init__(self, mock_switch_connector = False, mock_irc_client = False, mock_queue_receiver = False):
        self.mock_switch_connector = mock_switch_connector
        self.mock_irc_client = mock_irc_client
        self.mock_queue_receiver = mock_queue_receiver


class ChatNxDebugSettingsJsonEncoder(JSONEncoder):
    
    def default(self, object):
        if not isinstance(object, ChatNxDebugSettings):
            return json.JSONEncoder.default(self, object)
        
        return { "__type__": type(object).__name__,
                "mock_switch_connector": object.mock_switch_connector, 
                "mock_irc_client": object.mock_irc_client, 
                "mock_queue_receiver": object.mock_queue_receiver }

class ChatNxDebugSettingsJsonDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):

        typename = dct.get('__type__')
        
        if typename != 'ChatNxDebugSettings':
            return dct

        mock_switch_connector = dct['mock_switch_connector'] if 'mock_switch_connector' in dct else False
        mock_irc_client = dct['mock_irc_client'] if 'mock_irc_client' in dct else False
        mock_queue_receiver = dct['mock_queue_receiver'] if 'mock_queue_receiver' in dct else False

        return ChatNxDebugSettings(mock_switch_connector=mock_switch_connector,
                                   mock_irc_client=mock_irc_client,
                                   mock_queue_receiver=mock_queue_receiver)
