"""Extractor for educational institutions in Toulouse from OSM PBF data."""

import logging
from typing import Dict, Optional
from models.location import LocationType
from .toulouse_base_extractor import ToulouseBaseExtractor


class ToulouseEducationalExtractor(ToulouseBaseExtractor):
    """OSM handler for extracting educational institutions in Toulouse."""
    
    def __init__(self):
        """Initialize the educational institutions extractor."""
        super().__init__('educational')
        
        # Educational institution mappings
        self.amenity_mappings = {
            'school': LocationType.SCHOOL,
            'college': LocationType.COLLEGE,
            'university': LocationType.UNIVERSITY,
            'kindergarten': LocationType.KINDERGARTEN,
        }
        
        # French educational keywords for name-based detection
        self.name_keywords = {
            'école': LocationType.SCHOOL,
            'ecole': LocationType.SCHOOL,
            'collège': LocationType.COLLEGE,
            'college': LocationType.COLLEGE,
            'lycée': LocationType.LYCEE,
            'lycee': LocationType.LYCEE,
            'université': LocationType.UNIVERSITY,
            'universite': LocationType.UNIVERSITY,
            'maternelle': LocationType.KINDERGARTEN,
        }
    
    def _get_location_type_from_tags(self, tags: Dict[str, str]) -> Optional[LocationType]:
        """Extract educational venue type from OSM tags."""
        # Check amenity tags first
        if 'amenity' in tags and tags['amenity'] in self.amenity_mappings:
            return self.amenity_mappings[tags['amenity']]
        
        # Check name for French educational keywords
        name = self._extract_name(tags)
        if name:
            name_lower = name.lower()
            for keyword, location_type in self.name_keywords.items():
                if keyword in name_lower:
                    return location_type
        
        return None
    
    def _might_contain_venues(self, tags: Dict[str, str]) -> bool:
        """Check if way might contain educational venues."""
        # Check for amenity tags
        if 'amenity' in tags and tags['amenity'] in self.amenity_mappings:
            return True
        
        # Check name for educational keywords
        name = self._extract_name(tags)
        if name:
            name_lower = name.lower()
            return any(keyword in name_lower for keyword in self.name_keywords.keys())
        
        return False