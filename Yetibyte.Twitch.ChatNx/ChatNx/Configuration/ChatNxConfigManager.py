from .ChatNxConfig import *
from .TwitchConnectionSettings import *
from .QueueReceiverSettings import *
from .ChatNxDebugSettings import *
from .ChatNxCommandProfile import *
from .PermissionLevel import *

import os
import json
from os import listdir

class ChatNxConfigManager(object):
    """Encapsulates logic for loading, saving and managing ChatNx configuration settings."""

    DEFAULT_CONFIG_FILE_NAME = 'chatnx.config'
    DEFAULT_PROFILE_DIRECTORY_PATH = f'.{os.path.sep}Profiles'
    PROFILE_FILE_EXTENSION = 'cnx'
    
    def __init__(self):
        self.config_file_name = ChatNxConfigManager.DEFAULT_CONFIG_FILE_NAME
        self.profile_directory_path = ChatNxConfigManager.DEFAULT_PROFILE_DIRECTORY_PATH

    def config_file_exists(self)->bool:
        return os.path.isfile(self.config_file_name)

    def save_config(self, config: ChatNxConfig)->None:
        config_json = json.dumps(config, cls=ChatNxConfigJsonEncoder, indent=4)

        config_file = open(self.config_file_name, "w")
        config_file.write(config_json)
        config_file.close()

        os.makedirs(self.profile_directory_path, exist_ok=True)

        for profile in config.command_profiles:
            self._save_profile(profile)

    def get_relative_profile_path(self, profile_name: str)->str:
        return f'{self.profile_directory_path}{os.path.sep}{profile_name}.{ChatNxConfigManager.PROFILE_FILE_EXTENSION}'

    def _save_profile(self, profile: ChatNxCommandProfile)->None:
        file_name = self.get_relative_profile_path(profile.name)

        profile_json = json.dumps(profile, cls=ChatNxCommandProfileJsonEncoder, indent=4)

        profile_file = open(file_name, "w")
        profile_file.write(profile_json)
        profile_file.close()

    def _load_profile(self, profile_name:str)->ChatNxCommandProfile:
        file_name = self.get_relative_profile_path(profile_name)

        profile_file = open(file_name, "r")
        profile_json = profile_file.read()
        profile_file.close()

        profile_decoder = ChatNxCommandProfileJsonDecoder()
        profile = profile_decoder.decode(profile_json)

        return profile

    def create_empty_config(self)->ChatNxConfig:
        config = ChatNxConfig(
            TwitchConnectionSettings('EnterTwitchChannelName', 'ENTER_AUTH_TOKEN', 'OptionalBotUserName'),
            queue_receiver_settings=QueueReceiverSettings('127.0.0.1'),
            debug_settings=ChatNxDebugSettings())

        example_profile = self.create_example_profile()

        config.add_command_profile(example_profile)

        return config

    def create_example_profile(self)->ChatNxCommandProfile:
        profile = ChatNxCommandProfile('ExampleProfile')

        macro_jump = ChatNxMacro([ MacroInput('A', 0.5) ])
        macro_jump_thrice = ChatNxMacro([ MacroInput('A', 0.5), MacroInput('', 0.5) , MacroInput('A', 0.5), MacroInput('', 0.5), MacroInput('A', 0.5), MacroInput('', 0.5) ])

        test_command_jump = ChatNxCommandSetup('jump', macro_jump, arguments=['high','low'], cooldown_group='JumpCooldown')
        test_command_jump_thrice = ChatNxCommandSetup('jump3x', macro_jump_thrice, arguments=[], cooldown_group='JumpCooldown')

        cooldown_jump = ChatNxCooldownSetup("JumpCooldown", 3)
        cooldown_jump.set_time(PermissionLevel.ANY, 15)
        cooldown_jump.set_time(PermissionLevel.SUB, 10)
        cooldown_jump.set_time(PermissionLevel.MOD, 5)

        profile.commands.append(test_command_jump)
        profile.commands.append(test_command_jump_thrice)
        profile.cooldown_groups.append(cooldown_jump)

        return profile

    def load_config(self)->ChatNxConfig:
        
        if not self.config_file_exists():
            empty_config = self.create_empty_config()
            self.save_config(empty_config)

        config_file = open(self.config_file_name, "r")
        config_json = config_file.read()
        config_file.close()

        config_decoder = ChatNxConfigJsonDecoder()

        config: ChatNxConfig = config_decoder.decode(config_json)

        profile_files = [f for f in listdir(self.profile_directory_path) if os.path.isfile(os.path.join(self.profile_directory_path, f)) and f.endswith(f'.{ChatNxConfigManager.PROFILE_FILE_EXTENSION}')]

        for profile_name in [p[:-(len(ChatNxConfigManager.PROFILE_FILE_EXTENSION)+1)] for p in profile_files]:
            profile = self._load_profile(profile_name)
            config.add_command_profile(profile)

        return config