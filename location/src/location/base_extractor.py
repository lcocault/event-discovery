"""
Base extractor class for Toulouse OSM data processing.

This module provides a common base class for all Toulouse-specific extractors,
eliminating code duplication and providing consistent functionality.
"""

import logging
import osmium
from typing import Dict, List, Optional, Any, Set
from abc import ABC, abstractmethod
from .location import Location, LocationType, Coordinates, OpeningHours
from .location_repository import LocationRepository


class BaseExtractor(osmium.SimpleHandler, ABC):
    def _get_category_from_location_type(self, location_type: LocationType) -> str:
        """Map LocationType to original extractor category."""
        if location_type == LocationType.CHURCH:
            return "church"
        elif location_type in [
            LocationType.SCHOOL,
            LocationType.COLLEGE,
            LocationType.LYCEE,
            LocationType.UNIVERSITY,
            LocationType.KINDERGARTEN,
            LocationType.VOCATIONAL_SCHOOL,
        ]:
            return "educational"
        elif location_type in [
            LocationType.BAR,
            LocationType.CAFE,
            LocationType.PUB,
            LocationType.RESTAURANT,
            LocationType.NIGHTCLUB,
            LocationType.BIERGARTEN,
        ]:
            return "hospitality"
        elif location_type in [
            LocationType.CINEMA,
            LocationType.THEATRE,
            LocationType.MUSIC_VENUE,
            LocationType.ARTS_CENTRE,
            LocationType.EVENTS_VENUE,
            LocationType.COMMUNITY_CENTRE,
            LocationType.EXHIBITION_CENTRE,
        ]:
            return "entertainment"
        elif location_type == LocationType.WORK_PLACE:
            return "work"
        else:
            return "other"

    """
    Base class for OSM extractors focused on Toulouse venues.

    Provides common functionality for geographic filtering, statistics tracking,
    location creation, and OSM data processing.
    """

    def __init__(self, extractor_type: str):
        """
        Initialize the base extractor.

        Args:
            extractor_type: Type of extractor (e.g., 'educational', 'hospitality', 'entertainment')
        """
        osmium.SimpleHandler.__init__(self)
        self.extractor_type = extractor_type
        self.repository = LocationRepository()

        # Toulouse approximate bounds (for performance filtering)
        self.min_lat = 43.55
        self.max_lat = 43.65
        self.min_lon = 1.35
        self.max_lon = 1.50

        # Statistics tracking
        self.processed_nodes = 0
        self.processed_ways = 0
        self.found_venues = 0

        # Subclasses should define their specific mappings
        self.amenity_mappings: Dict[str, LocationType] = {}
        self.building_mappings: Dict[str, LocationType] = {}
        self.leisure_mappings: Dict[str, LocationType] = {}
        self.tourism_mappings: Dict[str, LocationType] = {}
        self.additional_mappings: Dict[str, Dict[str, LocationType]] = {}

        logging.info(f"Initialized {self.__class__.__name__}")

    def _is_in_toulouse(self, lat: float, lon: float) -> bool:
        """Check if coordinates are within Toulouse bounds."""
        return (
            self.min_lat <= lat <= self.max_lat and self.min_lon <= lon <= self.max_lon
        )

    def _extract_name(self, tags: Dict[str, str]) -> Optional[str]:
        """Extract venue name from OSM tags with fallback hierarchy."""
        if "name" in tags:
            return tags["name"]
        elif "name:fr" in tags:
            return tags["name:fr"]
        elif "name:en" in tags:
            return tags["name:en"]
        elif "operator" in tags:
            return tags["operator"]
        elif "brand" in tags:
            return tags["brand"]
        return None

    def _extract_opening_hours(self, tags: Dict[str, str]) -> Optional[OpeningHours]:
        """Extract opening hours information from OSM tags."""
        if "opening_hours" in tags:
            raw_hours = tags["opening_hours"]
            is_always_open = raw_hours.lower() in ["24/7", "always"]

            return OpeningHours(
                raw_hours=raw_hours,
                is_always_open=is_always_open,
                notes=tags.get("opening_hours:note"),
            )
        return None

    def _extract_additional_info(self, tags: Dict[str, str]) -> Dict[str, Any]:
        """Extract additional information from OSM tags."""
        additional_info = {}

        # Address information
        if "addr:full" in tags:
            additional_info["address"] = tags["addr:full"]
        else:
            address_parts = []
            if "addr:housenumber" in tags:
                address_parts.append(tags["addr:housenumber"])
            if "addr:street" in tags:
                address_parts.append(tags["addr:street"])
            if address_parts:
                additional_info["address"] = " ".join(address_parts)

        # Location details
        for field in ["addr:city", "addr:postcode", "phone", "website", "email"]:
            if field in tags:
                key = field.replace("addr:", "").replace(":", "_")
                additional_info[key] = tags[field]

        # Accessibility
        if "wheelchair" in tags:
            additional_info["wheelchair_accessible"] = tags["wheelchair"] == "yes"

        # Other useful tags
        for field in ["description", "operator", "brand", "cuisine", "internet_access"]:
            if field in tags:
                additional_info[field] = tags[field]

        return additional_info

    @abstractmethod
    def _get_location_type_from_tags(
        self, tags: Dict[str, str]
    ) -> Optional[LocationType]:
        """
        Extract location type from OSM tags.

        This method must be implemented by subclasses to define their specific
        mapping logic from OSM tags to LocationType.

        Args:
            tags: OSM tags dictionary

        Returns:
            LocationType if venue matches extractor criteria, None otherwise
        """
        pass

    def _create_location(
        self, tags: Dict[str, str], lat: float, lon: float, osm_id: str = None
    ) -> bool:
        """
        Create a Location object from OSM data.

        Args:
            tags: OSM tags dictionary
            lat: Latitude coordinate
            lon: Longitude coordinate
            osm_id: OSM ID for reference

        Returns:
            True if location was created successfully, False otherwise
        """
        # Get location type from subclass implementation
        location_type = self._get_location_type_from_tags(tags)

        if not location_type:
            return False

        # Extract venue information
        name = self._extract_name(tags)
        opening_hours = self._extract_opening_hours(tags)
        additional_info = self._extract_additional_info(tags)

        if osm_id:
            additional_info["osm_id"] = osm_id

        # Add original extractor category
        additional_info["category"] = self._get_category_from_location_type(
            location_type
        )

        try:
            location = Location(
                id=osm_id,  # Ensure id is set for repository storage
                name=name or f"Unnamed {location_type.value}",
                position=Coordinates(latitude=lat, longitude=lon),
                location_type=location_type,
                opening_hours=opening_hours,
                additional_info=additional_info,
            )

            self.repository.add_location(location)
            self.found_venues += 1

            # Determine source type for logging
            source = None
            if osm_id:
                if str(osm_id).startswith("node/"):
                    source = "node"
                elif str(osm_id).startswith("way/"):
                    source = "way"
            else:
                source = "unknown"

            logging.info(
                f"Added {location_type.value} from {source}: {name or 'Unnamed'} at ({lat:.6f}, {lon:.6f})"
            )
            return True

        except (ValueError, TypeError) as e:
            logging.warning(f"Failed to create location at ({lat}, {lon}): {e}")
            return False

    def node(self, n):
        """Process OSM nodes (points of interest)."""
        self.processed_nodes += 1

        if self.processed_nodes % 1000000 == 0:
            logging.info(
                f"Processed {self.processed_nodes:,} nodes, found {self.found_venues} venues"
            )

        # Check if node has location data
        if not hasattr(n, "location") or not n.location.valid():
            return

        lat = n.location.lat
        lon = n.location.lon

        # Store node location for way processing
        if not hasattr(self, "node_locations"):
            self.node_locations = {}
        self.node_locations[n.id] = (lat, lon)

        # Filter by Toulouse bounds for performance
        if not self._is_in_toulouse(lat, lon):
            return

        # Convert tags to dictionary
        tags = {tag.k: tag.v for tag in n.tags}

        # Try to create location
        self._create_location(tags, lat, lon, f"node/{n.id}")

    def way(self, w):
        """Process OSM ways (areas and buildings). Now enabled for venue extraction."""
        self.processed_ways += 1

        if self.processed_ways % 1000000 == 0:
            logging.info(
                f"Processed {self.processed_ways:,} ways, found {self.found_venues} venues"
            )

        if not hasattr(w, "nodes") or len(w.nodes) == 0:
            return

        # Use the first node's id to get its position from the node_locations dict
        lat = None
        lon = None
        for node in w.nodes:
            node_id = node.ref if hasattr(node, "ref") else getattr(node, "id", None)
            if (
                node_id is not None
                and hasattr(self, "node_locations")
                and node_id in self.node_locations
            ):
                lat, lon = self.node_locations[node_id]
                break
        if lat is None or lon is None:
            return
        # Filter by Toulouse bounds for performance
        if not self._is_in_toulouse(lat, lon):
            return
        tags = {tag.k: tag.v for tag in w.tags}
        # Try to create location
        self._create_location(tags, lat, lon, f"way/{w.id}")

    def _might_contain_venues(self, tags: Dict[str, str]) -> bool:
        """
        Quick check if way might contain venues relevant to this extractor.

        Subclasses can override this for more specific filtering.
        """
        # Check common venue-related tags
        venue_tags = {"amenity", "building", "leisure", "tourism", "landuse"}
        return any(tag in tags for tag in venue_tags)

    def get_statistics(self) -> Dict:
        """Get comprehensive extraction statistics."""
        stats = {
            "extractor_type": self.extractor_type,
            "processed_nodes": self.processed_nodes,
            "processed_ways": self.processed_ways,
            "total_venues": len(self.repository),
            "venue_breakdown": {},
        }

        # Ensure venue_breakdown is a dictionary and count venues by type
        venue_breakdown = {}
        for location in self.repository.get_all_locations():
            venue_type = location.location_type.value
            venue_breakdown[venue_type] = venue_breakdown.get(venue_type, 0) + 1
        stats["venue_breakdown"] = venue_breakdown

        return stats

    def get_repository(self) -> LocationRepository:
        """Get the location repository with all extracted venues."""
        return self.repository
