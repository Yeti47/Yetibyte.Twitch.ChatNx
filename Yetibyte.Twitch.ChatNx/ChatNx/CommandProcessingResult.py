from dataclasses import dataclass

@dataclass(frozen=True)
class CommandProcessingResult(object):
    """Encapsulates the result of a command processing operation."""
    success: bool
    is_match: bool
    was_enqueued: bool
    shared_time_remaining: float
    time_remaining: float



