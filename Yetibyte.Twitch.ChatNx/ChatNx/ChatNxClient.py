from .SwitchConnector import *
from .Irc.IrcClient  import *
from .Irc.IrcClientListener  import *
from .Irc.IrcMessage  import *
from .Irc.IrcMember  import *
from .QueueReceiver.ChatNxQueueReceiverClientBase import *
from .QueueReceiver.QueueStatus import *
from .Configuration.ChatNxConfig import *
from .Configuration.ChatNxCommandProfile import *
from .Configuration.ChatNxCommandSetup import *
from .Configuration.ChatNxCooldownSetup import *
from .Configuration.ChatNxDebugSettings import *
from .Configuration.ChatNxMacro import *
from .Configuration.QueueReceiverSettings import *
from .Configuration.TwitchConnectionSettings import *
import logging
import asyncio

class SwitchConnectInitError(Exception):
    pass

class ChatNxClient(object):
    
    def __init__(self, config: ChatNxConfig, command_profile: ChatNxCommandProfile, switch_connector: SwitchConnector, irc_client: IrcClient, queue_receiver_client: ChatNxQueueReceiverClientBase, logger: logging.Logger = None):
        self._config = config
        self._command_profile = command_profile
        self._switch_connector: SwitchConnector = switch_connector
        self._irc_client = irc_client
        self._queue_receiver_client = queue_receiver_client
        self._logger = logger or logging.Logger('__EMPTY__')
        self._command_queue: list[ChatNxCommand] = []
        self._is_connected_to_switch = False

    @property
    def queue_size(self):
        return len(self._command_queue)

    @property
    def is_connected_to_switch(self)->bool:
        return _is_connected_to_switch

    def get_queued_commands(self):
        return self._command_queue.copy()

    async def connect_to_switch(self)->str:

        if not self._switch_connector.is_initialized():
            raise SwitchConnectInitError('The Switch Connector has not been initialized.')

        # create all non-existing controllers

        switch_state = self._switch_connector.get_state()

        controller_id = -1

        for controller in self._command_profile.controllers:

            controller_id = controller_id + 1

            self._logger.info(f'ChatNxClient: Creating controller {controller} at index {controller_id}...')

            if controller_id in switch_state:
                self._logger.warn(f'ChatNxClient: Controllor at index {controller_id} already exists. Skipping.')
                continue # controller already exists

            controller_type = ControllerTypes.PRO_CONTROLLER

            if controller.casefold() == 'joycon_l':
                controller_type = ControllerTypes.JOYCON_L
            elif controller.casefold() == 'joycon_r':
                controller_type = ControllerTypes.JOYCON_R

            self._switch_connector.create_controller(controller_type, reconnect_address=self._switch_connector.get_switch_addresses())

            self._logger.info(f'ChatNxClient: Controller created.')

        controller_id = -1

        # ensure all controllers are connected

        for controller in self._command_profile.controllers:

            controller_id = controller_id + 1

            self._logger.info(f'ChatNxClient: Connecting controller with index {controller_id}...')

            if self._switch_connector.is_controller_connected(controller_id):
                self._logger.warn(f'ChatNxClient: Controller {controller_id} already connected. Skipping...')
                continue

            is_controller_connected = await self._switch_connector.connect(controller_id)

            if not is_controller_connected:
                pass # TODO



