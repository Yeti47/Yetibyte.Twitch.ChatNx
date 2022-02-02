from .PermissionLevel import *
from .ChatNxMacro import *

import json
from json import JSONEncoder, JSONDecoder
from json.decoder import WHITESPACE

class ChatNxCommandSetup(object):
    """Describes the configuration of a ChatNx command."""

    def __init__(self, command: str, macro: ChatNxMacro, permission_level = PermissionLevel.ANY, arguments: list[str] = [], cooldown_group = ''):
        self._command = command
        self._arguments = arguments
        self.macro = macro
        self.cooldown_group = cooldown_group
        self.permission_level = permission_level

    @property
    def command(self)-> str:
        return self._command

    @property
    def arguments(self)-> list[str]:
        return self._arguments


class ChatNxCommandSetupJsonEncoder(JSONEncoder):
    
    def default(self, object):
        if not isinstance(object, ChatNxCommandSetup):
            return json.JSONEncoder.default(self, object)

        macro_encoder = ChatNxMacroJsonEncoder()
        encoded_macro = macro_encoder.default(object.macro)

        return { "__type__": type(object).__name__,
                "command": object.command, 
                "arguments": object.arguments, 
                "cooldown_group": object.cooldown_group, 
                "macro": encoded_macro,
                "permission_level": object.permission_level.value
               }

class ChatNxCommandSetupJsonDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):

        typename = dct.get('__type__')
        
        if typename != 'ChatNxCommandSetup':
            return dct

        command = ''
        arguments = []
        macro = ChatNxMacro()
        cooldown_group = ''
        permission_level = PermissionLevel.ANY
        
        if 'command' in dct:
            command = dct['command']
        if 'arguments' in dct:
            arguments = dct['arguments']
        if 'cooldown_group' in dct:
            cooldown_group = dct['cooldown_group']
        if 'permission_level' in dct:
            permission_level = dct['permission_level']
        if 'macro' in dct:
            macro_decoder = ChatNxMacroJsonDecoder()
            macro = macro_decoder.decode(json.dumps(dct['macro']))

        command_setup = ChatNxCommandSetup(command, 
                                           macro, 
                                           permission_level=permission_level, 
                                           arguments=arguments, 
                                           cooldown_group=cooldown_group)

        return command_setup

