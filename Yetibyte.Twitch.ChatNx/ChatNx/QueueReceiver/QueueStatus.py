from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json

@dataclass_json
@dataclass
class QueueStatus:
    """Data Transfer Object that encapsulates the current state of the queue in a ChatNx queue receiver application."""

    queue_item_count: int = field(metadata=config(field_name='QueueItemCount'))
    history_item_count: int = field(metadata=config(field_name='HistoryItemCount'))
    queue_item_ids: list[str] = field(metadata=config(field_name='QueueItemIds'))
    