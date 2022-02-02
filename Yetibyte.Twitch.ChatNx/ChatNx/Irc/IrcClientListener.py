from .IrcMessage import *

from abc import ABC, abstractmethod

class IrcClientListener(ABC):

    @abstractmethod
    def on_message_received(self, message: IrcMessage)->None:
        pass

    @abstractmethod
    def on_sending_message(self, message: str)->None:
        pass

    @abstractmethod
    def on_message_sent(self, message: str)->None:
        pass