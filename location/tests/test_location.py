import pytest
from location.location import Location, LocationType, Coordinates


def test_location_initialization():
    # GIVEN: A location with specific attributes
    id = "loc_1"
    name = "Test Location"
    position = Coordinates(latitude=42.0, longitude=1.5)

    # WHEN: The location is initialized
    location = Location(
        id=id,
        name=name,
        type=LocationType.WORK_PLACE,
        position=position,
    )

    # THEN: The attributes should match the initialization values
    assert location.id == id
    assert location.name == name
    assert location.location_type == LocationType.WORK_PLACE
    assert location.latitude == position.latitude
    assert location.longitude == position.longitude
