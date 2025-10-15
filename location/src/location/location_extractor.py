"""Extractor for all locations of interest in Toulouse from OSM PBF data."""

import logging
from typing import Dict, Optional
from .location import LocationType
from .base_extractor import BaseExtractor


class LocationExtractor(BaseExtractor):
    """OSM handler for extracting all locations of interest in Toulouse."""

    def __init__(self):
        super().__init__("unified")

        # Amenity mappings for all categories
        self.amenity_mappings = {
            # Churches
            "place_of_worship": LocationType.CHURCH,
            # Educational
            "school": LocationType.SCHOOL,
            "college": LocationType.COLLEGE,
            "university": LocationType.UNIVERSITY,
            "kindergarten": LocationType.KINDERGARTEN,
            # Hospitality
            "bar": LocationType.BAR,
            "cafe": LocationType.CAFE,
            "pub": LocationType.PUB,
            "restaurant": LocationType.RESTAURANT,
            "nightclub": LocationType.NIGHTCLUB,
            "biergarten": LocationType.BIERGARTEN,
            "fast_food": LocationType.RESTAURANT,
            # Entertainment
            "cinema": LocationType.CINEMA,
            "theatre": LocationType.THEATRE,
            "theater": LocationType.THEATRE,
            "music_venue": LocationType.MUSIC_VENUE,
            "concert_hall": LocationType.MUSIC_VENUE,
            "arts_centre": LocationType.ARTS_CENTRE,
            "arts_center": LocationType.ARTS_CENTRE,
            "cultural_centre": LocationType.ARTS_CENTRE,
            "cultural_center": LocationType.ARTS_CENTRE,
            "events_venue": LocationType.EVENTS_VENUE,
            "conference_centre": LocationType.EVENTS_VENUE,
            "conference_center": LocationType.EVENTS_VENUE,
            "convention_center": LocationType.EVENTS_VENUE,
            "convention_centre": LocationType.EVENTS_VENUE,
            "community_centre": LocationType.COMMUNITY_CENTRE,
            "community_center": LocationType.COMMUNITY_CENTRE,
            "social_centre": LocationType.COMMUNITY_CENTRE,
            "social_center": LocationType.COMMUNITY_CENTRE,
            "exhibition_centre": LocationType.EXHIBITION_CENTRE,
            "exhibition_center": LocationType.EXHIBITION_CENTRE,
            "museum": LocationType.EXHIBITION_CENTRE,
            "gallery": LocationType.EXHIBITION_CENTRE,
            "planetarium": LocationType.EXHIBITION_CENTRE,
        }

        self.building_mappings = {
            "theatre": LocationType.THEATRE,
            "theater": LocationType.THEATRE,
            "cinema": LocationType.CINEMA,
            "museum": LocationType.EXHIBITION_CENTRE,
            "concert_hall": LocationType.MUSIC_VENUE,
        }

        self.leisure_mappings = {
            "dance": LocationType.MUSIC_VENUE,
            "adult_gaming_centre": LocationType.EVENTS_VENUE,
            "escape_game": LocationType.EVENTS_VENUE,
        }

        self.tourism_mappings = {
            "museum": LocationType.EXHIBITION_CENTRE,
            "gallery": LocationType.EXHIBITION_CENTRE,
            "theatre": LocationType.THEATRE,
            "attraction": LocationType.EVENTS_VENUE,
        }

        self.additional_mappings = {
            "cuisine": {
                "coffee_shop": LocationType.CAFE,
                "wine_bar": LocationType.BAR,
                "cocktail_bar": LocationType.BAR,
                "beer": LocationType.PUB,
                "tapas": LocationType.BAR,
            }
        }

        # Name-based detection for churches and educational
        self.name_keywords = {
            # Churches
            "église": LocationType.CHURCH,
            "eglise": LocationType.CHURCH,
            "temple": LocationType.CHURCH,
            "mosquée": LocationType.CHURCH,
            # Educational
            "école": LocationType.SCHOOL,
            "ecole": LocationType.SCHOOL,
            "collège": LocationType.COLLEGE,
            "college": LocationType.COLLEGE,
            "lycée": LocationType.LYCEE,
            "lycee": LocationType.LYCEE,
            "université": LocationType.UNIVERSITY,
            "universite": LocationType.UNIVERSITY,
            "maternelle": LocationType.KINDERGARTEN,
        }

    def _get_location_type_from_tags(
        self, tags: Dict[str, str]
    ) -> Optional[LocationType]:
        # Amenity
        if "amenity" in tags and tags["amenity"] in self.amenity_mappings:
            return self.amenity_mappings[tags["amenity"]]
        # Building
        if "building" in tags and tags["building"] in self.building_mappings:
            return self.building_mappings[tags["building"]]
        # Leisure
        if "leisure" in tags and tags["leisure"] in self.leisure_mappings:
            return self.leisure_mappings[tags["leisure"]]
        # Tourism
        if "tourism" in tags and tags["tourism"] in self.tourism_mappings:
            return self.tourism_mappings[tags["tourism"]]
        # Additional (cuisine)
        if "cuisine" in tags and tags["cuisine"] in self.additional_mappings["cuisine"]:
            return self.additional_mappings["cuisine"][tags["cuisine"]]
        # Work places
        if "shop" in tags or "office" in tags:
            return LocationType.WORK_PLACE
        # Name-based detection
        name = self._extract_name(tags)
        if name:
            name_lower = name.lower()
            for keyword, location_type in self.name_keywords.items():
                if keyword in name_lower:
                    return location_type
        return None

    def _might_contain_venues(self, tags: Dict[str, str]) -> bool:
        # Check all relevant tags
        return (
            ("amenity" in tags and tags["amenity"] in self.amenity_mappings)
            or ("building" in tags and tags["building"] in self.building_mappings)
            or ("leisure" in tags and tags["leisure"] in self.leisure_mappings)
            or ("tourism" in tags and tags["tourism"] in self.tourism_mappings)
            or (
                "cuisine" in tags
                and tags["cuisine"] in self.additional_mappings["cuisine"]
            )
            or ("shop" in tags)
            or ("office" in tags)
            or (
                self._extract_name(tags)
                and any(
                    keyword in self._extract_name(tags).lower()
                    for keyword in self.name_keywords
                )
            )
        )
