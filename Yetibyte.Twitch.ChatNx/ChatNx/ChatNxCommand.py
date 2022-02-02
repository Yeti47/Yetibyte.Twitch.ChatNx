from .Irc.IrcMessage import IrcMessage
from .Configuration.ChatNxCommandSetup import *

class ChatNxCommand(object):
    """Describes a command dispatched to and processable by a ChatNx client."""
    def __init__(self, id: str, irc_message: IrcMessage, command_setup: ChatNxCommandSetup):
        self._id = id
        self._irc_message = irc_message
        self._command_setup = command_setup

    @property
    def id(self)->str:
        return self._id

    @property
    def command(self)->str:
        return self._command_setup.command

    @property
    def command_setup(self)->ChatNxCommandSetup:
        return self._command_setup

    @property
    def irc_message(self)->IrcMessage:
        return self._irc_message

    @property
    def timestamp(self):
        return self.irc_message.timestamp


