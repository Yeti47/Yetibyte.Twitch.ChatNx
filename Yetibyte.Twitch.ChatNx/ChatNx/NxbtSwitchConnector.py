from .SwitchConnector import *
from .Configuration.ChatNxMacro import *

import logging
import os
import asyncio

if os.name.lower() != 'nt':
    import nxbt

class NxbtSwitchConnector(SwitchConnector):
    """Implementation of a SwitchConnector that uses NXBT to communicate with a Nintendo Switch console."""

    def __init__(self, connection_timeout: float = 30.0, logger: logging.Logger = None):
        self._connection_timeout = connection_timeout
        self._logger = logger or logging.Logger("__NONE__")
        self._nxbt = None
        self._is_initialized = False

    def is_initialized(self)->bool:
        return self._is_initialized

    def initialize(self)->bool:

        self._logger.info(f'NxbtSwitchConnector: Initializing...')

        if self.is_initialized():
            self._logger.error(f'NxbtSwitchConnector: Already initialized.')
            return False

        try:
            self._nxbt = nxbt.Nxbt()
        except Exception as ex:
            self._logger.error(f'NxbtSwitchConnector: Failed to initialized NXBT. Details: {ex}')
            return False

        self._is_initialized = True

        self._logger.info(f'NxbtSwitchConnector: Initialization successful.')

        return True

    def reinitialize(self):
        self._is_initialized = False
        return self.initialize()

    async def connect(self, controller_index)->bool:
        self._logger.info(f'NxbtSwitchConnector: Connecting controller {controller_index}...')

        if not self.is_initialized():
            self._logger.error(f'NxbtSwitchConnector: Switch connector not initialized. Cannot connect.')
            return False

        try:
            await asyncio.wait_for(self._wait_for_connection(controller_index), timeout=self._connection_timeout)
        except asyncio.TimeoutError as tex:
            self._logger.error(f'NxbtSwitchConnector: Connection timeout ({self._connection_timeout})!')
            return False
        except Exception as ex:
            self._logger.error(f'NxbtSwitchConnector: An error occurred while trying to connect controller {controller_index}.')
            return False

        self._logger.info(f'NxbtSwitchConnector: Controller {controller_index} connected successfully!')

        return True

    async def _wait_for_connection(self, controller_index)->None:
        #self._nxbt.wait_for_connection(controller_index)
        while not self.is_controller_connected(controller_index):
            await asyncio.sleep(0.1)

    def create_controller(self, controller_type, adapter_path=None, colour_body=None, colour_buttons=None, reconnect_address=None)->int:
        self._logger.info(f'NxbtSwitchConnector: Creating controller...')

        if not self.is_initialized():
            self._logger.error(f'NxbtSwitchConnector: Switch connector not initialized. Cannot create controller.')
            return -1

        nxbt_controller_type = nxbt.PRO_CONTROLLER

        controller_id = -1

        if controller_type == ControllerTypes.JOYCON_L:
            nxbt_controller_type = nxbt.JOYCON_L
        elif controller_type == ControllerTypes.JOYCON_R:
            nxbt_controller_type = nxbt.JOYCON_R 

        try:
            controller_id = self._nxbt.create_controller(
                nxbt_controller_type, 
                adapter_path=adapter_path, 
                colour_body=colour_body,
                colour_buttons=colour_buttons,
                reconnect_address=reconnect_address)
        except Exception as ex:
            self._logger.error(f'NxbtSwitchConnector: Error creating controller. Details: {ex}')
            return -1

        self._logger.info(f'NxbtSwitchConnector: Created controller with index {controller_id}.')

        return controller_id

    def get_state(self)->dict:
        return self._nxbt.state if self._nxbt else {}
    
    def get_available_adapters(self)->list[str]:
        return self._nxbt.get_available_adapters() if self._nxbt else []

    def get_switch_addresses(self)->list[str]:
        return self._nxbt.get_switch_addresses() if self._nxbt else []

    def get_controller_count(self)->int:
        return self._nxbt._controller_counter if self._nxbt else 0

    async def macro(self, controller_index, macro: ChatNxMacro, block=False, callback=None)->str:
        self._logger.info(f'NxbtSwitchConnector: Trying to dispatch macro for controller {controller_index}...')

        if not self.is_initialized():
            self._logger.error(f'NxbtSwitchConnector: Switch connector not initialized. Cannot dispatch macro.')
            return ''

        if not self.is_controller_connected(controller_index):
            self._logger.error(f'NxbtSwitchConnector: Cannot dispatch macro. Controller {controller_index} not connected.')
            return ''

        macro_id = ''

        macro_text = macro.build()
        macro_duration = macro.total_duration()

        self._logger.info(f'NxbtSwitchConnector: Dispatching macro. Total duration: {macro_duration}s')

        try:
            macro_id = self._nxbt.macro(controller_index, macro_text, block=block)

            if callback:
                if block:
                    callback(macro_id)
                else:
                    callback_task = asyncio.create_task(self._wait_for_macro_completion(callback, macro_id, controller_index))


        except Exception as ex:
            self._logger.error(f'NxbtSwitchConnector: Error dispatching macro. Details: {ex}')
            return ''
        
        self._logger.info(f'NxbtSwitchConnector: Macro with ID {macro_id} dispatched successfully!')

        return macro_id

    async def _wait_for_macro_completion(self, callback, macro_id, controller_index):

        while True:

            if not self.is_initialized() or not self.is_controller_connected(controller_index):
                break

            state = self.get_state()
            finished_macros = state[controller_index].get("finished_macros", [])

            if macro_id in finished_macros:
                callback(macro_id)
                break

            await asyncio.sleep(0.01)

    def stop_macro(self, controller_index, macro_id, block=False)->None:
        self._logger.info(f'NxbtSwitchConnector: Trying to stop macro {macro_id} for controller {controller_index}...')

        if not self.is_initialized():
            self._logger.error(f'NxbtSwitchConnector: Switch connector not initialized. Cannot stop macro.')
            return

        if not self.is_controller_connected(controller_index):
            self._logger.error(f'NxbtSwitchConnector: Cannot stop macro. Controller {controller_index} not connected.')
            return

        try:
            self._nxbt.stop_macro(controller_index, macro_id, block=block)
        except Exception as ex:
            self._logger.error(f'NxbtSwitchConnector: Error stopping macro. Details: {ex}')
            return
        
        self._logger.info(f'NxbtSwitchConnector: Macro with ID {macro_id} stopped!')

    def remove_controller(self, controller_index):
        self._logger.info(f'NxbtSwitchConnector: Removing controller {controller_index}...')

        if not self.is_initialized():
            self._logger.error(f'NxbtSwitchConnector: Switch connector not initialized. Cannot remove controller.')
            return

        try:
            self._nxbt.remove_controller(controller_index)
        except Exception as ex:
            pass

        self._logger.info(f'NxbtSwitchConnector: Controller {controller_index} removed.')

    def clear_macros(self, controller_index):
        self._logger.info(f'NxbtSwitchConnector: Clearing macros for controller {controller_index}...')

        if not self.is_initialized():
            self._logger.error(f'NxbtSwitchConnector: Switch connector not initialized. Cannot clear macros.')
            return

        success = False

        try:
            self._nxbt.clear_macros(controller_index)
            success = True
        except Exception as ex:
            self._logger.error(f'NxbtSwitchConnector: Switch connector not initialized. Cannot clear macros.')

        if success:
            self._logger.info(f'NxbtSwitchConnector: Macros cleared successfully.')

    def clear_all_macros(self):
        self._logger.info(f'NxbtSwitchConnector: Clearing all macros...')

        if not self.is_initialized():
            self._logger.error(f'NxbtSwitchConnector: Switch connector not initialized. Cannot clear macros.')
            return

        for i in range(self.get_controller_count() - 1):
            self.clear_macros(i)

