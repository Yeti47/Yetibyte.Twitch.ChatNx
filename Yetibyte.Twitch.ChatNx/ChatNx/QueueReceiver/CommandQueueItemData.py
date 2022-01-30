from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json

@dataclass_json
@dataclass
class CommandQueueItemData:
    """Data Transfer Object that encapsulates data of a command queue item."""

    id: str = field(metadata=config(field_name='Id'))
    user_name: str = field(metadata=config(field_name='UserName'),default='')
    user_color_hex: str = field(metadata=config(field_name='UserColorHex'),default='')
    command: str = field(metadata=config(field_name='Command'),default='')