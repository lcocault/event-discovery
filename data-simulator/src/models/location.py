"""Location classes for representing geographic points of interest."""

import uuid
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


class LocationType(Enum):
    # Religious venues
    CHURCH = "church"  # Place of worship (amenity=place_of_worship)
    """Enumeration for different types of locations."""

    # Educational institutions
    SCHOOL = "school"  # Primary school (école primaire)
    COLLEGE = "college"  # Middle school (collège)
    LYCEE = "lycee"  # High school (lycée)
    UNIVERSITY = "university"  # University
    KINDERGARTEN = "kindergarten"  # Kindergarten (maternelle)
    VOCATIONAL_SCHOOL = "vocational_school"  # Professional school

    # Hospitality venues
    BAR = "bar"  # Bar
    CAFE = "cafe"  # Café
    PUB = "pub"  # Pub
    RESTAURANT = "restaurant"  # Restaurant
    NIGHTCLUB = "nightclub"  # Night club
    BIERGARTEN = "biergarten"  # Beer garden

    # Entertainment venues
    CINEMA = "cinema"  # Cinema, movie theater
    THEATRE = "theatre"  # Theater, theatrical venue
    MUSIC_VENUE = "music_venue"  # Concert hall, music venue
    ARTS_CENTRE = "arts_centre"  # Arts center, cultural center
    EVENTS_VENUE = "events_venue"  # Events venue, conference center
    COMMUNITY_CENTRE = "community_centre"  # Community center
    EXHIBITION_CENTRE = "exhibition_centre"  # Exhibition center, museum

    # Work places
    WORK_PLACE = "work_place"  # Shop or office (work place)


@dataclass
class Position:
    """Represents a geographic position with latitude and longitude."""

    latitude: float
    longitude: float

    def __str__(self) -> str:
        """Return string representation of the position."""
        return f"({self.latitude:.6f}, {self.longitude:.6f})"


@dataclass
class OpeningHours:
    """Represents opening hours information."""

    raw_hours: Optional[str] = None  # Raw OSM opening_hours string
    is_always_open: bool = False


@dataclass
class Location:
    """Represents a real-world location (venue, institution, etc)."""

    id: Optional[str] = None
    name: Optional[str] = None
    location_type: Optional[LocationType] = None
    position: Optional[Position] = None
    opening_hours: Optional[OpeningHours] = None
    additional_info: Dict[str, Any] = field(default_factory=dict)
