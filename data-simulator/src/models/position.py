from dataclasses import dataclass
from location import Coordinates


@dataclass
class Position:
    """Represents the spatio-temporal position of a person (formerly Event)."""

    person_id: str
    day_in_year: int  # 1-366
    day_in_week: int  # 0=Monday, 6=Sunday
    time_slot: int  # 0-23 (hour of day)
    location: Coordinates  # Geographic coordinates of the position

    """Represents the spatio-temporal position of a person (formerly Event)."""

    def __init__(
        self, person_id, day_in_year, day_in_week, time_slot, location: Coordinates
    ):
        self.person_id = person_id
        self.day_in_year = day_in_year
        self.day_in_week = day_in_week
        self.time_slot = time_slot
        self.location = location
