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
from models.location import LocationType
from models.event import Event

# Set up logger
logger = logging.getLogger("event_generator")
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


class EventGenerator:
    """
    Generates daily activity events for each member of a family over one year.
    """

    def __init__(self, families: List[Family], location_repository=None):
        self.families = families
        self.events: list[Event] = []
        self.location_repository = location_repository

    def generate_events(self):
        start_date = datetime(datetime.now().year, 1, 6)  # Jan 6, 2025 is a Monday
        for day_offset in range(31):
            date = start_date + timedelta(days=day_offset)
            day_in_year = date.timetuple().tm_yday
            day_in_week = date.weekday()  # 0=Monday
            for family in self.families:
                for person in family.parents + family.children:
                    self._generate_base_events(person, day_in_year, day_in_week)
                    self._generate_bar_events(person, family, day_in_year, day_in_week)
                    self._generate_religious_events(
                        person, family, day_in_year, day_in_week
                    )
                    self._generate_show_events(person, family, day_in_year, day_in_week)

    def _generate_base_events(self, person, day_in_year, day_in_week):
        for time_slot in range(24):
            location = self._determine_location(person, day_in_week, time_slot)
            event = Event(
                person_id=person.person_id,
                day_in_year=day_in_year,
                day_in_week=day_in_week,
                time_slot=time_slot,
                location=location,
            )
            self.events.append(event)

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

    def _generate_bar_events(self, person, family, day_in_year, day_in_week):
        # Students aged 18+ go to nearest bar after school (assume after 16:00)
        # If you want to use social_category for bar logic, use family.social_category
        if person.is_student and person.is_adult:
            if day_in_week < 5:  # Mon-Fri
                bar = self._find_nearest_location(
                    person.school_location.position, "BAR"
                )
                if bar:
                    self.events.append(
                        Event(
                            person_id=person.person_id,
                            day_in_year=day_in_year,
                            day_in_week=day_in_week,
                            time_slot=17,
                            location=bar.position,
                        )
                    )

    def _generate_religious_events(self, person, family, day_in_year, day_in_week):
        import random

        religiosity = getattr(family, "religiosity", None)
        church = self._find_nearest_location(family.home_position, "CHURCH")
        if religiosity:
            if religiosity.name == "VERY_RELIGIOUS":
                # Weekdays + Saturday at 19:00
                if day_in_week < 6:
                    if church:
                        self.events.append(
                            Event(
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
                        self.events.append(
                            Event(
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
                    self.events.append(
                        Event(
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
                        self.events.append(
                            Event(
                                person_id=person.person_id,
                                day_in_year=day_in_year,
                                day_in_week=day_in_week,
                                time_slot=11,
                                location=church.position,
                            )
                        )

    def _generate_show_events(self, person, family, day_in_year, day_in_week):
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

    def save_events(self, path: str):
        # Save events to GeoParquet using geopandas
        records = []
        geometries = []
        for event in self.events:
            if event.location:
                geometry = Point(event.location.longitude, event.location.latitude)
            else:
                geometry = None
            record = {
                "person_id": event.person_id,
                "day_in_year": event.day_in_year,
                "day_in_week": event.day_in_week,
                "time_slot": event.time_slot,
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
            from models.location import Position

            family.home_position = Position(
                latitude=pos["latitude"], longitude=pos["longitude"]
            )
        # Parents and children are not reconstructed in detail (not needed for event gen)
        family.parents = []
        family.children = []
        families.append(family)
    return families


# --- Script entry point ---
if __name__ == "__main__":
    # Paths
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    family_file = os.path.join(base_dir, "data/families.json")
    event_file = os.path.join(base_dir, "data/events.parquet")
    data_dir = os.path.join(base_dir, "data")
    geojson_files = [
        "toulouse_churches.geojson",
        "toulouse_educational_institutions.geojson",
        "toulouse_entertainment_venues.geojson",
        "toulouse_hospitality_venues.geojson",
        "toulouse_work_places.geojson",
    ]
    # Load families
    logger.info(f"Loading families from {family_file} ...")
    families = load_families(family_file)
    logger.info(f"Loaded {len(families)} families.")
    # Load locations
    location_repo = LocationRepository()
    for fname in geojson_files:
        path = os.path.join(data_dir, fname)
        if os.path.exists(path):
            location_repo.add_locations_from_geojson(path)
        else:
            logger.warning(f"{path} not found.")
    # Debug: print number of locations loaded for each type
    logger.debug("Locations loaded by type:")
    for loc_type in LocationType:
        count = len(location_repo.get_locations_by_type(loc_type))
    logger.debug(f"  {loc_type.name}: {count}")
    # Generate and save events
    generator = EventGenerator(families, location_repository=location_repo)
    logger.info("Generating events...")
    generator.generate_events()
    logger.info(f"Saving events to {event_file} ...")
    generator.save_events(event_file)

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

    def save_events(self, path: str):
        # Save events to GeoParquet using geopandas
        records = []
        for event in self.events:
            if event.location:
                geometry = Point(event.location.longitude, event.location.latitude)
            else:
                geometry = None
            records.append(
                {
                    "person_id": event.person_id,
                    "day_in_year": event.day_in_year,
                    "day_in_week": event.day_in_week,
                    "time_slot": event.time_slot,
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
    geojson_files = [
        "toulouse_churches.geojson",
        "toulouse_educational_institutions.geojson",
        "toulouse_entertainment_venues.geojson",
        "toulouse_hospitality_venues.geojson",
        "toulouse_work_places.geojson",
    ]
    location_repo = LocationRepository()

    for fname in geojson_files:
        path = os.path.join(data_dir, fname)
        if os.path.exists(path):
            location_repo.add_locations_from_geojson(path)
        else:
            logger.warning(f"{path} not found.")

    # Debug: print number of locations loaded for each type
    logger.debug("Locations loaded by type:")
    from models.location import LocationType

    for loc_type in LocationType:
        count = len(location_repo.get_locations_by_type(loc_type))
    logger.debug(f"  {loc_type.name}: {count}")

    # Generate and save events
    event_generator = EventGenerator(families, location_repository=location_repo)
    logger.info("Generating events...")
    event_generator.generate_events()
    output_path = "data/events.parquet"
    logger.info(f"Saving events to {output_path} ...")
    event_generator.save_events(output_path)
    logger.info(f"✓ Events saved to {output_path}")

    """
    Generates daily activity events for each member of a family over one year.
    """

    def __init__(self, families: List[Family], location_repository=None):
        self.families = families
        self.location_repository = location_repository

    def generate_events(self):
        start_date = datetime(datetime.now().year, 1, 6)  # Jan 6, 2025 is a Monday
        for day_offset in range(31):
            date = start_date + timedelta(days=day_offset)
            day_in_year = date.timetuple().tm_yday
            day_in_week = date.weekday()  # 0=Monday
            for family in self.families:
                for person in family.parents + family.children:
                    self._generate_base_events(person, day_in_year, day_in_week)
                    self._generate_bar_events(person, family, day_in_year, day_in_week)
                    self._generate_religious_events(
                        person, family, day_in_year, day_in_week
                    )
                    self._generate_show_events(person, family, day_in_year, day_in_week)

    def _generate_base_events(self, person, day_in_year, day_in_week):
        for time_slot in range(24):
            location = self._determine_location(person, day_in_week, time_slot)
            event = Event(
                person_id=person.person_id,
                day_in_year=day_in_year,
                day_in_week=day_in_week,
                time_slot=time_slot,
                location=location,
            )
            self.events.append(event)

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

    def _generate_bar_events(self, person, family, day_in_year, day_in_week):
        # Students aged 18+ go to nearest bar after school (assume after 16:00)
        # If you want to use social_category for bar logic, use family.social_category
        if person.is_student and person.is_adult:
            if day_in_week < 5:  # Mon-Fri
                bar = self._find_nearest_location(
                    person.school_location.position, "BAR"
                )
                if bar:
                    self.events.append(
                        Event(
                            person_id=person.person_id,
                            day_in_year=day_in_year,
                            day_in_week=day_in_week,
                            time_slot=17,
                            location=bar.position,
                        )
                    )

    def _generate_religious_events(self, person, family, day_in_year, day_in_week):
        import random

        religiosity = getattr(family, "religiosity", None)
        church = self._find_nearest_location(family.home_position, "CHURCH")
        if religiosity:
            if religiosity.name == "VERY_RELIGIOUS":
                # Weekdays + Saturday at 19:00
                if day_in_week < 6:
                    if church:
                        self.events.append(
                            Event(
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
                        self.events.append(
                            Event(
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
                    self.events.append(
                        Event(
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
                        self.events.append(
                            Event(
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

    def save_events(self, path: str):
        # Save events to GeoParquet using geopandas
        records = []
        for event in self.events:
            if event.location:
                geometry = Point(event.location.longitude, event.location.latitude)
            else:
                geometry = None
            records.append(
                {
                    "person_id": event.person_id,
                    "day_in_year": event.day_in_year,
                    "day_in_week": event.day_in_week,
                    "time_slot": event.time_slot,
                    "geometry": geometry,
                }
            )
        gdf = gpd.GeoDataFrame(records, geometry="geometry", crs="EPSG:4326")
        gdf.to_parquet(path, engine="pyarrow")
