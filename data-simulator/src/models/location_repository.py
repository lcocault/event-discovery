# placeholder for location_repository.py"""Location repository for managing collections of locations."""


import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Set, Union
from collections import defaultdict

from .location import Location, LocationType, Position, OpeningHours


class LocationRepository:
    def add_locations_from_geojson(self, filepath: str) -> None:
        """
        Load locations from a GeoJSON file and add them to the repository.
        Args:
            filepath: Path to the GeoJSON file
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        features = data.get("features", [])
        for feature in features:
            props = feature.get("properties", {})
            coords = feature.get("geometry", {}).get("coordinates", [None, None])
            lat = coords[1]
            lon = coords[0]
            name = props.get("name", "Unnamed")
            location_type_str = props.get("location_type", None)
            try:
                location_type = (
                    LocationType(location_type_str) if location_type_str else None
                )
            except Exception:
                location_type = None
            opening_hours = props.get("opening_hours", None)
            # Use OpeningHours if present and not 'Hours not specified'
            oh_obj = None
            if opening_hours and opening_hours != "Hours not specified":
                oh_obj = OpeningHours(raw_hours=opening_hours)
            position = Position(latitude=lat, longitude=lon)
            location_id = props.get("id")
            # Remove known fields from additional_info
            additional_info = {
                k: v
                for k, v in props.items()
                if k not in {"id", "name", "location_type", "opening_hours", "osm_id"}
            }
            if not isinstance(additional_info, dict):
                additional_info = {}
            location = Location(
                id=location_id,
                name=name,
                position=position,
                location_type=location_type,
                opening_hours=oh_obj,
                additional_info=additional_info,
            )
            self.add_location(location)

    @staticmethod
    def infer_location_type_from_tags(tags: dict) -> Optional[LocationType]:
        # Map OSM tags to LocationType
        if tags.get("amenity") == "place_of_worship":
            return LocationType.CHURCH
        # ...existing mapping logic for other types...
        return None

    """Repository for managing and querying collections of locations."""

    def __init__(self):
        """Initialize an empty location repository."""
        self._locations: Dict[str, Location] = {}
        self._locations_by_type: Dict[LocationType, Set[str]] = defaultdict(set)
        self._locations_by_name: Dict[str, Set[str]] = defaultdict(set)

    def add_location(self, location: Location) -> None:
        """
        Add a location to the repository.

        Args:
            location: Location to add
        """
        if location.id is not None and location.id not in self._locations:
            self._locations[location.id] = location
            if location.location_type is not None and location.id is not None:
                self._locations_by_type[location.location_type].add(location.id)
            if location.name and location.id is not None:
                self._locations_by_name[location.name.lower()].add(location.id)

    def add_locations(self, locations: List[Location]) -> None:
        """
        Add multiple locations to the repository.

        Args:
            locations: List of Location objects to add
        """
        for location in locations:
            self.add_location(location)

    def clear(self) -> None:
        """Clear all locations from the repository."""
        self._locations.clear()
        self._locations_by_type.clear()
        self._locations_by_name.clear()

    def get_location(self, location_id: str) -> Optional[Location]:
        """
        Get a location by its ID.

        Args:
            location_id: ID of the location to retrieve

        Returns:
            Location object or None if not found
        """
        return self._locations.get(location_id)

    def get_all_locations(self) -> List[Location]:
        """
        Get all locations in the repository.

        Returns:
            List of all Location objects
        """
        return list(self._locations.values())

    def get_locations_by_type(self, location_type: LocationType) -> List[Location]:
        """
        Get all locations of a specific type.

        Args:
            location_type: Type of locations to retrieve

        Returns:
            List of Location objects of the specified type
        """
        location_ids = self._locations_by_type.get(location_type, set())
        return [
            self._locations[location_id]
            for location_id in location_ids
            if location_id in self._locations
        ]

    def search_locations_by_name(
        self, name: str, case_sensitive: bool = False
    ) -> List[Location]:
        """
        Search locations by name (supports partial matches).

        Args:
            name: Name to search for
            case_sensitive: Whether to perform case-sensitive search

        Returns:
            List of Location objects matching the search criteria
        """
        search_name = name if case_sensitive else name.lower()
        matching_locations = []

        for stored_name, location_ids in self._locations_by_name.items():
            compare_name = stored_name if case_sensitive else stored_name.lower()
            if search_name in compare_name:
                for location_id in location_ids:
                    matching_locations.append(self._locations[location_id])

        return matching_locations

    def get_locations_within_radius(
        self, center_lat: float, center_lon: float, radius_km: float
    ) -> List[Location]:
        """
        Get locations within a specified radius of a center point.

        Args:
            center_lat: Latitude of the center point
            center_lon: Longitude of the center point
            radius_km: Radius in kilometers

        Returns:
            List of Location objects within the specified radius
        """
        matching_locations = []

        from math import radians, sin, cos, sqrt, atan2

        def haversine(lat1, lon1, lat2, lon2):
            R = 6371.0
            dlat = radians(lat2 - lat1)
            dlon = radians(lon2 - lon1)
            a = (
                sin(dlat / 2) ** 2
                + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
            )
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            return R * c

        for location in self._locations.values():
            if location.position is not None:
                distance = haversine(
                    center_lat,
                    center_lon,
                    location.position.latitude,
                    location.position.longitude,
                )
                if distance <= radius_km:
                    matching_locations.append(location)

        return matching_locations

    def get_statistics(self) -> Dict[str, object]:
        """
        Get statistics about the locations in the repository.

        Returns:
            Dictionary with total venues and breakdown by category
        """
        total_venues = len(self._locations)
        venue_breakdown = {}
        for location_type, location_ids in self._locations_by_type.items():
            venue_breakdown[location_type.value] = len(location_ids)
        return {
            "total_venues": total_venues,
            "venue_breakdown": venue_breakdown
        }

    def get_bounds(self) -> Dict[str, float]:
        """
        Get the geographic bounds of all locations.

        Returns:
            Dictionary with min/max latitude and longitude
        """
        if not self._locations:
            return {"min_lat": 0.0, "max_lat": 0.0, "min_lon": 0.0, "max_lon": 0.0}

        positions = [
            loc.position for loc in self._locations.values() if loc.position is not None
        ]
        if not positions:
            return {"min_lat": 0.0, "max_lat": 0.0, "min_lon": 0.0, "max_lon": 0.0}
        return {
            "min_lat": min(pos.latitude for pos in positions),
            "max_lat": max(pos.latitude for pos in positions),
            "min_lon": min(pos.longitude for pos in positions),
            "max_lon": max(pos.longitude for pos in positions),
        }

    def to_geojson(self) -> Dict:
        """
        Export all locations as a GeoJSON FeatureCollection.

        Returns:
            GeoJSON-formatted dictionary
        """
        features = []

        for location in self._locations.values():
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        location.position.longitude if location.position else None,
                        location.position.latitude if location.position else None,
                    ],
                },
                "properties": {
                    "id": location.id,
                    "name": location.name,
                    "location_type": location.location_type.value
                    if location.location_type
                    else None,
                    "opening_hours": str(location.opening_hours)
                    if location.opening_hours
                    else None,
                },
            }

            # Add additional info if available
            if isinstance(location.additional_info, dict) and location.additional_info:
                feature["properties"].update(location.additional_info)

            features.append(feature)

        return {"type": "FeatureCollection", "features": features}

    def __len__(self) -> int:
        """Return the number of locations in the repository."""
        return len(self._locations)

    def __repr__(self) -> str:
        """Return detailed string representation of the repository."""
        return f"LocationRepository(locations={len(self._locations)})"
