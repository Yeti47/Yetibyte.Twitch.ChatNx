from .PermissionLevel import *

import json
from json import JSONEncoder, JSONDecoder
from json.decoder import WHITESPACE
from typing import Optional


class ChatNxCooldownSetup(object):
    """Describes the configuration of a ChatNx command cooldown."""

    def __init__(self, name: str, shared_time: int = 0):
        self._name = name
        self._times = {  }
        self.shared_time = shared_time

    @property
    def times(self)-> dict[PermissionLevel,int]:
        return self._times

    @property
    def name(self)-> str:
        return self._name

    @property
    def shared_time(self)->int:
        return self._shared_time

    @shared_time.setter
    def shared_time(self, value: int)->None:
        self._shared_time = max(0, value)

    def get_time(self, level: PermissionLevel)-> Optional[int]:
        # Find the time with the next lowest key value (OWN => MOD => SUB => ANY)
        sorted_keys = sorted(self._times.keys(), key=(lambda x:x.get_int_value()), reverse=True)
        lower_keys = [k for k in sorted_keys if k.get_int_value() <= level.get_int_value()]

        return self._times[lower_keys[0]] if lower_keys else None

    def set_time(self, level: PermissionLevel, seconds: int)-> None:
        self._times[level] = seconds


class ChatNxCooldownSetupJsonEncoder(JSONEncoder):
    
    def default(self, object):
        if isinstance(object, PermissionLevel):
            return object.value
        if not isinstance(object, ChatNxCooldownSetup):
            return json.JSONEncoder.default(self, object)

        times_encoded = {}

        for k, v in object.times.items():
            times_encoded[k.value] = v

        return { "__type__": type(object).__name__, "name": object.name, "shared_time": object.shared_time, "times": times_encoded }

class ChatNxCooldownSetupJsonDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):

        typename = dct.get('__type__')
        
        if typename != 'ChatNxCooldownSetup':
            return dct

        name = ''
        times = {}
        shared_time = 0
        
        if 'name' in dct:
            name = dct['name']
        if 'shared_time' in dct:
            shared_time = dct['shared_time']
        if 'times' in dct:
            times_encoded = dct['times']
            for k, v in times_encoded.items():
                times[PermissionLevel[k]] = v

        cooldown_setup = ChatNxCooldownSetup(name, shared_time)
        cooldown_setup._times = times # encoder is allowed to access private field to reduce overhead

        return cooldown_setup



