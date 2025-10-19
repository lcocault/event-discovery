"""Dispatcher of the REST API calls to the location service."""

from api.stubs.location.models import Location as JsonLocation
from location.location import Location
from location.location_repository import LocationRepository

from fastapi import HTTPException


class LocationDispatcher:
    """Dispatcher of the REST API calls to the location service."""

    def __init__(self, repository: LocationRepository) -> None:
        """Initialize the dispatcher."""
        self.repository = repository

    async def get_locations_location_id(self, location_id: str) -> JsonLocation:
        """Get location by ID."""
        location : Location | None = self.repository.get_location(location_id)
        if location is None:
            raise HTTPException(status_code=404, detail=f"Location with ID {location_id} not found")
        return JsonLocation(
            id=location.id,
            name=location.name,
            latitude=location.position.latitude,
            longitude=location.position.longitude,
        )
