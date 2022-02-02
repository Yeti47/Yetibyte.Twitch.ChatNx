from abc import ABC, abstractmethod
from enum import Enum
from .Configuration.ChatNxMacro import *
import asyncio
from typing import Callable

class ControllerTypes(Enum):
    JOYCON_L = 1
    JOYCON_R = 2
    PRO_CONTROLLER = 3

class SwitchConnector(ABC):
    """Abstraction of an object that exposes an API to interact with a Nintendo Switch console."""

    @abstractmethod
    def initialize(self)->bool:
        pass

    @abstractmethod
    def get_controller_count(self)->int:
        pass

    @abstractmethod
    def reinitialize(self)->bool:
        pass

    @abstractmethod
    def create_controller(self, controller_type, adapter_path=None, colour_body=None, colour_buttons=None, reconnect_address=None)->int:
        pass

    @abstractmethod
    def remove_controller(self, controller_index)->None:
        pass

    @abstractmethod
    async def connect(self, controller_index)->bool:
        pass

    @abstractmethod
    def get_available_adapters(self)->list[str]:
        pass

    @abstractmethod
    def get_switch_addresses(self)->list[str]:
        pass

    @abstractmethod
    def get_state(self)->dict:
        pass

    @abstractmethod
    def is_initialized(self)->bool:
        pass

    @abstractmethod
    async def macro(self, controller_index, macro: ChatNxMacro, block=False, callback: Callable[[str], None] = None)->str:
        pass

    @abstractmethod
    def stop_macro(self, controller_index, macro_id, block=False)->None:
        pass

    @abstractmethod
    def clear_macros(self, controller_index)->None:
        pass

    @abstractmethod
    def clear_all_macros(self)->None:
        pass

    def is_controller_connected(self, controller_index)->bool:
        state = self.get_state()

        return controller_index in state and state[controller_index]["state"] == "connected"




