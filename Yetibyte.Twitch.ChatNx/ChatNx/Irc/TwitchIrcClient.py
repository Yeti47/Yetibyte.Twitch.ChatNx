from .IrcClient import *
from .IrcMember import *
from .IrcMessage import *
from .IrcClientListener import *
from ..Configuration.TwitchConnectionSettings import *
from ..Configuration.ChatNxCommandProfile import *

import logging
import twitchio
import asyncio
import sys


class TwitchIrcClient(IrcClient):
    
    def __init__(self, command_prefix: str, connection_settings: TwitchConnectionSettings, logger: logging.Logger = None, loop = None):
        self._command_prefix = command_prefix
        self._connection_settings = connection_settings
        self._logger = logger or logging.Logger('__TWITCH__')
        self._listeners: list[IrcClientListener] = []
        self._twitch_client = twitchio.Client(self.auth_token, loop=loop)
        self._twitch_client._connection._close = self.__close_websocket
        self._twitch_client.event_message = self._event_message
        #self._twitch_client.add_event(self._event_message, 'event_message')

        self._is_connected = False

    @property
    def auth_token(self)->str:
        return self._connection_settings.auth_token

    @property
    def channel_name(self)->str:
        return self._connection_settings.channel

    @property
    def user_name(self)->str:
        return self._connection_settings.bot_user_name

    async def __close_websocket(self):
        """Replaces the original closing behavior of twitchio's WebsocketConnection.
           Makes sure the http session is properly closed. Otherwise, there will be an unclosed connector
           which leads to an exception being thrown. """
        self._twitch_client._connection._keeper.cancel()
        self._twitch_client._connection.is_ready.clear()

        futures = self._twitch_client._connection._fetch_futures()

        for fut in futures:
            fut.cancel()

        await self._twitch_client._http.session.close()
        await self._twitch_client._connection._websocket.close()

    def add_listener(self, listener)->None:
        self._listeners.append(listener)

    def is_connected(self)->bool:
        #return self._twitch_client.connected_channels and (len(self._twitch_client.connected_channels) > 0) and self._twitch_client._connection.is_alive
        return self._is_connected

    async def connect(self)->bool:
        self._logger.info(f'TwitchIrcClient: Trying to connect...')
        if self.is_connected():
            self._logger.info(f'TwitchIrcClient: Already connected.')
            return False

        try:
            await self._twitch_client.connect()
        except asyncio.CancelledError as cancel_ex:
            self._logger.error(f'TwitchIrcClient: Error connecting to Twitch IRC. Details: {cancel_ex}')
            return False
        except Exception as ex:
            self._logger.error(f'TwitchIrcClient: Error connecting to Twitch IRC. Details: {ex}')
            return False
        finally:
            await asyncio.sleep(0.05)

        try:
            await self._twitch_client.join_channels([self.channel_name])
        except Exception as ex:
            self._logger.error(f'TwitchIrcClient: Error connecting to Twitch IRC. Details: {ex}')
            await asyncio.sleep(0.05)
            return False
        finally:
            await asyncio.sleep(0.05)

        try:
            await asyncio.wait_for(self._wait_for_join(), 10)
        except asyncio.TimeoutError as timeout_ex:
            self._logger.error(f'TwitchIrcClient: Timeout occurred while trying to join channel {self.channel_name}.')
            return False
        finally:
            await asyncio.sleep(0.05)

        self._is_connected = True

        self._logger.info(f'TwitchIrcClient: Connected.')

        return True

    async def _wait_for_join(self):
        
        try:
            while (self.channel_name.casefold() not in [c.name.casefold() for c in self._twitch_client.connected_channels]):
                await asyncio.sleep(0.05)
        except Exception as ex:
            pass

    async def disconnect(self):

        success = False

        try:
            await self._twitch_client.close()
            success = True
        except Exception as ex:
            self._logger.error(f'TwitchIrcClient: Error during disconnect. Details: {ex}')

        self._is_connected = False

        if success:
            self._twitch_client.connected_channels.clear()
            self._logger.info(f'TwitchIrcClient: Disconnected.')
    
    async def send_message(self, content)->bool:

        self._logger.info(f'TwitchIrcClient: Sending message "{content}"...')

        if not self.is_connected():
            self._logger.error(f'TwitchIrcClient: Cannot send message. Client not connected.')
            return False

        channel = self._twitch_client.get_channel(self.channel_name)

        for listener in self._listeners:
            listener.on_sending_message(content)

        await channel.send(content)

        self._logger.info(f'TwitchIrcClient: Message sent successfully.')

        for listener in self._listeners:
            listener.on_message_sent(content)

        return True

    async def _event_message(self, message: twitchio.Message)->None:

        irc_message = message

        # author prop will be empty if message was sent by this bot
        if not irc_message or not irc_message.author:
            return
        
        for listener in self._listeners:
            listener.on_message_received(irc_message)

    async def dispose(self)->None:
        if self._twitch_client and self._twitch_client._http and self._twitch_client._http.session:
            await self._twitch_client._http.session.close()
        