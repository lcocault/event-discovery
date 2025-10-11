"""Extractor for churches in Toulouse from OSM PBF data."""

import logging
from typing import Dict, Optional
from simulation.models.location import LocationType
from .toulouse_base_extractor import ToulouseBaseExtractor


class ToulouseChurchExtractor(ToulouseBaseExtractor):
    """OSM handler for extracting churches in Toulouse."""

    def __init__(self):
        """Initialize the churches extractor."""
        super().__init__("church")

        # Church mappings
        self.amenity_mappings = {
            "place_of_worship": LocationType.CHURCH,
        }

        # French church keywords for name-based detection
        self.name_keywords = {
            "église": LocationType.CHURCH,
            "eglise": LocationType.CHURCH,
            "temple": LocationType.CHURCH,
            "mosquée": LocationType.CHURCH,
        }

    def _get_location_type_from_tags(
        self, tags: Dict[str, str]
    ) -> Optional[LocationType]:
        """Extract churches venue type from OSM tags."""
        # Check amenity tags first
        if "amenity" in tags and tags["amenity"] in self.amenity_mappings:
            return self.amenity_mappings[tags["amenity"]]

        return None

    def _might_contain_venues(self, tags: Dict[str, str]) -> bool:
        """Check if way might contain churches venues."""
        # Check for amenity tags
        if "amenity" in tags and tags["amenity"] in self.amenity_mappings:
            return True

        # Check name for churches keywords
        name = self._extract_name(tags)
        if name:
            name_lower = name.lower()
            return any(keyword in name_lower for keyword in self.name_keywords.keys())

        return False
