from abc import ABC, abstractmethod
from .IrcClientListener import *

class IrcClient(ABC):
    """Abstraction of an IRC client."""

    @property
    @abstractmethod
    def user_name(self)->str:
        pass

    @property
    @abstractmethod
    def channel_name(self)->str:
        pass

    @property
    @abstractmethod
    def auth_token(self)->str:
        pass

    @abstractmethod
    async def connect(self)->bool:
        pass

    @abstractmethod
    def is_connected(self)->bool:
        pass

    @abstractmethod
    async def send_message(self, content: str)->bool:
        pass

    @abstractmethod
    async def disconnect(self)->None:
        pass

    @abstractmethod
    def add_listener(self, listener: IrcClientListener)->None:
        pass

    @abstractmethod
    async def dispose(self)->None:
        pass

