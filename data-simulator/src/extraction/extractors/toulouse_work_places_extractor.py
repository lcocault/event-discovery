"""Extractor for work places (shop/office) in Toulouse from OSM PBF data."""

import logging
from typing import Dict, Optional
from simulation.models.location import LocationType
from .toulouse_base_extractor import ToulouseBaseExtractor


class ToulouseWorkPlaceExtractor(ToulouseBaseExtractor):
    """OSM handler for extracting work places (shop/office) in Toulouse."""

    def __init__(self):
        """Initialize the work places extractor."""
        super().__init__("work_places")
        # Work place mappings
        self.shop_mappings = True  # All shop values
        self.office_mappings = True  # All office values

    def _get_location_type_from_tags(
        self, tags: Dict[str, str]
    ) -> Optional[LocationType]:
        """Extract work place type from OSM tags."""
        if "shop" in tags:
            return LocationType.WORK_PLACE
        if "office" in tags:
            return LocationType.WORK_PLACE
        return None

    def _might_contain_venues(self, tags: Dict[str, str]) -> bool:
        """Check if way might contain work places."""
        return "shop" in tags or "office" in tags
