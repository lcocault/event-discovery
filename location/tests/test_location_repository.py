import unittest

from location.location import Location, LocationType, Coordinates
from location.location_repository import LocationRepository


class TestLocationRepository(unittest.TestCase):
    def test_add_location(self):
        # GIVEN a LocationRepository instance and a Location object
        repo = LocationRepository()
        position = Coordinates(latitude=42.0, longitude=1.5)
        location = Location(
            id="123",
            name="Test Location",
            type=LocationType.WORK_PLACE,
            position=position,
        )
        # WHEN the location is added to the repository
        repo.add_location(location)
        # THEN the location should be present in the repository
        self.assertEqual(len(repo.get_all_locations()), 1)
        self.assertEqual(repo.get_all_locations()[0].name, "Test Location")


if __name__ == "__main__":
    unittest.main()
