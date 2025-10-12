import os
import json
import logging
import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime, timedelta
from typing import List
from models.location_repository import LocationRepository
from models.family import Family
from models.person import Person

from models.location import LocationType, Coordinates
from models.position import Position

# Set up logger
logger = logging.getLogger("position_generator")
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


class PositionGenerator:
    """
    Generates daily activity positions for each member of a family over one year.
    """

    def __init__(self, families: List[Family], location_repository=None):
        self.families = families
        self.positions = []  # type: ignore
        self.location_repository = location_repository

    def generate_positions(self):
        start_date = datetime(datetime.now().year, 1, 6)  # Jan 6, 2025 is a Monday
        for day_offset in range(31):
            date = start_date + timedelta(days=day_offset)
            day_in_year = date.timetuple().tm_yday
            day_in_week = date.weekday()  # 0=Monday
            for family in self.families:
                for person in family.parents + family.children:
                    self._generate_base_positions(person, day_in_year, day_in_week)
                    self._generate_bar_positions(person, family, day_in_year, day_in_week)
                    self._generate_religious_positions(
                        person, family, day_in_year, day_in_week
                    )
                    self._generate_show_positions(person, family, day_in_year, day_in_week)

    def _generate_base_positions(self, person, day_in_year, day_in_week):
        for time_slot in range(24):
            coords = self._determine_location(person, day_in_week, time_slot)
            pos = Position(
                person_id=person.person_id,
                day_in_year=day_in_year,
                day_in_week=day_in_week,
                time_slot=time_slot,
                location=coords,
            )
            self.positions.append(pos)

    def _find_nearest_location(self, position, loc_type_str):
        if not self.location_repository or not position:
            return None
        # Map string to LocationType
        try:
            loc_type = getattr(LocationType, loc_type_str)
        except AttributeError:
            # Try lower-case match (for e.g. 'CHURCH' not in enum)
            loc_type = None
            for t in LocationType:
                if t.name == loc_type_str or t.value.upper() == loc_type_str.upper():
                    loc_type = t
                    break
        if not loc_type:
            return None
        # Find nearest location of this type
        candidates = self.location_repository.get_locations_by_type(loc_type)
        if not candidates:
            logger.debug(f"No candidates found for location type {loc_type_str}")
            return None

        # Find the closest by Euclidean distance
        def dist(loc):
            return (
                (loc.position.latitude - position.latitude) ** 2
                + (loc.position.longitude - position.longitude) ** 2
            ) ** 0.5

        nearest = min(candidates, key=dist)
        min_dist = dist(nearest)
        logger.debug(
            f"Nearest {loc_type_str} to ({position.latitude}, {position.longitude}) is '{getattr(nearest, 'name', None)}' at ({nearest.position.latitude}, {nearest.position.longitude}) with distance {min_dist:.4f} degrees (~{min_dist*111:.2f} km)"
        )
        return nearest

    def _generate_bar_positions(self, person, family, day_in_year, day_in_week):
        # Students aged 18+ go to nearest bar after school (assume after 16:00)
        # If you want to use social_category for bar logic, use family.social_category
        if person.is_student and person.is_adult:
            if day_in_week < 5:  # Mon-Fri
                bar = self._find_nearest_location(
                    person.school_location.position, "BAR"
                )
                if bar:
                    self.positions.append(
                        Position(
                            person_id=person.person_id,
                            day_in_year=day_in_year,
                            day_in_week=day_in_week,
                            time_slot=17,
                            location=bar.position,
                        )
                    )

    def _generate_religious_positions(self, person, family, day_in_year, day_in_week):
        import random

        religiosity = getattr(family, "religiosity", None)
        church = self._find_nearest_location(family.home_position, "CHURCH")
        if religiosity:
            if religiosity.name == "VERY_RELIGIOUS":
                # Weekdays + Saturday at 19:00
                if day_in_week < 6:
                    if church:
                        self.positions.append(
                            Position(
                                person_id=person.person_id,
                                day_in_year=day_in_year,
                                day_in_week=day_in_week,
                                time_slot=19,
                                location=church.position,
                            )
                        )
                # Sunday at 11:00
                if day_in_week == 6:
                    if church:
                        self.positions.append(
                            Position(
                                person_id=person.person_id,
                                day_in_year=day_in_year,
                                day_in_week=day_in_week,
                                time_slot=11,
                                location=church.position,
                            )
                        )
            elif religiosity.name == "MODERATE_RELIGIOUS":
                # Every Sunday at 11:00
                if day_in_week == 6 and church:
                    self.positions.append(
                        Position(
                            person_id=person.person_id,
                            day_in_year=day_in_year,
                            day_in_week=day_in_week,
                            time_slot=11,
                            location=church.position,
                        )
                    )
            elif religiosity.name == "OCCASIONAL_RELIGIOUS":
                # One Sunday out of 6
                if day_in_week == 6 and church:
                    if random.randint(1, 6) == 1:
                        self.positions.append(
                            Position(
                                person_id=person.person_id,
                                day_in_year=day_in_year,
                                day_in_week=day_in_week,
                                time_slot=11,
                                location=church.position,
                            )
                        )

    def _generate_show_positions(self, person, family, day_in_year, day_in_week):
        """
        Generate show (cinema, theatre, concert, etc.) events for a person based on their family's social category.
        Farmers = 0%, Artisans = 1%, Employees/Workers = 3%, Inactive/Retirees = 5%, Others = 10%.
        Retirees/Inactive can go anytime, others go in the evening (19-22).
        """
        import random
        from models.person import SocialCategory

        if not family or not family.social_category:
            return
        cat = family.social_category
        # Probabilities per day
        if cat == SocialCategory.FARMERS:
            prob = 0.0
        elif cat == SocialCategory.ARTISANS_MERCHANTS_ENTREPRENEURS:
            prob = 0.01
        elif cat in (SocialCategory.EMPLOYEES, SocialCategory.WORKERS):
            prob = 0.03
        elif cat in (SocialCategory.INACTIVE, SocialCategory.RETIREES):
            prob = 0.05
        else:
            prob = 0.10

    def _determine_location(self, person: Person, day_in_week: int, time_slot: int):
        # Always return a Coordinates object; fallback to home if needed
        coords = None
        # Night hours: 0-6, always at home
        if 0 <= time_slot <= 6:
            if person.family and person.family.home_position:
                coords = person.family.home_position
        # School hours: 8-16, Mon-Fri, children (age < 15)
        elif (
            person.age < 15
            and person.school_location
            and day_in_week < 5
            and 8 <= time_slot <= 16
        ):
            if getattr(person.school_location, "position", None):
                coords = person.school_location.position
        # Work hours: 8-17, Mon-Fri, adults (age >= 15)
        elif (
            person.age >= 15
            and person.work_location
            and day_in_week < 5
            and 8 <= time_slot <= 17
        ):
            if getattr(person.work_location, "position", None):
                coords = person.work_location.position
        # Otherwise, home
        elif person.family and person.family.home_position:
            coords = person.family.home_position
        # Fallback: always use home position if nothing else
        if coords is None and person.family and person.family.home_position:
            coords = person.family.home_position
        return coords

    def save_positions(self, path: str):
        # Save positions to GeoParquet using geopandas
        records = []
        geometries = []
        for position in self.positions:
            if position.location:
                geometry = Point(position.location.longitude, position.location.latitude)
            else:
                geometry = None
            record = {
                "person_id": position.person_id,
                "day_in_year": position.day_in_year,
                "day_in_week": position.day_in_week,
                "time_slot": position.time_slot,
            }
            records.append(record)
            geometries.append(geometry)
        import pandas as pd

        df = pd.DataFrame(records)
        gdf = gpd.GeoDataFrame(df, geometry=geometries, crs="EPSG:4326")
        gdf.to_parquet(path, engine="pyarrow")


