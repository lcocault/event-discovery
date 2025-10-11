from dataclasses import dataclass
from .location import Position


@dataclass
class Event:
    person_id: str
    day_in_year: int  # 1-366
    day_in_week: int  # 0=Monday, 6=Sunday
    time_slot: int  # 0-23 (hour of day)
    location: Position  # Geographic position of the event
