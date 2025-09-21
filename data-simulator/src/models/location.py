"""Location classes for representing geographic points of interest."""

import uuid
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass


class LocationType(Enum):
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
    notes: Optional[str] = None
    
    def __str__(self) -> str:
        """Return string representation of opening hours."""
        if self.is_always_open:
            return "Always open"
        elif self.raw_hours:
            return self.raw_hours
        else:
            return "Hours not specified"


class Location:
    """Represents a geographic location with position, type, and opening hours."""
    
    def __init__(
        self,
        name: str,
        position: Position,
        location_type: LocationType,
        opening_hours: Optional[OpeningHours] = None,
        osm_id: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None,
        location_id: Optional[str] = None
    ):
        """
        Initialize a Location instance.
        
        Args:
            name: Name of the location
            position: Geographic position (Position object)
            location_type: Type of location (LocationType enum)
            opening_hours: Opening hours information (OpeningHours object)
            osm_id: Original OSM ID if extracted from OSM data
            additional_info: Additional metadata from OSM tags
            location_id: Optional location identifier. If not provided, a UUID will be generated.
        """
        self.location_id = location_id or str(uuid.uuid4())
        self.name = name
        self.position = position
        self.location_type = location_type
        self.opening_hours = opening_hours or OpeningHours()
        self.osm_id = osm_id
        self.additional_info = additional_info or {}
    
    def __str__(self) -> str:
        """Return string representation of the location."""
        return f"Location(name='{self.name}', type={self.location_type.value}, position={self.position})"
    
    def __repr__(self) -> str:
        """Return detailed string representation of the location."""
        return (f"Location(id='{self.location_id}', name='{self.name}', "
                f"type={self.location_type}, position={self.position}, "
                f"hours={self.opening_hours}, osm_id={self.osm_id})")
    
    def __eq__(self, other) -> bool:
        """Check equality based on location_id."""
        if not isinstance(other, Location):
            return False
        return self.location_id == other.location_id
    
    def __hash__(self) -> int:
        """Return hash based on location_id."""
        return hash(self.location_id)
    
    @property
    def coordinates(self) -> tuple[float, float]:
        """Return coordinates as (latitude, longitude) tuple."""
        return (self.position.latitude, self.position.longitude)
    
    def distance_to(self, other_position: Position) -> float:
        """
        Calculate approximate distance to another position in kilometers.
        Uses simple Euclidean distance (not great circle distance).
        """
        lat_diff = self.position.latitude - other_position.latitude
        lon_diff = self.position.longitude - other_position.longitude
        # Rough conversion: 1 degree ≈ 111 km
        return ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111