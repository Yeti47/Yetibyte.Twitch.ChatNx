from .ChatNxClient import *
from .Configuration.ChatNxCommandSetup import *
from .Configuration.ChatNxCooldownSetup import *
from .ChatNxCommand import *
from .Irc.IrcClient import *
from .Irc.IrcMessage import *
from .Irc.IrcMember import *
from .CommandProcessingResult import *

import logging
import datetime
import typing

class CommandProcessor(object):
    """Processes a ChatNx command."""

    NULL_LOGGER = logging.Logger('_CP_NULL_')
    EPSILON = 0.001

    def __init__(self, 
                 chat_nx_client: "ChatNxClient",
                 command_setup: ChatNxCommandSetup, 
                 cooldown_setup: ChatNxCooldownSetup, 
                 irc_client: IrcClient,
                 logger: logging.Logger = None):
        self._chat_nx_client = chat_nx_client
        self._command_setup = command_setup
        self._cooldown_setup = cooldown_setup
        self._irc_client = irc_client
        self._logger = logger or CommandProcessor.NULL_LOGGER
        self._last_uses: dict[str,datetime.datetime] = {}
        self._shared_last_use: Optional[datetime.datetime] = None

    @property
    def command_setup(self)->ChatNxCommandSetup:
        return self._command_setup

    @property
    def normalized_command_name(self)->str:
        return self._command_setup.command.strip().casefold()

    @property
    def shared_last_use(self)->Optional[datetime.datetime]:
        return self._shared_last_use

    def applies_to(self, command_name: str)->bool:
        return self.normalized_command_name == command_name.strip().casefold()

    def get_last_use(self, user_name: str)->Optional[datetime.datetime]:
        return self._last_uses.get(user_name.casefold(), None)

    def update_last_use(self, user_name: str)->None:
        self._last_uses[user_name.casefold()] = datetime.datetime.now()

    def get_cooldown_time_for_user(self, user: IrcMember)->float:
        permission_level = PermissionLevel.ANY

        if user.name.casefold() == self._chat_nx_client.channel_name.casefold():
            permission_level = PermissionLevel.OWN
        elif user.is_mod:
            permission_level = PermissionLevel.MOD
        elif user.is_subscriber:
            permission_level = PermissionLevel.SUB

        user_time = self._cooldown_setup.get_time(permission_level)

        return user_time if user_time != None else 0

    def _update_last_use(self, user_name: str)->None:
        self._last_uses[user_name.casefold()] = datetime.datetime.now()
    
    def process(self, command: ChatNxCommand)->CommandProcessingResult:
        
        if not self.applies_to(command.command):
            return CommandProcessingResult(
                success=False,
                is_match=False,
                was_enqueued=False,
                time_remaining=0.0,
                shared_time_remaining=0.0)

        shared_time_remaining = 0

        if self._shared_last_use != None:
            shared_time_delta = (datetime.datetime.now() - self._shared_last_use).total_seconds()
            shared_time_remaining = max(self._cooldown_setup.shared_time - shared_time_delta, 0)

        user_cooldown_time = self.get_cooldown_time_for_user(command.irc_message.author)

        last_use = self.get_last_use(command.irc_message.author.name)

        time_remaining = 0

        if last_use != None:
            time_delta = (datetime.datetime.now() -last_use).total_seconds()
            time_remaining = max(user_cooldown_time - time_delta, 0)

        if shared_time_remaining > CommandProcessor.EPSILON or time_remaining > CommandProcessor.EPSILON:
            return CommandProcessingResult(
                success=False,
                is_match=True,
                was_enqueued=False,
                time_remaining=time_remaining,
                shared_time_remaining=shared_time_remaining)

        curr_time = datetime.datetime.now()

        self._shared_last_use = curr_time
        self._update_last_use(command.irc_message.author.name)

        self._chat_nx_client.enqueue_command(command)

        return CommandProcessingResult(
                success=True,
                is_match=True,
                was_enqueued=True,
                time_remaining=0.0,
                shared_time_remaining=0.0)
        

