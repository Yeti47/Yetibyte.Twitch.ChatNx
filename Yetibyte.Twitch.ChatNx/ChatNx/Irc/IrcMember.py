
class IrcMemberMeta(type):
    """Serves as an interface for objects that describe a member of an IRC."""

    EXPECTED_MEMBERS = [
        "id",
        "name",
        "display_name",
        "color",
        "is_subscriber",
        "is_mod"
    ]

    def __instancecheck__(self, instance):
        return self.__subclasscheck__(type(instance))

    def __subclasscheck__(self, subclass):
        return all(hasattr(subclass, m) for m in IrcMemberMeta.EXPECTED_MEMBERS)


class IrcMember(object, metaclass=IrcMemberMeta):
    """Describes a user that participates in an IRC."""

    def __init__(self, name: str, color: str, is_sub = False, is_mod = False, display_name: str = None):
        self._name = name
        self._color = color
        self._is_sub = is_sub
        self._is_mod = is_mod
        self._display_name = display_name or name

    @property
    def name(self)->str:
        return self._name

    @property
    def display_name(self)->str:
        return self._display_name

    @property
    def id(self)->str:
        return self._name

    @property
    def color(self)->str:
        return self._color

    @property
    def is_mod(self)->bool:
        return self._is_mod

    @property
    def is_subscriber(self)->bool:
        return self._is_sub

