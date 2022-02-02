from .SwitchConnector import *
from .Configuration.ChatNxMacro import *

import logging
import os
import asyncio

class MockSwitchConnector(SwitchConnector):
    """Mock implementation of SwitchConnector"""

    MOCK_SWITCH_ADDRESS = 'MOCK_SWITCH_ADDRESS'
    MOCK_ADAPTER_NAME = 'mock_adapter'

    CONTROLLER_STATE_INITITALIZING = "initializing"
    CONTROLLER_STATE_CONNECTED = "connected"

    CONNECTION_TIME = 3.0

    def __init__(self, logger: logging.Logger = None):
        self._state = { }
        self._isInitialized = False
        self._logger = logger or logging.Logger("_NULL_")

    def initialize(self)->None:
        self._logger.info('MockSwitchConnector: Initialized.')
        self._isInitialized = True
        return True

    def reinitialize(self):
        self._logger.info('MockSwitchConnector: Re-initializing...')
        return self.initialize()

    def is_initialized(self)->bool:
        return self._isInitialized

    def create_controller(self, controller_type, adapter_path=None, colour_body=None, colour_buttons=None, reconnect_address=None)->int:

        index = self.get_controller_count()

        if not adapter_path:
            adapter_path = MockSwitchConnector.MOCK_ADAPTER_NAME

        controller_state = { }
        controller_state["state"] = MockSwitchConnector.CONTROLLER_STATE_INITITALIZING
        controller_state["finished_macros"] = []
        controller_state["errors"] = False
        controller_state["direct_input"] = ''
        controller_state["colour_body"] = colour_body
        controller_state["colour_buttons"] = colour_buttons
        controller_state["type"] = str(controller_type)
        controller_state["adapter_path"] = adapter_path
        controller_state["last_connection"] = None
        self._state[index] = controller_state

        self._logger.info(f'MockSwitchConnector: Created controller of type {controller_type} at index {index}. Adapter Path: {adapter_path} | Color Body: {colour_body} | Color Buttons: {colour_buttons} | Reconnect Address: {reconnect_address}')

        return index

    def get_controller_count(self)->int:
        return len(self._state)

    def remove_controller(self, controller_index)->None:

        self._logger.info(f'MockSwitchConnector: Removing controller at index {controller_index}...')

        if self.has_controller(controller_index):
            self._state.pop(controller_index)
            self._logger.info(f'MockSwitchConnector: Removed controller at index {controller_index}.')
        else:
            self._logger.error(f'MockSwitchConnector: Cannot remove controller at index {controller_index}. No controller found.')

    async def connect(self, controller_index)->bool:
        self._logger.info(f'MockSwitchConnector: Simulating connection of controller at index {controller_index}...')

        success = False

        if self.has_controller(controller_index):
            await asyncio.sleep(MockSwitchConnector.CONNECTION_TIME)
            self._state[controller_index]["state"] = MockSwitchConnector.CONTROLLER_STATE_CONNECTED
            self._state[controller_index]["last_connection"] = MockSwitchConnector.MOCK_SWITCH_ADDRESS
            self._logger.info('MockSwitchConnector: Controller connected.')
            success = True
        else:
            self._logger.error(f'MockSwitchConnector: No controller with index {controller_index} found.')
            success = False

        return success

    def has_controller(self, index)->bool:
        return (index in self._state)

    def get_available_adapters(self)->list[str]:
        return [ MockSwitchConnector.MOCK_ADAPTER_NAME ]

    def get_switch_addresses(self)->list[str]:
        return [ MockSwitchConnector.MOCK_SWITCH_ADDRESS ]

    def get_state(self)->dict:
        return self._state

    def clear_all_macros(self):
        self._logger.info('MockSwitchConnector: All macros cleared.')

    def clear_macros(self, controller_index):
        self._logger.info(f'MockSwitchConnector: Clearing macros for controller at index {controller_index}.')

        if self.has_controller(controller_index):
            self._logger.info(f'MockSwitchConnector: Macros cleared for controller {controller_index}.')
        else:
            self._logger.error(f'MockSwitchConnector: Cannot clear macros. No controller with index {controller_index} found.')

    async def macro(self, controller_index, macro: ChatNxMacro, block=False, callback: Callable[[str], None] = None)->str:
        self._logger.info(f'MockSwitchConnector: Trying to execute macro {macro} for controller at index {controller_index} (block: {block}).')

        macro_id = None

        if self.has_controller(controller_index):
            macro_id = os.urandom(24).hex()
            self._logger.info(f'MockSwitchConnector: Simulating execution of macro with ID {macro_id}...')

            duration = macro.total_duration()

            if block:
                await asyncio.sleep(duration)
                if callback:
                    callback(macro_id)
            elif callback:
                callback_task = asyncio.create_task(self._on_macro_finished(callback, duration, macro_id))

            self._logger.info('MockSwitchConnector: Macro executed.')
        else:
            self._logger.info(f'MockSwitchConnector: Cannot execute macro. Controller with index {controller_index} not found.')

        return macro_id

    async def _on_macro_finished(self, callback, duration, id):
        await asyncio.sleep(duration)
        callback(id)

    def stop_macro(self, controller_index, macro_id, block=False)->None:
        self._logger.info(f'MockSwitchConnector: Stopping macro with id {macro_id} for controller {controller_index}.')

        if self.has_controller(controller_index):
            self._logger.info('MockSwitchConnector: Macro stopped.')
        else:
            self._logger.error(f'MockSwitchConnector: Cannot stop macro {macro_id}. No controller with index {controller_index} found.')      