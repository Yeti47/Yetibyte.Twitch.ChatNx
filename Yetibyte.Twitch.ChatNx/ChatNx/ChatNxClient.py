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
from .CommandProcessor import *
import logging
import asyncio
import os
import time

class ClientAlreadyRunningError(Exception):
    pass

class ClientNotInitializedError(Exception):
    pass

class SwitchConnectInitError(Exception):
    pass

class ChatNxClient(IrcClientListener):
    
    def __init__(self, config: ChatNxConfig, command_profile: ChatNxCommandProfile, switch_connector: SwitchConnector, irc_client: IrcClient, queue_receiver_client: ChatNxQueueReceiverClientBase = None, logger: logging.Logger = None):
        self._config = config
        self._command_profile = command_profile
        self._switch_connector: SwitchConnector = switch_connector
        self._irc_client = irc_client
        self._queue_receiver_client = queue_receiver_client
        self._logger = logger or logging.Logger('__EMPTY__')
        self._command_queue: list[ChatNxCommand] = []
        self._is_connected_to_switch = False
        self._command_processors: list[CommandProcessor] = []
        self._is_running = False
        self._queue_lock = False
        self._irc_client.add_listener(self)

    @property
    def channel_name(self)->str:
        return self._irc_client.channel_name or self._config.connection_settings.channel

    @property
    def queue_size(self):
        return len(self._command_queue)

    @property
    def is_connected_to_switch(self)->bool:
        return self._is_connected_to_switch

    @property
    def is_connected_to_irc(self)->bool:
        return self._irc_client.is_connected()

    @property
    def is_running(self)->bool:
        return self._is_running

    @property
    def is_connected_to_queue_receiver(self)->bool:
        return self._queue_receiver_client and self._queue_receiver_client.is_connected()

    @property
    def has_queue_receiver_client(self)->bool:
        return self._queue_receiver_client and True

    def connect_to_queue_receiver(self)->bool:

        if not self._queue_receiver_client:
            return False

        is_connected = self._queue_receiver_client.connect()

        return is_connected

    async def connect_to_irc(self)->str:

        is_connected = await self._irc_client.connect()

        if not is_connected:
            return ''

        return self._irc_client.channel_name

    def get_queued_commands(self):
        return self._command_queue.copy()

    def enqueue_command(self, command: ChatNxCommand)->None:
        
        if command in self._command_queue or command.id in [c.id for c in self._command_queue]:
            self._logger.warn(f'ChatNxClient: Command {command.id} already in queue. Will not enqueue again.')
            return

        #while self._queue_lock:
        #    pass

        self._queue_lock = True

        self._command_queue.append(command)

        self._logger.info(f'ChatNxClient: Command {command.id} enqueued for execution.')

        if self.is_connected_to_queue_receiver:
            self._queue_receiver_client.enqueue(command)
            sync_task = asyncio.create_task(self._synchronize_queue(command))

        if self.queue_size == 1:
            process_command_task = asyncio.create_task(self._process_current_command())

    async def _process_current_command(self)->None:

        if self.queue_size <= 0:
            return

        current_command = min(self._command_queue, key=(lambda c: c.timestamp))

        macro = current_command.command_setup.macro
        macro_id = await self._switch_connector.macro(
            macro.controller_index, 
            macro, 
            block=False, 
            callback=(lambda mid: self._on_macro_finished(mid, current_command)))

        self._queue_lock = False

    async def _synchronize_queue(self, current_command)->None:

        asyncio.sleep(0.001)

        queue_status = await self._queue_receiver_client.fetch_status()

        for queued_command in [cmd for cmd in self._command_queue if cmd.id != current_command.id]:
            if queued_command.id not in queue_status.queue_item_ids:
                self._command_queue.remove(queued_command)

    def _on_macro_finished(self, macro_id: str, command: ChatNxCommand)->None:
        self._command_queue.remove(command)

        if self.is_connected_to_queue_receiver:
            self._queue_receiver_client.set_complete(command.id)

        process_command_task = asyncio.create_task(self._process_current_command())

    def _initialize_command_processors(self):
        self._command_processors.clear()
        
        for command_setup in self._command_profile.commands:
        
            matching_cooldowns = \
                [c for c in self._command_profile.cooldown_groups if c.name.casefold() == command_setup.cooldown_group.casefold()] \
                if command_setup.cooldown_group \
                else []
        
            cooldown_setup = matching_cooldowns[0] if len(matching_cooldowns) > 0 else ChatNxCooldownSetup("NONE", 0)
            command_processor = CommandProcessor(self, command_setup, cooldown_setup, self._irc_client, self._logger)
        
            self._command_processors.append(command_processor)
        

    async def run(self)->None:

        if self.is_running:
            raise ClientAlreadyRunningError

        if not self.is_connected_to_switch:
            raise ClientNotInitializedError('The client is not connected to a Nintendo Switch console.')

        if not self.is_connected_to_irc:
            raise ClientNotInitializedError('The client is not connected to Twitch IRC.')

        if not self.is_connected_to_queue_receiver:
            self._logger.warn('ChatNxClient: Not connected to queue receiver.')

        self._initialize_command_processors()

        self._command_queue.clear()

        if self.is_connected_to_queue_receiver:
            self._queue_receiver_client.clear_queue()

        # run_task = asyncio.create_task(self._run_loop(), "chat_nx_client_run")
        self._is_running = True

    def stop(self)->None:
        self._is_running = False
        

    async def _run_loop(self)->None:
        
        self._is_running = True

        while self.is_running:
            pass


    def _process_message(self, message: IrcMessage)->None:
        normalized_message = message.content.strip().casefold()

        self._logger.info(f'ChatNxClient: Processing message "{message.content}" received from user {message.author.display_name}.')

        if normalized_message.startswith(self._command_profile.prefix.casefold()):
            # message may be a command
            command_name = normalized_message[len(self._command_profile.prefix):]

            matching_command_procs = [cmd for cmd in self._command_processors if cmd.applies_to(command_name)]

            if len(matching_command_procs) <= 0:
                self._logger.warn(f'ChatNxClient: Command "{command_name}" not found.')
            else:
                command_proc = matching_command_procs[0]

                command_id = os.urandom(24).hex()
                command = ChatNxCommand(command_id, message, command_proc.command_setup)

                process_result = command_proc.process(command)

                # command could not be processed
                if not process_result.success:

                    if process_result.shared_time_remaining > 0:
                        warn_msg = f'Command "{command_name}" is not ready yet. Please wait another {process_result.shared_time_remaining:.2f} seconds.'
                        self._logger.warn(f'ChatNxClient: {warn_msg}')
                        send_msg_task = asyncio.create_task(self._irc_client.send_message(f'@{message.author.name}, {warn_msg}'))
                        pass
                    elif process_result.time_remaining > 0:
                        warn_msg = f'Command "{command_name}" is still on cooldown for user {message.author.name}. Remaining time: {process_result.time_remaining:.2f} seconds.'
                        self._logger.warn(f'ChatNxClient: {warn_msg}')
                        send_msg_task = asyncio.create_task(self._irc_client.send_message(f'@{message.author.name}, you are still on cooldown for command "{command_name}". Please wait another {process_result.time_remaining:.2f} seconds before using the command again.'))
                        pass

    def on_message_received(self, message: IrcMessage)->None:

        if not self.is_running:
            return

        self._process_message(message)


    def on_sending_message(self, message: str)->None:
        pass

    def on_message_sent(self, message: str)->None:
        pass

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
                self._logger.warn(f'ChatNxClient: Controller at index {controller_id} already exists. Skipping.')
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
                raise RuntimeError(f"Could not connect controller {controller_id}.")

        await asyncio.sleep(0.5)

        self._is_connected_to_switch = len(self._switch_connector.get_switch_addresses()) > 0

        return self._switch_connector.get_switch_addresses()[0] if len(self._switch_connector.get_switch_addresses()) > 0 else ''


