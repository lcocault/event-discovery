"""
Family Location Assignment System

This module handles assigning geographic locations to families:
- Random home positions within Toulouse bounds
- Nearest schools for children based on age
- Random work locations for adults
"""

import random
import math
import json
from typing import List, Tuple, Dict, Optional
from pathlib import Path

from models.family import Family
from models.person import Person
from location import Location, LocationType, Coordinates


class LocationAssigner:
    """Handles assignment of home, school, and work locations for families."""

    # Toulouse bounds (expanded slightly for residential areas)
    TOULOUSE_BOUNDS = {
        "min_lat": 43.55,
        "max_lat": 43.65,
        "min_lon": 1.35,
        "max_lon": 1.50,
    }

    # Age ranges for different school types
    SCHOOL_AGE_MAPPING = {
        LocationType.KINDERGARTEN: (3, 5),  # Kindergarten: 3-5 years
        LocationType.SCHOOL: (6, 10),  # Primary school: 6-10 years
        LocationType.COLLEGE: (11, 14),  # Middle school: 11-14 years
        LocationType.LYCEE: (15, 17),  # High school: 15-17 years
        LocationType.UNIVERSITY: (18, 25),  # University: 18-25 years
    }

    # Employment rates by gender
    EMPLOYMENT_RATES = {
        "male": 0.80,  # 80% employment rate for men
        "female": 0.70,  # 70% employment rate for women
    }

    def __init__(self, unified_geojson_path: str):
        """
        Initialize the location assigner with a unified locations GeoJSON file.

        Args:
            unified_geojson_path: Path to unified locations GeoJSON
        """
        self.all_locations = self._load_all_locations(unified_geojson_path)

        # Filter and group locations by type
        self.educational_locations = [
            loc
            for loc in self.all_locations
            if loc.location_type
            in [
                LocationType.KINDERGARTEN,
                LocationType.SCHOOL,
                LocationType.COLLEGE,
                LocationType.LYCEE,
                LocationType.UNIVERSITY,
            ]
        ]
        self.work_locations = [
            loc
            for loc in self.all_locations
            if loc.location_type
            in [
                LocationType.RESTAURANT,
                LocationType.BAR,
                LocationType.CAFE,
                LocationType.WORK_PLACE,
            ]
        ]

        # Group educational locations by type for efficient lookup
        self.schools_by_type: Dict[LocationType, List[Location]] = {}
        self._group_schools_by_type()

    def _load_all_locations(self, geojson_path: str) -> List[Location]:
        """Load all locations from a unified GeoJSON file."""
        locations = []
        with open(geojson_path, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)

        for feature in geojson_data["features"]:
            coords = feature["geometry"]["coordinates"]
            props = feature["properties"]

            # Convert location type string to enum
            location_type_str = props.get("location_type", "").lower()
            try:
                if location_type_str == "school":
                    location_type = LocationType.SCHOOL
                elif location_type_str == "college":
                    location_type = LocationType.COLLEGE
                elif location_type_str == "lycee":
                    location_type = LocationType.LYCEE
                elif location_type_str == "university":
                    location_type = LocationType.UNIVERSITY
                elif location_type_str == "kindergarten":
                    location_type = LocationType.KINDERGARTEN
                elif location_type_str == "restaurant":
                    location_type = LocationType.RESTAURANT
                elif location_type_str == "bar":
                    location_type = LocationType.BAR
                elif location_type_str == "cafe":
                    location_type = LocationType.CAFE
                elif location_type_str == "work_place":
                    location_type = LocationType.WORK_PLACE
                else:
                    continue  # Skip unknown types

                location = Location(
                    name=props.get("name", "Unnamed"),
                    location_type=location_type,
                    position=Coordinates(coords[1], coords[0]),  # GeoJSON is [lon, lat]
                    additional_info=props,
                )
                locations.append(location)

            except (KeyError, ValueError):
                continue  # Skip invalid entries

        return locations

    # _load_work_locations is now obsolete and removed.

    def _group_schools_by_type(self):
        """Group educational locations by type for efficient lookup."""
        for location in self.educational_locations:
            if location.location_type not in self.schools_by_type:
                self.schools_by_type[location.location_type] = []
            self.schools_by_type[location.location_type].append(location)

    def generate_random_home_position(self) -> Coordinates:
        """Generate a random home position within Toulouse bounds."""
        lat = random.uniform(
            self.TOULOUSE_BOUNDS["min_lat"], self.TOULOUSE_BOUNDS["max_lat"]
        )
        lon = random.uniform(
            self.TOULOUSE_BOUNDS["min_lon"], self.TOULOUSE_BOUNDS["max_lon"]
        )
        return Coordinates(lat, lon)

    @staticmethod
    def calculate_distance(pos1: Coordinates, pos2: Coordinates) -> float:
        """Calculate distance between two positions using Haversine formula."""
        # Convert to radians
        lat1, lon1 = math.radians(pos1.latitude), math.radians(pos1.longitude)
        lat2, lon2 = math.radians(pos2.latitude), math.radians(pos2.longitude)

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        # Earth's radius in kilometers
        earth_radius_km = 6371.0
        return earth_radius_km * c

    def get_school_type_for_age(self, age: int) -> Optional[LocationType]:
        """Determine appropriate school type based on child's age."""
        for school_type, (min_age, max_age) in self.SCHOOL_AGE_MAPPING.items():
            if min_age <= age <= max_age:
                return school_type
        return None

    def find_nearest_school(
        self, home_position: Coordinates, child_age: int
    ) -> Optional[Location]:
        """Find the nearest school appropriate for the child's age."""
        school_type = self.get_school_type_for_age(child_age)
        if not school_type or school_type not in self.schools_by_type:
            return None

        available_schools = self.schools_by_type[school_type]
        if not available_schools:
            return None

        # Find the nearest school
        nearest_school = None
        min_distance = float("inf")

        for school in available_schools:
            distance = LocationAssigner.calculate_distance(
                home_position, school.position
            )
            if distance < min_distance:
                min_distance = distance
                nearest_school = school

        return nearest_school

    def assign_random_work_location(self, person: Person) -> Optional[Location]:
        """
        Assign a random work location based on employment rates.

        Args:
            person: The person to assign work to

        Returns:
            Location if employed, None if unemployed based on employment rates
        """
        if not self.work_locations:
            return None

        # Check if person should be employed based on gender employment rates
        gender_str = person.gender.value.lower()  # Convert Gender enum to string
        employment_rate = self.EMPLOYMENT_RATES.get(
            gender_str, 0.75
        )  # Default 75% if gender not found

        # Random employment decision based on employment rate
        if random.random() > employment_rate:
            return None  # Person is unemployed

        # Person is employed - assign random work location
        return random.choice(self.work_locations)

    def assign_locations_to_family(self, family: Family) -> Dict[str, any]:
        """
        Assign home, school, and work locations directly to family and person objects.

        This method modifies the family and person objects in place by setting:
        - family.home_position
        - person.school_location for children
        - person.work_location for employed adults

        Returns a dictionary with assignment statistics for reporting.
        """
        # Generate random home position and assign to family
        home_position = self.generate_random_home_position()
        family.home_position = home_position

        # Find schools for children and assign directly to person objects
        children_assigned = 0
        for child in family.children:
            school = self.find_nearest_school(home_position, child.age)
            if school:
                child.school_location = school
                children_assigned += 1
            else:
                child.school_location = None

        # Assign work locations for adults based on employment rates
        adults_assigned = 0
        for adult in family.parents:
            work_location = self.assign_random_work_location(adult)
            if work_location:
                adult.work_location = work_location
                adults_assigned += 1
            else:
                adult.work_location = None

        # Return statistics for reporting
        return {
            "family_id": family.family_id,
            "home_position": home_position,
            "children_assigned_schools": children_assigned,
            "children_total": len(family.children),
            "adults_assigned_work": adults_assigned,
            "adults_total": len(family.parents),
        }

    def get_assignment_statistics(self, families: List[Family]) -> Dict:
        """Generate statistics about the location assignments from family objects directly."""
        stats = {
            "total_families": len(families),
            "children_with_schools": 0,
            "children_without_schools": 0,
            "adults_with_work": 0,
            "adults_without_work": 0,
            "school_distances": [],
            "work_distances": [],
            "school_type_distribution": {},
            "work_type_distribution": {},
        }

        for family in families:
            if not family.home_position:
                continue  # Skip families without home positions

            # Process children and their schools
            for child in family.children:
                if child.school_location:
                    stats["children_with_schools"] += 1

                    # Calculate distance from home to school
                    distance = LocationAssigner.calculate_distance(
                        family.home_position, child.school_location.position
                    )
                    stats["school_distances"].append(distance)

                    # Count school types
                    school_type = child.school_location.location_type.value
                    stats["school_type_distribution"][school_type] = (
                        stats["school_type_distribution"].get(school_type, 0) + 1
                    )
                else:
                    stats["children_without_schools"] += 1

            # Process adults and their work locations
            for adult in family.parents:
                if adult.work_location:
                    stats["adults_with_work"] += 1

                    # Calculate distance from home to work
                    distance = LocationAssigner.calculate_distance(
                        family.home_position, adult.work_location.position
                    )
                    stats["work_distances"].append(distance)

                    # Count work types
                    work_type = adult.work_location.location_type.value
                    stats["work_type_distribution"][work_type] = (
                        stats["work_type_distribution"].get(work_type, 0) + 1
                    )
                else:
                    stats["adults_without_work"] += 1

        # Calculate average distances
        if stats["school_distances"]:
            stats["avg_school_distance"] = round(
                sum(stats["school_distances"]) / len(stats["school_distances"]), 2
            )

        if stats["work_distances"]:
            stats["avg_work_distance"] = round(
                sum(stats["work_distances"]) / len(stats["work_distances"]), 2
            )

        return stats
