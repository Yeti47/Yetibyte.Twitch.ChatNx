from .IrcClient import *
from .IrcClientListener import *
from .IrcMember import *
from .IrcMessage import *
from ..Configuration import TwitchConnectionSettings, ChatNxCommandProfile

import logging
from logging import Logger
import asyncio
from random import Random 
from datetime import datetime
import os
import time

class MockIrcClient(IrcClient):
    """Mock implementation of an IRC client."""

    INVALID_MESSAGE_PROBABILITY = 33

    MEMBERS = [ 
        IrcMember("bobby", "#FF0000", False, False, "Bobby"),
        IrcMember("testytestington", "#0000FF", True, False, "TestyTestington"),
        IrcMember("someone", "#DD00DD", False, False, "someone"),
        IrcMember("henryxv", "#00CC44", True, False, "HenryXV"),
        IrcMember("user123", "#EEDD00", False, False, "User123"),
        IrcMember("user456", "#2233CC", False, False, "User456"),
        IrcMember('somemod', "#CC0033", True, True, "SomeMod"),
        IrcMember('someothermod', "#3300CC", True, True, "SomeOtherMod")
    ]

    INVALID_MESSAGES = [
        'Haha, that is funny!',
        'Hello everybody',
        'How are you guys today?',
        'AFK for a while',
        'This is a really nice stream!'
    ]

    def __init__(self, connection_settings: TwitchConnectionSettings, command_profile: ChatNxCommandProfile, logger: Logger):
        self._command_prefix = command_profile.prefix
        self._connection_settings = connection_settings
        self._command_profile = command_profile
        self._logger = logger
        self._listeners: list[IrcClientListener] = []
        self._is_connected = False
        self._random = Random()

    @property
    def user_name(self):
        return self._connection_settings.bot_user_name

    @property
    def channel_name(self):
        return self._connection_settings.channel

    @property
    def auth_token(self):
        return self._connection_settings.auth_token

    def add_listener(self, listener):
        self._listeners.append(listener)
        self._logger.info(f'MockIrcClient: Added listener.')

    async def connect(self):
        self._logger.info(f'MockIrcClient: Trying to connect...')
        if self.is_connected():
            self._logger.info(f'MockIrcClient: Already connected.')
            return False

        self._logger.info(f'MockIrcClient: Simulating connection.')

        time.sleep(2)

        self._is_connected = True

        # call coroutine
        connection_task = asyncio.create_task(self._simulate_connection())

        self._logger.info(f'MockIrcClient: Connected.')

        return True

    async def disconnect(self):
        self._is_connected = False
        self._logger.info(f'MockIrcClient: Disconnected.')

    async def _simulate_connection(self)->None:

        while self.is_connected():
            wait_time = self._random.randint(3, 12)
            await asyncio.sleep(wait_time)

            member_index = self._random.randint(0, len(MockIrcClient.MEMBERS) - 1)
            member = MockIrcClient.MEMBERS[member_index]

            command_index = self._random.randint(0, len(self._command_profile.commands) - 1)
            command = self._command_profile.commands[command_index]
            
            message_content = ''

            if self._random.randint(1, 100) > MockIrcClient.INVALID_MESSAGE_PROBABILITY:
                message_content = f'{self._command_prefix}{command.command}'
            else:
                message_content = self._random.choice(MockIrcClient.INVALID_MESSAGES)

            message_id = os.urandom(24).hex()
            irc_message = IrcMessage(message_id, member, self._connection_settings.channel, message_content)

            self._on_message_received(irc_message)
            
    def _on_message_received(self, message: IrcMessage)->None:

        self._logger.info(f'MockIrcClient: Message Received | {message.timestamp} {message.author.display_name} {message.content}')

        for listener in self._listeners:
            listener.on_message_received(message)

    def _on_sending_message(self, message: str)->None:
        for listener in self._listeners:
            listener.on_sending_message(message)

    def _on_message_sent(self, message: str)->None:
        timestamp = datetime.now()

        self._logger.info(f'MockIrcClient:  Message sent | {timestamp} {self.user_name} {message}')

        for listener in self._listeners:
            listener.on_message_sent(message)

    def is_connected(self):
        return self._is_connected

    async def send_message(self, content):
        self._logger.info(f'MockIrcClient: Trying to send message...')
        
        if not self.is_connected():
            self._logger.error(f'MockIrcClient: Cannot send message. Not connected.')
            return

        self._on_sending_message(content)
        self._on_message_sent(content)
        
    async def dispose(self):
        pass

