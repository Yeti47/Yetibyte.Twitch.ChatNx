from .ChatNxDebugSettings import *
from .QueueReceiverSettings import *
from .TwitchConnectionSettings import *
from .ChatNxCommandProfile import *

from typing import Optional
import json
from json import JSONEncoder, JSONDecoder
from json.decoder import WHITESPACE

class ChatNxConfig(object):
    """Describes a set of configuration settings for ChatNx.""" 
    def __init__(self, connection_settings: TwitchConnectionSettings, queue_receiver_settings: QueueReceiverSettings = None, debug_settings: ChatNxDebugSettings = None):
        self.connection_settings = connection_settings
        self.queue_receiver_settings = queue_receiver_settings or QueueReceiverSettings('')
        self.debug_settings = debug_settings or ChatNxDebugSettings()
        self._command_profiles = []

    @property
    def command_profiles(self)-> list[ChatNxCommandProfile]:
        return self._command_profiles

    def get_command_profile(self, profile_name: str)->Optional[ChatNxCommandProfile]:
        return next((p for p in self._command_profiles if p.name.casefold() == profile_name.casefold()), None)

    def add_command_profile(self, command_profile: ChatNxCommandProfile)-> None:
        self._command_profiles.append(command_profile)

    def remove_command_profile(self, profile_name: str)->bool:
        command_profile = self.get_command_profile(profile_name)

        if command_profile:
            self._command_profiles.remove(command_profile)

        return True and command_profile

class ChatNxConfigJsonEncoder(JSONEncoder):

    def default(self, object):
        if not isinstance(object, ChatNxConfig):
            return json.JSONEncoder.default(self, object)

        connection_encoder = TwitchConnectionSettingsJsonEncoder()
        receiver_encoder = QueueReceiverSettingsJsonEncoder()
        debug_settings_encoder = ChatNxDebugSettingsJsonEncoder()
        
        return { "__type__": type(object).__name__,
                "connection_settings": connection_encoder.default(object.connection_settings), 
                "queue_receiver_settings": receiver_encoder.default(object.queue_receiver_settings),
                "debug_settings": debug_settings_encoder.default(object.debug_settings) }

class ChatNxConfigJsonDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):

        typename = dct.get('__type__')
        
        if typename != 'ChatNxConfig':
            return dct

        connection_settings = TwitchConnectionSettings('', '', '')
        queue_receiver_settings = QueueReceiverSettings('')
        debug_settings = ChatNxDebugSettings()

        if 'connection_settings' in dct:
            connection_settings = TwitchConnectionSettingsJsonDecoder().decode(json.dumps(dct['connection_settings']))
        if 'queue_receiver_settings' in dct:
            queue_receiver_settings = QueueReceiverSettingsJsonDecoder().decode(json.dumps(dct['queue_receiver_settings']))
        if 'debug_settings' in dct:
            debug_settings= ChatNxDebugSettingsJsonDecoder().decode(json.dumps(dct['debug_settings']))

        return ChatNxConfig(connection_settings, queue_receiver_settings, debug_settings)
