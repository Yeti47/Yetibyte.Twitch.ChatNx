from ..ChatNxCommand import *
from .QueueStatus import *
from .ChatNxQueueReceiverClientBase import *
from .CommandQueueRequest import *

import websocket
import traceback
import asyncio
from logging import Logger

REQUEST_ACTION_ADD = "ADD"
REQUEST_ACTION_COMPLETE = "COMPLETE"
REQUEST_ACTION_CHECK = "CHECK"
REQUEST_ACTION_CLEAR = "CLEAR"

class ChatNxQueueReceiverClient(ChatNxQueueReceiverClientBase):
    """Describes a client that connects with a ChatNx Queue Receiver application."""

    def __init__(self, address: str, port = 4769, logger: Logger = None):
        self.address = address
        self.port = port
        self._websocket = websocket.WebSocket(skip_utf8_validation=True)
        self._logger = logger or Logger("null_logger")

    @property
    def url(self):
        return f'ws://{self.address}:{self.port}/Queue'

    def is_connected(self)->bool:
        return self._websocket.connected

    def connect(self)->bool:
        if self.is_connected():
            return False
        
        self._logger.info(f'ChatNxQueueReceiverClient: Connecting to queue receiver at {self.url}...')

        try:
            self._websocket.connect(self.url)
        except Exception as ex:
            self._logger.error(f'ChatNxQueueReceiverClient: Could not connect to queue receiver at {self.url}. Details: {ex}')
            return False

        self._logger.info(f'ChatNxQueueReceiverClient: Connected successfully.')

        return True

    def disconnect(self):
        if not self.is_connected():
            return

        self._logger.info(f'ChatNxQueueReceiverClient: Disconnecting from {self.url}...')

        try:
            self._websocket.close()
        except Exception as ex:
            self._logger.error(f'ChatNxQueueReceiverClient: Error while disconnecting. Details: {ex}')

        self._logger.info(f'ChatNxQueueReceiverClient: Disconnected.')

    def set_complete(self, command_id: str)->bool:
        if not self.is_connected():
            self._logger.error(f'ChatNxQueueReceiverClient: Cannot set queue item to complete while disconnected.')
            raise TypeError

        self._logger.info(f'ChatNxQueueReceiverClient: Sending completion request for command with ID "{command_id}"...')

        complete_request = CommandQueueRequest(action=REQUEST_ACTION_COMPLETE, item_data=CommandQueueItemData(id=command_id))
        request_json = complete_request.to_json()

        try:
            self._websocket.send(request_json)
        except Exception as ex:
            self._logger.error(f'ChatNxQueueReceiverClient: An error occurred while trying to send a completion request to the queue receiver application. Details: {ex}')
            return False

        self._logger.info(f'ChatNxQueueReceiverClient: Request sent successfully!')

        return True
       
    def enqueue(self, command: ChatNxCommand):
        if not self.is_connected():
            self._logger.error(f'ChatNxQueueReceiverClient: Cannot enqueue item while disconnected.')
            raise TypeError

        command_data = CommandQueueItemData(
            id=command.id,
            user_name=command.irc_message.author.display_name,
            user_color_hex=command.irc_message.author.color,
            command=command.command
        )

        enqueue_request = CommandQueueRequest(action=REQUEST_ACTION_ADD, item_data=command_data)
        request_json = enqueue_request.to_json()

        self._logger.info(f'ChatNxQueueReceiverClient: Sending enqueue request for command with ID "{command.id}"...')

        try:
            self._websocket.send(request_json)
        except Exception as ex:
            self._logger.error(f'ChatNxQueueReceiverClient: An error occurred while trying to enqueue a command. Details: {ex}')
            return False

        self._logger.info(f'ChatNxQueueReceiverClient: Request sent successfully!')

        return True

    def clear_queue(self):
        if not self.is_connected():
            self._logger.error(f'ChatNxQueueReceiverClient: Cannot clear queue while disconnected.')
            raise TypeError

        clear_request = CommandQueueRequest(action=REQUEST_ACTION_CLEAR, item_data=None)
        request_json = clear_request.to_json()

        self._logger.info(f'ChatNxQueueReceiverClient: Sending clear queue request...')

        try:
            self._websocket.send(request_json)
        except Exception as ex:
            self._logger.error(f'ChatNxQueueReceiverClient: An error occurred while trying to send a clear request to the queue receiver application. Details: {ex}')
            return False

        self._logger.info(f'ChatNxQueueReceiverClient: Request sent successfully!')

        return True

    async def _receive_message(self)->str:
        return self._websocket.recv()

    async def fetch_status(self)->QueueStatus:

        if not self.is_connected():
            self._logger.error(f'ChatNxQueueReceiverClient: Cannot fetch status while disconnected.')
            raise TypeError

        status_request = CommandQueueRequest(action=REQUEST_ACTION_CHECK, item_data=None)
        request_json = status_request.to_json()

        self._logger.info(f'ChatNxQueueReceiverClient: Fetching queue status...')

        try:
            self._websocket.send(request_json)
        except Exception as ex:
            self._logger.error(f'ChatNxQueueReceiverClient: An error occurred while trying to send a status request to the queue receiver application. Details: {ex}')
            return None

        received_message = ''
        
        try:
            received_message = await asyncio.wait_for(self._receive_message(), timeout=3.0)
        except asyncio.TimeOutError as tex:
            self._logger.error(f'ChatNxQueueReceiverClient: A timeout occurred while trying to receive a message from the queue receiver application.')
            return None
        except Exception as ex:
            self._logger.error(f'ChatNxQueueReceiverClient: An error occurred while trying to receive a message from the queue receiver application. Details: {ex}')
            return None

        self._logger.info(f'ChatNxQueueReceiverClient: Queue status received.')

        queue_status = QueueStatus.from_json(received_message)

        return queue_status

        
