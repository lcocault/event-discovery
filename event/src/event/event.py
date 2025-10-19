"""Event domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import uuid


@dataclass
class LocationRef:
    latitude: float
    longitude: float


@dataclass
class Event:
    """Represents an event taking place at a location/time."""

    id: str
    name: str
    latitude: float
    longitude: float
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def create(name: str, latitude: float, longitude: float, **kwargs) -> "Event":
        return Event(id=str(uuid.uuid4()), name=name, latitude=latitude, longitude=longitude, **kwargs)
