from ..ChatNxCommand import *
from .QueueStatus import *

from abc import ABC, abstractmethod
import asyncio

class ChatNxQueueReceiverClientBase(ABC):
    """Abstraction of a ChatNx Queue Receiver app client."""

    @abstractmethod
    def connect(self)->bool:
        pass

    @abstractmethod
    def is_connected(self)->bool:
        pass

    @abstractmethod
    def disconnect(self)->None:
        pass

    @abstractmethod
    def enqueue(self, command: ChatNxCommand)->bool:
        pass

    @abstractmethod
    def set_complete(self, command_id: str)->bool:
        pass

    @abstractmethod
    def clear_queue(self)->bool:
        pass

    @abstractmethod
    async def fetch_status(self)->QueueStatus:
        pass

