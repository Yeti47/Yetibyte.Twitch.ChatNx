from .IrcMember import *

from datetime import datetime

class IrcMessageMeta(type):
    """Interface for objects that describe a message in an IRC."""

    EXPECTED_MEMBERS = [
        "id",
        "author",
        "channel",
        "content",
        "timestamp"
    ]

    def __instancecheck__(self, instance):
        return self.__subclasscheck__(type(instance))

    def __subclasscheck__(self, subclass):
        return all(hasattr(subclass, m) for m in IrcMessageMeta.EXPECTED_MEMBERS)

class IrcMessage(object, metaclass=IrcMessageMeta):
    """Describes a chat message in an IRC environment."""
    def __init__(self, id: str, author: IrcMember, channel: str, content: str, timestamp:datetime=None):
        self._id = id
        self._author = author
        self._channel = channel
        self._content = content
        self._timestamp = timestamp or datetime.now()

    @property
    def id(self)->str:
        return self._id

    @property
    def author(self)->IrcMember:
        return self._author

    @property
    def channel(self)->str:
        return self._channel

    @property
    def content(self)->str:
        return self._content

    @property
    def timestamp(self)->datetime:
        return self._timestamp




