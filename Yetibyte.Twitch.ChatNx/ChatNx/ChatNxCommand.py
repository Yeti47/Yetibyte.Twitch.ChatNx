from .Irc.IrcMessage import IrcMessage

class ChatNxCommand(object):
    """Describes a command dispatched to and processable by a ChatNx client."""
    def __init__(self, id: str, command: str, irc_message: IrcMessage):
        self._id = id
        self._command = command
        self._irc_message = irc_message

    @property
    def id(self)->str:
        return self._id

    @property
    def command(self)->str:
        return self._command

    @property
    def irc_message(self)->IrcMessage:
        return self._irc_message


