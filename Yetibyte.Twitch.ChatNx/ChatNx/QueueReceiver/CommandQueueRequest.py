from .CommandQueueItemData import *

from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json

@dataclass_json
@dataclass
class CommandQueueRequest:
    """Data Transfer Object that encapsulates a request to a ChatNx queue receiver."""

    action: str = field(metadata=config(field_name='Action'))
    item_data: CommandQueueItemData = field(metadata=config(field_name='ItemData'))
    