from .PermissionLevel import *
from .ChatNxMacro import *
from .ChatNxCommandSetup import *
from .ChatNxCooldownSetup import *
from .ChatNxCommandSetup import *
import json
from json import JSONEncoder, JSONDecoder
from json.decoder import WHITESPACE

class ChatNxCommandProfile(object):
    """Encapsulates the configuration of a set of ChatNx commands and cooldowns."""

    def __init__(self, name: str, commands = [], cooldown_groups = [], prefix = '!', controllers = ['PRO_CONTROLLER']):
        self._name = name
        self.commands = commands
        self.cooldown_groups = cooldown_groups
        self.prefix = prefix
        self.controllers = controllers

    @property
    def name(self)->str:
        return self._name

    def find_command(self, command_name: str)-> ChatNxCommandSetup:  
        for cmd in self.commands:
            if cmd.command.casefold() == command_name.casefold():
                return cmd
        return None

    def find_cooldown_group(self, name: str)-> ChatNxCooldownSetup:  
        for cooldown in self.cooldown_groups:
            if cooldown.name.casefold() == name.casefold():
                return cooldown
        return None


class ChatNxCommandProfileJsonEncoder(JSONEncoder):
    
    def default(self, object):
        if isinstance(object, PermissionLevel):
            return object.value
        if not isinstance(object, ChatNxCommandProfile):
            return json.JSONEncoder.default(self, object)

        command_encoder = ChatNxCommandSetupJsonEncoder()
        cooldown_encoder = ChatNxCooldownSetupJsonEncoder()

        encoded_commands = []
        encoded_cooldowns = []

        for command in object.commands:
            encoded_command = command_encoder.default(command)
            encoded_commands.append(encoded_command)

        for cooldown in object.cooldown_groups:
            encoded_cooldown = cooldown_encoder.default(cooldown)
            encoded_cooldowns.append(encoded_cooldown)

        return { "__type__": type(object).__name__, 
                "name": object.name, 
                "commands": encoded_commands, 
                "cooldown_groups": encoded_cooldowns, 
                "prefix": object.prefix, 
                "controllers": object.controllers }

class ChatNxCommandProfileJsonDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):

        typename = dct.get('__type__')
        
        if typename != 'ChatNxCommandProfile':
            return dct

        name = 'unnamed'
        prefix = '!'
        commands = []
        cooldown_groups = []
        controllers = [ 'PRO_CONTROLLER' ]

        if 'name' in dct:
            name = dct['name']

        if 'prefix' in dct:
            prefix = dct['prefix']

        if 'controllers' in dct:
            controllers = dct['controllers']
        
        if 'commands' in dct:
            encoded_commands = dct['commands']
            command_decoder = ChatNxCommandSetupJsonDecoder()

            for encoded_cmd in encoded_commands:
                cmd = command_decoder.decode(json.dumps(encoded_cmd))
                commands.append(cmd)
            
        if 'cooldown_groups' in dct:
            encoded_cooldowns = dct['cooldown_groups']
            cooldown_decoder = ChatNxCooldownSetupJsonDecoder()

            for encoded_cooldown in encoded_cooldowns:
                cooldown = cooldown_decoder.decode(json.dumps(encoded_cooldown))
                cooldown_groups.append(cooldown)

        profile = ChatNxCommandProfile(name, commands=commands, cooldown_groups=cooldown_groups, prefix=prefix, controllers = controllers)

        return profile

