"""Extractor for entertainment venues in Toulouse from OSM PBF data."""

import logging
from typing import Dict, Optional
from models.location import LocationType
from .toulouse_base_extractor import ToulouseBaseExtractor


class ToulouseEntertainmentExtractor(ToulouseBaseExtractor):
    """OSM handler for extracting entertainment venues in Toulouse."""
    
    def __init__(self):
        """Initialize the entertainment venues extractor."""
        super().__init__('entertainment')
        
        # OSM amenity mappings to LocationType
        self.amenity_mappings = {
            'cinema': LocationType.CINEMA,
            'theatre': LocationType.THEATRE,
            'theater': LocationType.THEATRE,
            'music_venue': LocationType.MUSIC_VENUE,
            'concert_hall': LocationType.MUSIC_VENUE,
            'arts_centre': LocationType.ARTS_CENTRE,
            'arts_center': LocationType.ARTS_CENTRE,
            'cultural_centre': LocationType.ARTS_CENTRE,
            'cultural_center': LocationType.ARTS_CENTRE,
            'events_venue': LocationType.EVENTS_VENUE,
            'conference_centre': LocationType.EVENTS_VENUE,
            'conference_center': LocationType.EVENTS_VENUE,
            'convention_center': LocationType.EVENTS_VENUE,
            'convention_centre': LocationType.EVENTS_VENUE,
            'community_centre': LocationType.COMMUNITY_CENTRE,
            'community_center': LocationType.COMMUNITY_CENTRE,
            'social_centre': LocationType.COMMUNITY_CENTRE,
            'social_center': LocationType.COMMUNITY_CENTRE,
            'exhibition_centre': LocationType.EXHIBITION_CENTRE,
            'exhibition_center': LocationType.EXHIBITION_CENTRE,
            'museum': LocationType.EXHIBITION_CENTRE,
            'gallery': LocationType.EXHIBITION_CENTRE,
            'planetarium': LocationType.EXHIBITION_CENTRE,
        }
        
        # Building type mappings
        self.building_mappings = {
            'theatre': LocationType.THEATRE,
            'theater': LocationType.THEATRE,
            'cinema': LocationType.CINEMA,
            'museum': LocationType.EXHIBITION_CENTRE,
            'concert_hall': LocationType.MUSIC_VENUE,
        }
        
        # Leisure mappings
        self.leisure_mappings = {
            'dance': LocationType.MUSIC_VENUE,
            'adult_gaming_centre': LocationType.EVENTS_VENUE,
            'escape_game': LocationType.EVENTS_VENUE,
        }
        
        # Tourism mappings
        self.tourism_mappings = {
            'museum': LocationType.EXHIBITION_CENTRE,
            'gallery': LocationType.EXHIBITION_CENTRE,
            'theatre': LocationType.THEATRE,
            'attraction': LocationType.EVENTS_VENUE,
        }
    
    def _get_location_type_from_tags(self, tags: Dict[str, str]) -> Optional[LocationType]:
        """Extract entertainment venue type from OSM tags."""
        # Check amenity tags first
        if 'amenity' in tags and tags['amenity'] in self.amenity_mappings:
            return self.amenity_mappings[tags['amenity']]
        
        # Check building tags
        if 'building' in tags and tags['building'] in self.building_mappings:
            return self.building_mappings[tags['building']]
        
        # Check leisure tags
        if 'leisure' in tags and tags['leisure'] in self.leisure_mappings:
            return self.leisure_mappings[tags['leisure']]
        
        # Check tourism tags
        if 'tourism' in tags and tags['tourism'] in self.tourism_mappings:
            return self.tourism_mappings[tags['tourism']]
        
        return None
    
    def _might_contain_venues(self, tags: Dict[str, str]) -> bool:
        """Check if way might contain entertainment venues."""
        return (
            any(tag in tags for tag in ['amenity', 'building', 'leisure', 'tourism']) and
            (tags.get('amenity') in self.amenity_mappings or
             tags.get('building') in self.building_mappings or
             tags.get('leisure') in self.leisure_mappings or
             tags.get('tourism') in self.tourism_mappings)
        )