# --- Utility function to load families ---
def load_families(path):
    from models.family import Family

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    families = []
    for fam in data:
        family = Family(
            religiosity=None,  # Will be set below
            family_id=fam.get("family_id"),
            home_position=None,
        )
        # Set religiosity if present
        relig = fam.get("religiosity")
        if relig:
            from models.person import Religiosity

            try:
                family.religiosity = Religiosity(relig.upper())
            except Exception:
                family.religiosity = Religiosity[relig.upper()]
        # Set home position
        pos = fam.get("home_position")
        if pos:
            family.home_position = Coordinates(
                latitude=pos["latitude"], longitude=pos["longitude"]
            )
        # Parents and children are not reconstructed in detail (not needed for event gen)
        family.parents = []
        family.children = []
        families.append(family)
    return families



    def _determine_location(self, person: Person, day_in_week: int, time_slot: int):
    # Always return a Coordinates object; fallback to home if needed
        pos = None
        # Night hours: 0-6, always at home
        if 0 <= time_slot <= 6:
            if person.family and person.family.home_position:
                pos = person.family.home_position
        # School hours: 8-16, Mon-Fri, children
        elif (
            person.is_child
            and person.school_location
            and day_in_week < 5
            and 8 <= time_slot <= 16
        ):
            if getattr(person.school_location, "position", None):
                pos = person.school_location.position
        # Work hours: 8-17, Mon-Fri, adults
        elif (
            person.is_adult
            and person.work_location
            and day_in_week < 5
            and 8 <= time_slot <= 17
        ):
            if getattr(person.work_location, "position", None):
                pos = person.work_location.position
        # Otherwise, home
        elif person.family and person.family.home_position:
            pos = person.family.home_position
        # Fallback: always use home position if nothing else
        if pos is None and person.family and person.family.home_position:
            pos = person.family.home_position
        return pos

    def save_positions(self, path: str):
        # Save positions to GeoParquet using geopandas
        records = []
        for position in self.positions:
            if position.location:
                geometry = Point(position.location.longitude, position.location.latitude)
            else:
                geometry = None
            records.append(
                {
                    "person_id": position.person_id,
                    "day_in_year": position.day_in_year,
                    "day_in_week": position.day_in_week,
                    "time_slot": position.time_slot,
                    "geometry": geometry,
                }
            )
        gdf = gpd.GeoDataFrame(records, geometry="geometry", crs="EPSG:4326")
        gdf.to_parquet(path, engine="pyarrow")


