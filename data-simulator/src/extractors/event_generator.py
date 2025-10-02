import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime, timedelta
from typing import List
from models.event import Event
from models.family import Family
from models.person import Person
from models.location import LocationType


class EventGenerator:
    """
    Generates daily activity events for each member of a family over one year.
    """

    def __init__(self, families: List[Family], location_repository=None):
        self.families = families
        self.events: List[Event] = []
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
        # (stray code removed)

    def _generate_bar_events(self, person, family, day_in_year, day_in_week):
        # Students aged 18+ go to nearest bar after school (assume after 16:00)
        # If you want to use social_category for bar logic, use family.social_category
        if person.is_student() and person.is_adult():
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
