import pytest
from location.location import Location, LocationType


def test_location_initialization():
    # GIVEN: A location with specific attributes
    id = "loc_1"
    name = "Test Location"
    latitude = 42.0
    longitude = 1.5

    # WHEN: The location is initialized
    location = Location(
        id=id,
        name=name,
        type=LocationType.WORK_PLACE,
        latitude=latitude,
        longitude=longitude,
    )

    # THEN: The attributes should match the initialization values
    assert location.id == id
    assert location.name == name
    assert location.location_type == LocationType.WORK_PLACE
    assert location.latitude == latitude
    assert location.longitude == longitude
