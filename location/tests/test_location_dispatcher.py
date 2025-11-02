import pytest
from location.location_dispatcher import LocationDispatcher
from location.location import Coordinates, Location
from api.stubs.location.models import Location as JsonLocation
from fastapi import HTTPException


class FakeRepository:
    def get_location(self, location_id: str):
        if location_id == "valid_id":
            return Location(
                id="valid_id",
                name="Test Location",
                type="workplace",
                position=Coordinates(latitude=42.0, longitude=1.5),
            )
        return None


@pytest.mark.asyncio
async def test_get_locations_location_id_found():
    # GIVEN: A dispatcher with a fake repository returning a valid location
    repository = FakeRepository()
    dispatcher = LocationDispatcher(repository)

    # WHEN: The method is called with a valid location ID
    location_id = "valid_id"
    result = await dispatcher.get_locations_location_id(location_id)

    # THEN: The result should be a JsonLocation with matching details
    assert result.id == "valid_id"
    assert result.name == "Test Location"


@pytest.mark.asyncio
async def test_get_locations_location_id_not_found():
    # GIVEN: A dispatcher with a fake repository returning None
    repository = FakeRepository()
    dispatcher = LocationDispatcher(repository)

    # WHEN: The method is called with an invalid location ID
    location_id = "invalid_id"

    # THEN: An HTTPException should be raised
    with pytest.raises(HTTPException) as context:
        await dispatcher.get_locations_location_id(location_id)
    assert context.value.status_code == 404
    assert context.value.detail == "Location with ID invalid_id not found"
