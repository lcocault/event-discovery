"""Extractor for hospitality venues in Toulouse from OSM PBF data."""

import logging
from typing import Dict, Optional
from models.location import LocationType
from .toulouse_base_extractor import ToulouseBaseExtractor


class ToulouseHospitalityExtractor(ToulouseBaseExtractor):
    """OSM handler for extracting hospitality venues in Toulouse."""
    
    def __init__(self):
        """Initialize the hospitality venues extractor."""
        super().__init__('hospitality')
        
        # Hospitality venue mappings
        self.amenity_mappings = {
            'bar': LocationType.BAR,
            'cafe': LocationType.CAFE,
            'pub': LocationType.PUB,
            'restaurant': LocationType.RESTAURANT,
            'nightclub': LocationType.NIGHTCLUB,
            'biergarten': LocationType.BIERGARTEN,
            'fast_food': LocationType.RESTAURANT,  # Include fast food as restaurant
        }
        
        # Additional cuisine/bar type mappings for French venues
        self.additional_mappings = {
            'cuisine': {
                'coffee_shop': LocationType.CAFE,
                'wine_bar': LocationType.BAR,
                'cocktail_bar': LocationType.BAR,
                'beer': LocationType.PUB,
                'tapas': LocationType.BAR,
            }
        }
    
    def _get_location_type_from_tags(self, tags: Dict[str, str]) -> Optional[LocationType]:
        """Extract hospitality venue type from OSM tags."""
        # Check amenity tags first
        if 'amenity' in tags and tags['amenity'] in self.amenity_mappings:
            return self.amenity_mappings[tags['amenity']]
        
        # Check cuisine for additional mappings
        if 'cuisine' in tags and tags['cuisine'] in self.additional_mappings['cuisine']:
            return self.additional_mappings['cuisine'][tags['cuisine']]
        
        return None
    
    def _might_contain_venues(self, tags: Dict[str, str]) -> bool:
        """Check if way might contain hospitality venues."""
        return (
            'amenity' in tags and tags['amenity'] in self.amenity_mappings or
            'cuisine' in tags and tags['cuisine'] in self.additional_mappings['cuisine']
        )