# --- Script entry point ---
if __name__ == "__main__":
    import sys
    import os
    from models.family import Family
    from models.location_repository import LocationRepository
    from models.person import Person
    from simulation.family_generator import FamilyGenerator

    # Load families
    families_path = "data/families.json"
    if not os.path.exists(families_path):
        logger.error(f"Family file not found: {families_path}")
        sys.exit(1)
    generator = FamilyGenerator()
    families = generator.load_families(families_path)

    # Load locations
    data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    unified_geojson = os.path.join(data_dir, "toulouse_locations_of_interest.geojson")
    location_repo = LocationRepository()
    if os.path.exists(unified_geojson):
        location_repo.add_locations_from_geojson(unified_geojson)
    else:
        logger.warning(f"{unified_geojson} not found.")

    # Debug: print number of locations loaded for each type
    logger.debug("Locations loaded by type:")
    from models.location import LocationType

    for loc_type in LocationType:
        count = len(location_repo.get_locations_by_type(loc_type))
    logger.debug(f"  {loc_type.name}: {count}")

    # Generate and save positions
    position_generator = PositionGenerator(families, location_repository=location_repo)
    logger.info("Generating positions...")
    position_generator.generate_positions()
    output_path = "data/positions.parquet"
    logger.info(f"Saving positions to {output_path} ...")
    position_generator.save_positions(output_path)
    logger.info(f"✓ Positions saved to {output_path}")

    """
    Generates daily activity positions for each member of a family over one year.
    """

    def __init__(self, families: List[Family], location_repository=None):
        self.families = families
        self.location_repository = location_repository

    def generate_positions(self):
        start_date = datetime(datetime.now().year, 1, 6)  # Jan 6, 2025 is a Monday
        for day_offset in range(31):
            date = start_date + timedelta(days=day_offset)
            day_in_year = date.timetuple().tm_yday
            day_in_week = date.weekday()  # 0=Monday
            for family in self.families:
                for person in family.parents + family.children:
                    self._generate_base_positions(person, day_in_year, day_in_week)
                    self._generate_bar_positions(person, family, day_in_year, day_in_week)
                    self._generate_religious_positions(
                        person, family, day_in_year, day_in_week
                    )
                    self._generate_show_positions(person, family, day_in_year, day_in_week)

    def _generate_base_positions(self, person, day_in_year, day_in_week):
        for time_slot in range(24):
            location = self._determine_location(person, day_in_week, time_slot)
            position = Position(
                person_id=person.person_id,
                day_in_year=day_in_year,
                day_in_week=day_in_week,
                time_slot=time_slot,
                location=location,
            )
            self.positions.append(position)

    def _find_nearest_location(self, position, loc_type_str):
        if not self.location_repository or not position:
            return None
        # Map string to LocationType
        try:
            loc_type = getattr(LocationType, loc_type_str)
        except AttributeError:
            # Try lower-case match (for e.g. 'CHURCH' not in enum)
            loc_type = None
            for t in LocationType:
                if t.name == loc_type_str or t.value.upper() == loc_type_str.upper():
                    loc_type = t
                    break
        if not loc_type:
            return None
        # Find nearest location of this type
        candidates = self.location_repository.get_locations_by_type(loc_type)
        if not candidates:
            print(f"[DEBUG] No candidates found for location type {loc_type_str}")
            return None

        # Find the closest by Euclidean distance
        def dist(loc):
            return (
                (loc.position.latitude - position.latitude) ** 2
                + (loc.position.longitude - position.longitude) ** 2
            ) ** 0.5

        nearest = min(candidates, key=dist)
        min_dist = dist(nearest)
        print(
            f"[DEBUG] Nearest {loc_type_str} to ({position.latitude}, {position.longitude}) is '{getattr(nearest, 'name', None)}' at ({nearest.position.latitude}, {nearest.position.longitude}) with distance {min_dist:.4f} degrees (~{min_dist*111:.2f} km)"
        )
        return nearest

    def _generate_bar_positions(self, person, family, day_in_year, day_in_week):
        # Students aged 18+ go to nearest bar after school (assume after 16:00)
        # If you want to use social_category for bar logic, use family.social_category
        if person.is_student and person.is_adult:
            if day_in_week < 5:  # Mon-Fri
                bar = self._find_nearest_location(
                    person.school_location.position, "BAR"
                )
                if bar:
                    self.positions.append(
                        Position(
                            person_id=person.person_id,
                            day_in_year=day_in_year,
                            day_in_week=day_in_week,
                            time_slot=17,
                            location=bar.position,
                        )
                    )

    def _generate_religious_positions(self, person, family, day_in_year, day_in_week):
        import random

        religiosity = getattr(family, "religiosity", None)
        church = self._find_nearest_location(family.home_position, "CHURCH")
        if religiosity:
            if religiosity.name == "VERY_RELIGIOUS":
                # Weekdays + Saturday at 19:00
                if day_in_week < 6:
                    if church:
                        self.positions.append(
                            Position(
                                person_id=person.person_id,
                                day_in_year=day_in_year,
                                day_in_week=day_in_week,
                                time_slot=19,
                                location=church.position,
                            )
                        )
                # Sunday at 11:00
                if day_in_week == 6:
                    if church:
                        self.positions.append(
                            Position(
                                person_id=person.person_id,
                                day_in_year=day_in_year,
                                day_in_week=day_in_week,
                                time_slot=11,
                                location=church.position,
                            )
                        )
            elif religiosity.name == "MODERATE_RELIGIOUS":
                # Every Sunday at 11:00
                if day_in_week == 6 and church:
                    self.positions.append(
                        Position(
                            person_id=person.person_id,
                            day_in_year=day_in_year,
                            day_in_week=day_in_week,
                            time_slot=11,
                            location=church.position,
                        )
                    )
            elif religiosity.name == "OCCASIONAL_RELIGIOUS":
                # One Sunday out of 6
                if day_in_week == 6 and church:
                    if random.randint(1, 6) == 1:
                        self.positions.append(
                            Position(
                                person_id=person.person_id,
                                day_in_year=day_in_year,
                                day_in_week=day_in_week,
                                time_slot=11,
                                location=church.position,
                            )
                        )

    def _determine_location(self, person: Person, day_in_week: int, time_slot: int):
        # Always return a Position object; fallback to home if needed
        pos = None
        # Night hours: 0-6, always at home
        if 0 <= time_slot <= 6:
            if person.family and person.family.home_position:
                pos = person.family.home_position
        # School hours: 8-16, Mon-Fri, children
        elif (
            person.is_child
            and person.school_location
            and day_in_week < 5
            and 8 <= time_slot <= 16
        ):
            if getattr(person.school_location, "position", None):
                pos = person.school_location.position
        # Work hours: 8-17, Mon-Fri, adults
        elif (
            person.is_adult
            and person.work_location
            and day_in_week < 5
            and 8 <= time_slot <= 17
        ):
            if getattr(person.work_location, "position", None):
                pos = person.work_location.position
        # Otherwise, home
        elif person.family and person.family.home_position:
            pos = person.family.home_position
        # Fallback: always use home position if nothing else
        if pos is None and person.family and person.family.home_position:
            pos = person.family.home_position
        return pos

    def save_positions(self, path: str):
        # Save positions to GeoParquet using geopandas
        records = []
        for position in self.positions:
            if position.location:
                geometry = Point(position.location.longitude, position.location.latitude)
            else:
                geometry = None
            records.append(
                {
                    "person_id": position.person_id,
                    "day_in_year": position.day_in_year,
                    "day_in_week": position.day_in_week,
                    "time_slot": position.time_slot,
                    "geometry": geometry,
                }
            )
        gdf = gpd.GeoDataFrame(records, geometry="geometry", crs="EPSG:4326")
        gdf.to_parquet(path, engine="pyarrow")
