"""Location repository for managing collections of locations."""

import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Set, Union
from collections import defaultdict

from models.location import Location, LocationType, Position, OpeningHours


class LocationRepository:
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
        if location.location_id not in self._locations:
            self._locations[location.location_id] = location
            self._locations_by_type[location.location_type].add(location.location_id)
            self._locations_by_name[location.name.lower()].add(location.location_id)
    
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
        return [self._locations[location_id] for location_id in location_ids]
    
    def search_locations_by_name(self, name: str, case_sensitive: bool = False) -> List[Location]:
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
    
    def get_locations_within_radius(self, center_lat: float, center_lon: float, 
                                   radius_km: float) -> List[Location]:
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
        
        for location in self._locations.values():
            distance = location.position.distance_to(center_lat, center_lon)
            if distance <= radius_km:
                matching_locations.append(location)
        
        return matching_locations
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get statistics about the locations in the repository.
        
        Returns:
            Dictionary with statistics about location counts by type
        """
        stats = {"total": len(self._locations)}
        
        for location_type, location_ids in self._locations_by_type.items():
            stats[location_type.value] = len(location_ids)
        
        return stats
    
    def get_bounds(self) -> Dict[str, float]:
        """
        Get the geographic bounds of all locations.
        
        Returns:
            Dictionary with min/max latitude and longitude
        """
        if not self._locations:
            return {"min_lat": 0.0, "max_lat": 0.0, "min_lon": 0.0, "max_lon": 0.0}
        
        positions = [loc.position for loc in self._locations.values()]
        
        return {
            "min_lat": min(pos.latitude for pos in positions),
            "max_lat": max(pos.latitude for pos in positions),
            "min_lon": min(pos.longitude for pos in positions),
            "max_lon": max(pos.longitude for pos in positions)
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
                    "coordinates": [location.position.longitude, location.position.latitude]
                },
                "properties": {
                    "id": location.location_id,
                    "name": location.name,
                    "location_type": location.location_type.value,
                    "opening_hours": str(location.opening_hours) if location.opening_hours else None,
                }
            }
            
            # Add additional info if available
            if hasattr(location, 'additional_info') and location.additional_info:
                feature["properties"].update(location.additional_info)
            
            features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
    
    def __len__(self) -> int:
        """Return the number of locations in the repository."""
        return len(self._locations)
    
    def __repr__(self) -> str:
        """Return detailed string representation of the repository."""
        return f"LocationRepository(locations={len(self._locations)})"
